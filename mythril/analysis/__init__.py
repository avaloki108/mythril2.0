"""
Mythril Analysis Module

This package provides the core analysis capabilities for Mythril, including:
- Traditional security analysis modules
- DeFi-specific analysis capabilities
- Machine learning-powered analysis features
- Issue detection and reporting
"""

# Core analysis modules
from . import issue_annotation
from . import report
from . import security
from . import solver
from . import traceexplore

__all__ = [
    'issue_annotation',
    'report', 
    'security',
    'solver',
    'traceexplore',
]

# New DeFi analysis modules - lazy import to avoid circular dependencies
def get_defi():
    try:
        from . import defi
        return defi
    except ImportError:
        # DeFi modules require additional dependencies
        return None

# New ML analysis modules - lazy import to avoid circular dependencies
def get_ml():
    try:
        from . import ml
        return ml
    except ImportError:
        # ML modules require additional dependencies like scikit-learn
        return None

# Add to __all__ for documentation purposes
__all__.extend(['defi', 'ml'])