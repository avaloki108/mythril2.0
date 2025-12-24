"""
Mythril2 Analysis Module

Enhanced with DeFi analysis and ML integration capabilities.
"""

# Core analysis modules
from . import analysis_args
from . import call_helpers
from . import callgraph
from . import issue_annotation
from . import ops
from . import potential_issues
from . import report
from . import security
from . import solver
from . import swc_data
from . import symbolic
from . import traceexplore

# Enhanced analysis modules
try:
    from . import defi
    from . import ml
except ImportError:
    # Optional modules may not be available in all installations
    pass

__all__ = [
    'analysis_args',
    'call_helpers', 
    'callgraph',
    'issue_annotation',
    'ops',
    'potential_issues',
    'report',
    'security',
    'solver',
    'swc_data',
    'symbolic',
    'traceexplore',
    'defi',
    'ml'
]
