"""
ML-based pattern learning from known exploits to detect novel attack vectors
"""

import json
import pickle
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib

from mythril.analysis.issue_annotation import IssueAnnotation
from mythril.laser.ethereum.state.global_state import GlobalState
from .feature_extraction import FeatureExtractor, CodeFeatures


@dataclass
class ExploitPattern:
    """Represents a learned pattern from known exploits"""
    pattern_id: str
    attack_type: str
    features: np.ndarray
    confidence: float
    description: str
    cve_references: List[str]
    exploit_examples: List[str]
    

class ExploitDatabase:
    """Database of known exploits and their patterns"""
    
    def __init__(self, db_path: str = "exploits.json"):
        self.db_path = Path(db_path)
        self.exploits: Dict[str, Dict] = {}
        self.load_database()
        
    def load_database(self):
        """Load exploit database from file"""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                self.exploits = json.load(f)
        else:
            # Initialize with known DeFi exploits
            self.exploits = {
                "reentrancy": {
                    "patterns": [
                        "external_call_before_state_change",
                        "recursive_call_detection",
                        "state_modification_after_external_call"
                    ],
                    "examples": ["DAO_hack", "Cream_Finance", "Grim_Finance"],
                    "severity": "critical"
                },
                "flash_loan_attack": {
                    "patterns": [
                        "flash_loan_arbitrage",
                        "price_manipulation",
                        "oracle_manipulation"
                    ],
                    "examples": ["bZx_attack", "Harvest_Finance", "Alpha_Finance"],
                    "severity": "high"
                },
                "governance_attack": {
                    "patterns": [
                        "voting_power_concentration",
                        "proposal_spam",
                        "time_lock_bypass"
                    ],
                    "examples": ["Compound_governance", "Maker_governance"],
                    "severity": "medium"
                }
            }
            self.save_database()
    
    def save_database(self):
        """Save exploit database to file"""
        with open(self.db_path, 'w') as f:
            json.dump(self.exploits, f, indent=2)
    
    def add_exploit(self, exploit_id: str, patterns: List[str], 
                   examples: List[str], severity: str):
        """Add new exploit pattern to database"""
        self.exploits[exploit_id] = {
            "patterns": patterns,
            "examples": examples,
            "severity": severity
        }
        self.save_database()
    
    def get_patterns_by_type(self, attack_type: str) -> List[str]:
        """Get patterns for specific attack type"""
        return self.exploits.get(attack_type, {}).get("patterns", [])


