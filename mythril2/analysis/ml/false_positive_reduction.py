"""
False positive reduction system using ML models trained on validated results
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import joblib
import json
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

from mythril2.analysis.issue_annotation import IssueAnnotation
from .feature_extraction import FeatureExtractor, CodeFeatures


@dataclass
class ValidationResult:
    """Result of manual validation for training data"""
    issue_id: str
    detector_name: str
    is_true_positive: bool
    confidence_score: float
    validation_notes: str
    validator_id: str
    validation_timestamp: str


class ValidationDatabase:
    """Database for storing validation results"""
    
    def __init__(self, db_path: str = "validation_results.json"):
        self.db_path = Path(db_path)
        self.validations: List[ValidationResult] = []
        self.load_database()
    
    def load_database(self):
        """Load validation database from file"""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                self.validations = [
                    ValidationResult(**item) for item in data
                ]
    
    def save_database(self):
        """Save validation database to file"""
        data = [{
            'issue_id': v.issue_id,
            'detector_name': v.detector_name,
            'is_true_positive': v.is_true_positive,
            'confidence_score': v.confidence_score,
            'validation_notes': v.validation_notes,
            'validator_id': v.validator_id,
            'validation_timestamp': v.validation_timestamp
        } for v in self.validations]
        
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_validation(self, validation: ValidationResult):
        """Add new validation result"""
        self.validations.append(validation)
        self.save_database()
    
    def get_validations_by_detector(self, detector_name: str) -> List[ValidationResult]:
        """Get validations for specific detector"""
        return [v for v in self.validations if v.detector_name == detector_name]
    
    def get_training_data(self) -> Tuple[List[Dict], List[bool]]:
        """Get training data for ML models"""
        features = []
        labels = []
        
        for validation in self.validations:
            # Extract features from validation result
            feature_dict = {
                'detector_name': validation.detector_name,
                'confidence_score': validation.confidence_score,
                # Add more features as needed
            }
            features.append(feature_dict)
            labels.append(validation.is_true_positive)
        
        return features, labels


class FalsePositiveReducer:
    """ML-based false positive reduction system"""
    
    def __init__(self, model_path: str = "fp_reduction_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        self.validation_db = ValidationDatabase()
        self.feature_extractor = FeatureExtractor()
        
        # ML Models for different detectors
        self.detector_models: Dict[str, Any] = {}
        self.global_model = None
        self.scaler = StandardScaler()
        
        # Model configurations
        self.model_configs = {
            'random_forest': {
                'model': RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    class_weight='balanced'
                ),
                'calibrated': True
            },
            'gradient_boosting': {
                'model': GradientBoostingClassifier(
                    n_estimators=100,
                    random_state=42
                ),
                'calibrated': True
            },
            'logistic_regression': {
                'model': LogisticRegression(
                    random_state=42,
                    class_weight='balanced'
                ),
                'calibrated': False
            }
        }
        
        self.load_models()
    
    def extract_issue_features(self, issue: IssueAnnotation, 
                              code_features: CodeFeatures) -> np.ndarray:
        """Extract features from issue for false positive prediction"""
        features = []
        
        # Issue-specific features
        features.extend([
            len(issue.description),
            issue.gas_used if issue.gas_used else 0,
            1 if issue.severity == "High" else 0,
            1 if issue.severity == "Medium" else 0,
            1 if issue.severity == "Low" else 0,
        ])
        
        # Detector-specific features
        detector_features = self._get_detector_features(issue.detector)
        features.extend(detector_features)
        
        # Code context features
        code_vector = code_features.to_vector()
        features.extend(code_vector[:10])  # Use first 10 code features
        
        # Statistical features
        features.extend([
            self._get_detector_historical_accuracy(issue.detector),
            self._get_issue_type_frequency(issue.swc_id)
        ])
        
        return np.array(features, dtype=np.float32)
    
    def predict_false_positive_probability(self, issue: IssueAnnotation, 
                                         code_features: CodeFeatures) -> float:
        """Predict probability that an issue is a false positive"""
        features = self.extract_issue_features(issue, code_features)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Try detector-specific model first
        if issue.detector in self.detector_models:
            model = self.detector_models[issue.detector]
            if hasattr(model, 'predict_proba'):
                # Return probability of being false positive (class 0)
                proba = model.predict_proba(features_scaled)[0]
                return proba[0] if len(proba) > 1 else 0.5
        
        # Fall back to global model
        if self.global_model and hasattr(self.global_model, 'predict_proba'):
            proba = self.global_model.predict_proba(features_scaled)[0]
            return proba[0] if len(proba) > 1 else 0.5
        
        return 0.5  # Default uncertainty
    
    def filter_issues(self, issues: List[IssueAnnotation], 
                     code_features: CodeFeatures,
                     fp_threshold: float = 0.7) -> List[IssueAnnotation]:
        """Filter out likely false positives from issue list"""
        filtered_issues = []
        
        for issue in issues:
            fp_probability = self.predict_false_positive_probability(issue, code_features)
            
            if fp_probability < fp_threshold:
                # Add confidence score to issue
                issue.confidence = 1.0 - fp_probability
                filtered_issues.append(issue)
        
        return filtered_issues
    
    def train_models(self, retrain_all: bool = False):
        """Train false positive reduction models"""
        features, labels = self.validation_db.get_training_data()
        
        if len(features) < 10:  # Need minimum training data
            print("Insufficient training data for false positive reduction")
            return
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(features)
        
        # Group by detector for detector-specific models
        detector_groups = df.groupby('detector_name')
        
        for detector_name, group in detector_groups:
            if len(group) >= 5:  # Minimum samples per detector
                self._train_detector_model(detector_name, group, labels)
        
        # Train global model
        self._train_global_model(df, labels)
        
        # Save models
        self.save_models()
    
    def _train_detector_model(self, detector_name: str, features_df: pd.DataFrame, 
                            all_labels: List[bool]):
        """Train model for specific detector"""
        # Get labels for this detector
        detector_indices = features_df.index.tolist()
        detector_labels = [all_labels[i] for i in detector_indices]
        
        # Prepare features (excluding detector_name)
        X = features_df.drop('detector_name', axis=1).values
        y = np.array(detector_labels)
        
        if len(np.unique(y)) < 2:  # Need both classes
            return
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train best model
        best_model = None
        best_score = 0
        
        for model_name, config in self.model_configs.items():
            model = config['model']
            
            # Cross-validation
            scores = cross_val_score(model, X_scaled, y, cv=3, scoring='f1')
            avg_score = np.mean(scores)
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
        
        if best_model:
            # Train final model
            if self.model_configs[model_name]['calibrated']:
                best_model = CalibratedClassifierCV(best_model, cv=3)
            
            best_model.fit(X_scaled, y)
            self.detector_models[detector_name] = best_model
    
    def _train_global_model(self, features_df: pd.DataFrame, labels: List[bool]):
        """Train global false positive reduction model"""
        # One-hot encode detector names
        detector_encoded = pd.get_dummies(features_df['detector_name'], prefix='detector')
        X = pd.concat([features_df.drop('detector_name', axis=1), detector_encoded], axis=1)
        y = np.array(labels)
        
        if len(np.unique(y)) < 2:
            return
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X.values)
        
        # Train ensemble model
        self.global_model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight='balanced'
        )
        
        self.global_model.fit(X_scaled, y)
    
    def _get_detector_features(self, detector_name: str) -> List[float]:
        """Get detector-specific features"""
        # Historical accuracy, frequency, etc.
        validations = self.validation_db.get_validations_by_detector(detector_name)
        
        if not validations:
            return [0.5, 0.0, 0.0]  # Default values
        
        accuracy = sum(1 for v in validations if v.is_true_positive) / len(validations)
        avg_confidence = sum(v.confidence_score for v in validations) / len(validations)
        total_detections = len(validations)
        
        return [accuracy, avg_confidence, total_detections]
    
    def _get_detector_historical_accuracy(self, detector_name: str) -> float:
        """Get historical accuracy for detector"""
        validations = self.validation_db.get_validations_by_detector(detector_name)
        
        if not validations:
            return 0.5
        
        return sum(1 for v in validations if v.is_true_positive) / len(validations)
    
    def _get_issue_type_frequency(self, swc_id: str) -> float:
        """Get frequency of issue type"""
        # This would analyze historical data for issue type frequency
        return 0.1  # Placeholder
    
    def save_models(self):
        """Save trained models to disk"""
        # Save detector-specific models
        for detector_name, model in self.detector_models.items():
            model_file = self.model_path / f"{detector_name}_fp_model.pkl"
            joblib.dump(model, model_file)
        
        # Save global model
        if self.global_model:
            joblib.dump(self.global_model, self.model_path / "global_fp_model.pkl")
        
        # Save scaler
        joblib.dump(self.scaler, self.model_path / "fp_scaler.pkl")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Load global model
            global_model_path = self.model_path / "global_fp_model.pkl"
            if global_model_path.exists():
                self.global_model = joblib.load(global_model_path)
            
            # Load scaler
            scaler_path = self.model_path / "fp_scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            
            # Load detector-specific models
            for model_file in self.model_path.glob("*_fp_model.pkl"):
                detector_name = model_file.stem.replace("_fp_model", "")
                self.detector_models[detector_name] = joblib.load(model_file)
        
        except Exception as e:
            print(f"Warning: Could not load some FP reduction models: {e}")


class ValidationModel:
    """Model for validating and improving detection accuracy"""
    
    def __init__(self, validation_db: ValidationDatabase):
        self.validation_db = validation_db
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        validations = self.validation_db.validations
        
        if not validations:
            return {"error": "No validation data available"}
        
        # Overall statistics
        total_validations = len(validations)
        true_positives = sum(1 for v in validations if v.is_true_positive)
        false_positives = total_validations - true_positives
        
        overall_accuracy = true_positives / total_validations
        
        # Per-detector statistics
        detector_stats = {}
        detectors = set(v.detector_name for v in validations)
        
        for detector in detectors:
            detector_validations = [v for v in validations if v.detector_name == detector]
            detector_tp = sum(1 for v in detector_validations if v.is_true_positive)
            detector_total = len(detector_validations)
            
            detector_stats[detector] = {
                'total_detections': detector_total,
                'true_positives': detector_tp,
                'false_positives': detector_total - detector_tp,
                'accuracy': detector_tp / detector_total,
                'avg_confidence': sum(v.confidence_score for v in detector_validations) / detector_total
            }
        
        return {
            'overall': {
                'total_validations': total_validations,
                'true_positives': true_positives,
                'false_positives': false_positives,
                'accuracy': overall_accuracy
            },
            'by_detector': detector_stats,
            'recommendations': self._generate_recommendations(detector_stats)
        }
    
    def _generate_recommendations(self, detector_stats: Dict) -> List[str]:
        """Generate recommendations for improving detection"""
        recommendations = []
        
        for detector, stats in detector_stats.items():
            if stats['accuracy'] < 0.7:
                recommendations.append(
                    f"Consider tuning {detector} detector - accuracy is {stats['accuracy']:.2f}"
                )
            
            if stats['false_positives'] > stats['true_positives']:
                recommendations.append(
                    f"{detector} has high false positive rate - consider stricter thresholds"
                )
        
        return recommendations
