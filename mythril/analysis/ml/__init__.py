"""
Machine Learning Analysis Module

Provides ML-powered analysis capabilities for smart contract security including:
- False positive reduction using trained models
- Pattern learning from known vulnerabilities
- Feature extraction for ML models
- Model training and evaluation utilities
"""

from .false_positive_reduction import FalsePositiveReducer
from .pattern_learning import PatternLearner
from .feature_extraction import FeatureExtractor
from .model_training import ModelTrainer

__all__ = [
    'FalsePositiveReducer',
    'PatternLearner', 
    'FeatureExtractor',
    'ModelTrainer'
]