class PatternLearner:
    """ML-based pattern learning system for detecting novel attack vectors"""
    
    def __init__(self, model_path: str = "pattern_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        self.feature_extractor = FeatureExtractor()
        self.exploit_db = ExploitDatabase()
        
        # ML Models
        self.anomaly_detector = IsolationForest(
            contamination=0.1, 
            random_state=42,
            n_estimators=100
        )
        self.pattern_classifier = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight='balanced'
        )
        self.clustering_model = DBSCAN(eps=0.3, min_samples=5)
        self.scaler = StandardScaler()
        
        # Pattern storage
        self.learned_patterns: List[ExploitPattern] = []
        self.pattern_embeddings: Optional[np.ndarray] = None
        
        self.load_models()
    
    def extract_code_patterns(self, global_state: GlobalState) -> CodeFeatures:
        """Extract patterns from code execution state"""
        return self.feature_extractor.extract_features(global_state)
    
    def learn_from_exploit(self, exploit_code: str, attack_type: str, 
                          cve_ref: str = "") -> ExploitPattern:
        """Learn patterns from a known exploit"""
        # This would typically involve analyzing the exploit code
        # For now, we'll create a simplified pattern
        features = self.feature_extractor.extract_from_code(exploit_code)
        
        pattern = ExploitPattern(
            pattern_id=f"{attack_type}_{len(self.learned_patterns)}",
            attack_type=attack_type,
            features=features.to_vector(),
            confidence=0.9,
            description=f"Pattern learned from {attack_type} exploit",
            cve_references=[cve_ref] if cve_ref else [],
            exploit_examples=[exploit_code[:100]]  # Store snippet
        )
        
        self.learned_patterns.append(pattern)
        self._update_pattern_embeddings()
        
        return pattern
    
    def detect_novel_patterns(self, code_features: CodeFeatures) -> List[Tuple[str, float]]:
        """Detect novel attack patterns using learned models"""
        feature_vector = code_features.to_vector().reshape(1, -1)
        scaled_features = self.scaler.transform(feature_vector)
        
        results = []
        
        # Anomaly detection
        anomaly_score = self.anomaly_detector.decision_function(scaled_features)[0]
        if anomaly_score < -0.5:  # Threshold for anomaly
            results.append(("novel_anomaly", abs(anomaly_score)))
        
        # Pattern similarity matching
        if self.pattern_embeddings is not None:
            similarities = cosine_similarity(feature_vector, self.pattern_embeddings)[0]
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[max_similarity_idx]
            
            if max_similarity > 0.8:  # High similarity threshold
                pattern = self.learned_patterns[max_similarity_idx]
                results.append((f"similar_to_{pattern.attack_type}", max_similarity))
        
        # Classification prediction
        if hasattr(self.pattern_classifier, 'predict_proba'):
            try:
                probabilities = self.pattern_classifier.predict_proba(scaled_features)[0]
                classes = self.pattern_classifier.classes_
                
                for i, prob in enumerate(probabilities):
                    if prob > 0.7:  # High confidence threshold
                        results.append((f"classified_as_{classes[i]}", prob))
            except:
                pass  # Model not trained yet
        
        return results
    
    def train_models(self, training_data: List[Tuple[CodeFeatures, str]]):
        """Train ML models on collected data"""
        if not training_data:
            return
        
        features = np.array([data[0].to_vector() for data, _ in training_data])
        labels = [label for _, label in training_data]
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train anomaly detector
        self.anomaly_detector.fit(features_scaled)
        
        # Train classifier if we have labels
        if len(set(labels)) > 1:
            self.pattern_classifier.fit(features_scaled, labels)
        
        # Perform clustering
        cluster_labels = self.clustering_model.fit_predict(features_scaled)
        
        # Save models
        self.save_models()
    
    def _update_pattern_embeddings(self):
        """Update pattern embeddings matrix"""
        if self.learned_patterns:
            self.pattern_embeddings = np.array([
                pattern.features for pattern in self.learned_patterns
            ])
    
    def save_models(self):
        """Save trained models to disk"""
        joblib.dump(self.anomaly_detector, self.model_path / "anomaly_detector.pkl")
        joblib.dump(self.pattern_classifier, self.model_path / "pattern_classifier.pkl")
        joblib.dump(self.scaler, self.model_path / "scaler.pkl")
        
        # Save learned patterns
        with open(self.model_path / "learned_patterns.pkl", 'wb') as f:
            pickle.dump(self.learned_patterns, f)
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            if (self.model_path / "anomaly_detector.pkl").exists():
                self.anomaly_detector = joblib.load(self.model_path / "anomaly_detector.pkl")
            
            if (self.model_path / "pattern_classifier.pkl").exists():
                self.pattern_classifier = joblib.load(self.model_path / "pattern_classifier.pkl")
            
            if (self.model_path / "scaler.pkl").exists():
                self.scaler = joblib.load(self.model_path / "scaler.pkl")
            
            if (self.model_path / "learned_patterns.pkl").exists():
                with open(self.model_path / "learned_patterns.pkl", 'rb') as f:
                    self.learned_patterns = pickle.load(f)
                self._update_pattern_embeddings()
        
        except Exception as e:
            print(f"Warning: Could not load some models: {e}")
    
    def analyze_contract(self, global_state: GlobalState) -> List[IssueAnnotation]:
        """Analyze contract for novel attack patterns"""
        issues = []
        
        # Extract features from current state
        features = self.extract_code_patterns(global_state)
        
        # Detect patterns
        detected_patterns = self.detect_novel_patterns(features)
        
        for pattern_type, confidence in detected_patterns:
            if confidence > 0.7:  # High confidence threshold
                issue = IssueAnnotation(
                    detector="pattern_learner",
                    title=f"Novel Attack Pattern Detected: {pattern_type}",
                    description=f"ML model detected potential {pattern_type} with confidence {confidence:.2f}",
                    swc_id="999",  # Custom SWC for ML detections
                    severity="Medium" if confidence < 0.9 else "High",
                    gas_used=global_state.mstate.min_gas_used,
                    address=global_state.get_current_instruction()["address"]
                )
                issues.append(issue)
        
        return issues