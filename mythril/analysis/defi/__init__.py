"""
DeFi Analysis Module

Provides comprehensive analysis capabilities for DeFi protocols including:
- Economic attack modeling and flash loan analysis
- Oracle manipulation detection
- Liquidity pool analysis and rug pull detection
- Governance attack vector detection
"""

from .economic_modeling import (
    EconomicAttackModeler,
    FlashLoanAnalyzer
)
from .oracle_analysis import (
    OracleManipulationDetector,
    PriceFeedAnalyzer
)
from .liquidity_analysis import (
    LiquidityPoolAnalyzer,
    RugPullDetector
)
from .governance_analysis import (
    GovernanceAttackDetector
)

__all__ = [
    'EconomicAttackModeler',
    'FlashLoanAnalyzer',
    'OracleManipulationDetector',
    'PriceFeedAnalyzer',
    'LiquidityPoolAnalyzer',
    'RugPullDetector',
    'GovernanceAttackDetector'
]