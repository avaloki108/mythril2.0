"""
Model Training Module

Provides training infrastructure for ML models used in vulnerability detection
and false positive reduction.
"""

import logging
import pickle
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TrainingData:
    """Container for training data"""
    features: np.ndarray
    labels: np.ndarray
    feature_names: List[str]
    metadata: Dict[str, Any]
    
    def split(self, test_size: float = 0.2, random_state: int = 42) -> Tuple['TrainingData', 'TrainingData']:
        """Split data into training and testing sets"""
        X_train, X_test, y_train, y_test = train_test_split(
            self.features, self.labels, 
            test_size=test_size, 
            random_state=random_state,
            stratify=self.labels
        )
        
        train_data = TrainingData(
            features=X_train,
            labels=y_train,
            feature_names=self.feature_names,
            metadata={**self.metadata, 'split': 'train'}
        )
        
        test_data = TrainingData(
            features=X_test,
            labels=y_test,
            feature_names=self.feature_names,
            metadata={**self.metadata, 'split': 'test'}
        )
        
        return train_data, test_data

class ModelTrainer:
    """Trains and evaluates ML models for vulnerability detection"""
    
    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or Path("models")
        self.model_dir.mkdir(exist_ok=True)
        
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            ),
            'logistic_regression': LogisticRegression(
                random_state=42,
                max_iter=1000
            )
        }
        
        self.scaler = StandardScaler()
        self.trained_models = {}
        
    def prepare_data(self, training_data: TrainingData) -> TrainingData:
        """Prepare and scale training data"""
        logger.info(f"Preparing training data with {len(training_data.features)} samples")
        
        # Scale features
        scaled_features = self.scaler.fit_transform(training_data.features)
        
        return TrainingData(
            features=scaled_features,
            labels=training_data.labels,
            feature_names=training_data.feature_names,
            metadata={**training_data.metadata, 'scaled': True}
        )
    
    def train_model(self, model_name: str, training_data: TrainingData) -> Dict[str, Any]:
        """Train a specific model"""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        logger.info(f"Training {model_name} model")
        
        model = self.models[model_name]
        
        # Prepare data
        prepared_data = self.prepare_data(training_data)
        train_data, test_data = prepared_data.split()
        
        # Train model
        model.fit(train_data.features, train_data.labels)
        
        # Evaluate model
        train_score = model.score(train_data.features, train_data.labels)
        test_score = model.score(test_data.features, test_data.labels)
        
        # Cross-validation
        cv_scores = cross_val_score(model, prepared_data.features, prepared_data.labels, cv=5)
        
        # Predictions for detailed evaluation
        test_predictions = model.predict(test_data.features)
        
        # Store trained model
        self.trained_models[model_name] = {
            'model': model,
            'scaler': self.scaler,
            'feature_names': training_data.feature_names
        }
        
        results = {
            'model_name': model_name,
            'train_score': train_score,
            'test_score': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': classification_report(
                test_data.labels, test_predictions, output_dict=True
            ),
            'confusion_matrix': confusion_matrix(test_data.labels, test_predictions).tolist()
        }
        
        logger.info(f"Model {model_name} trained - Test Score: {test_score:.3f}")
        return results
    
    def train_all_models(self, training_data: TrainingData) -> Dict[str, Dict[str, Any]]:
        """Train all available models"""
        results = {}
        
        for model_name in self.models.keys():
            try:
                results[model_name] = self.train_model(model_name, training_data)
            except Exception as e:
                logger.error(f"Failed to train {model_name}: {e}")
                results[model_name] = {'error': str(e)}
        
        return results
    
    def save_model(self, model_name: str, filename: Optional[str] = None) -> Path:
        """Save a trained model to disk"""
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        filename = filename or f"{model_name}_model.pkl"
        filepath = self.model_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.trained_models[model_name], f)
        
        logger.info(f"Model {model_name} saved to {filepath}")
        return filepath
    
    def load_model(self, filepath: Path) -> str:
        """Load a trained model from disk"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model_name = filepath.stem.replace('_model', '')
        self.trained_models[model_name] = model_data
        
        logger.info(f"Model loaded from {filepath}")
        return model_name
    
    def predict(self, model_name: str, features: np.ndarray) -> np.ndarray:
        """Make predictions using a trained model"""
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model_data = self.trained_models[model_name]
        model = model_data['model']
        scaler = model_data['scaler']
        
        # Scale features
        scaled_features = scaler.transform(features)
        
        return model.predict(scaled_features)
    
    def predict_proba(self, model_name: str, features: np.ndarray) -> np.ndarray:
        """Get prediction probabilities"""
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model_data = self.trained_models[model_name]
        model = model_data['model']
        scaler = model_data['scaler']
        
        # Scale features
        scaled_features = scaler.transform(features)
        
        return model.predict_proba(scaled_features)
    
    def get_feature_importance(self, model_name: str) -> Dict[str, float]:
        """Get feature importance for tree-based models"""
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model_data = self.trained_models[model_name]
        model = model_data['model']
        feature_names = model_data['feature_names']
        
        if hasattr(model, 'feature_importances_'):
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            # Sort by importance
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        else:
            logger.warning(f"Model {model_name} does not support feature importance")
            return {}