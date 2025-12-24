"""
Liquidity pool analysis for impermanent loss and rug pull pattern detection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math

# Note: IssueAnnotation import commented out to avoid circular dependencies
# from mythril.analysis.issue_annotation import IssueAnnotation
# from mythril.laser.ethereum.state.global_state import GlobalState


class PoolType(Enum):
    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    SUSHISWAP = "sushiswap"
    BALANCER = "balancer"
    CURVE = "curve"
    CUSTOM_AMM = "custom_amm"


class RiskType(Enum):
    RUG_PULL = "rug_pull"
    IMPERMANENT_LOSS = "impermanent_loss"
    LIQUIDITY_DRAIN = "liquidity_drain"
    SANDWICH_ATTACK = "sandwich_attack"
    FRONT_RUNNING = "front_running"
    SLIPPAGE_MANIPULATION = "slippage_manipulation"


@dataclass
class LiquidityPool:
    """Represents a liquidity pool configuration"""
    pool_type: PoolType
    token_a: str
    token_b: str
    reserve_a: float
    reserve_b: float
    total_supply: float
    fee_rate: float


@dataclass
class LiquidityRisk:
    """Represents a detected liquidity risk"""
    risk_type: RiskType
    severity: str
    description: str
    confidence: float
    affected_functions: List[str]


class LiquidityPoolAnalyzer:
    """Analyzes liquidity pools for security risks"""
    
    def __init__(self):
        self.pool_patterns = {
            PoolType.UNISWAP_V2: {
                'indicators': ['UniswapV2Pair', 'getReserves', 'sync'],
                'vulnerabilities': ['rug_pull', 'impermanent_loss']
            },
            PoolType.UNISWAP_V3: {
                'indicators': ['UniswapV3Pool', 'position', 'tick'],
                'vulnerabilities': ['impermanent_loss', 'concentrated_liquidity_risk']
            },
            PoolType.CURVE: {
                'indicators': ['CurvePool', 'coins', 'balances'],
                'vulnerabilities': ['peg_risk', 'liquidity_drain']
            }
        }
        
        self.risk_patterns = {
            RiskType.RUG_PULL: {
                'indicators': ['onlyOwner', 'withdraw', 'drain', 'emergency'],
                'severity': 'Critical'
            },
            RiskType.IMPERMANENT_LOSS: {
                'indicators': ['swap', 'price', 'ratio'],
                'severity': 'Medium'
            },
            RiskType.LIQUIDITY_DRAIN: {
                'indicators': ['drain', 'withdraw', 'skim'],
                'severity': 'High'
            }
        }
    
    def analyze_liquidity_security(self, contract_code: str) -> List[Dict[str, Any]]:
        """Analyze liquidity security vulnerabilities in contract code"""
        risks = []
        
        # Detect pool type
        pool_type = self._detect_pool_type(contract_code)
        
        if pool_type:
            # Check for rug pull vulnerabilities
            rug_pull_risks = self._check_rug_pull_vulnerabilities(contract_code, pool_type)
            risks.extend(rug_pull_risks)
            
            # Check for liquidity drain vulnerabilities
            drain_risks = self._check_liquidity_drain(contract_code, pool_type)
            risks.extend(drain_risks)
            
            # Check for slippage manipulation
            slippage_risks = self._check_slippage_manipulation(contract_code, pool_type)
            risks.extend(slippage_risks)
            
            # Check for sandwich attack vulnerabilities
            sandwich_risks = self._check_sandwich_attacks(contract_code, pool_type)
            risks.extend(sandwich_risks)
        
        return risks
    
    def _detect_pool_type(self, contract_code: str) -> Optional[PoolType]:
        """Detect the type of liquidity pool from contract code"""
        
        if 'UniswapV2Pair' in contract_code or 'getReserves' in contract_code:
            return PoolType.UNISWAP_V2
        elif 'UniswapV3Pool' in contract_code or 'position' in contract_code:
            return PoolType.UNISWAP_V3
        elif 'CurvePool' in contract_code or 'coins' in contract_code:
            return PoolType.CURVE
        elif 'BalancerPool' in contract_code or 'getVault' in contract_code:
            return PoolType.BALANCER
        elif 'swap' in contract_code.lower() and 'liquidity' in contract_code.lower():
            return PoolType.CUSTOM_AMM
        
        return None
    
    def _check_rug_pull_vulnerabilities(self, contract_code: str,
                                      pool_type: PoolType) -> List[Dict[str, Any]]:
        """Check for rug pull vulnerabilities"""
        risks = []
        
        # Look for owner-only functions that can drain liquidity
        dangerous_functions = [
            'withdraw',
            'drain',
            'emergencyWithdraw',
            'skim',
            'pullLiquidity'
        ]
        
        owner_modifiers = [
            'onlyOwner',
            'require(msg.sender == owner)',
            'require(msg.sender == _owner)'
        ]
        
        has_owner_functions = any(func in contract_code for func in dangerous_functions)
        has_owner_modifiers = any(mod in contract_code for mod in owner_modifiers)
        
        if has_owner_functions and has_owner_modifiers:
            # Check if these functions can drain all liquidity
            for func in dangerous_functions:
                if func in contract_code:
                    # Look for patterns that indicate full liquidity removal
                    func_content = self._extract_function_content(contract_code, func)
                    
                    if 'balanceOf' in func_content or 'totalSupply' in func_content:
                        risk = {
                            'detector': 'liquidity_pool_analyzer',
                            'title': 'Rug Pull Vulnerability Detected',
                            'description': f"Function '{func}' with owner privileges can potentially "
                                       "drain all liquidity from the pool. This is a classic rug pull pattern.",
                            'swc_id': '920',
                            'severity': 'Critical',
                            'affected_function': func
                        }
                        risks.append(risk)
        
        return risks
    
    def _check_liquidity_drain(self, contract_code: str,
                             pool_type: PoolType) -> List[Dict[str, Any]]:
        """Check for liquidity drain vulnerabilities"""
        risks = []
        
        # Look for functions that can manipulate reserves
        reserve_manipulation_patterns = [
            'sync',
            'update',
            'setReserve',
            'manipulate'
        ]
        
        for pattern in reserve_manipulation_patterns:
            if pattern in contract_code:
                risk = {
                    'detector': 'liquidity_pool_analyzer',
                    'title': 'Liquidity Drain Vulnerability',
                    'description': f"Contract contains '{pattern}' functionality that could "
                               "be exploited to manipulate pool reserves and drain liquidity.",
                    'swc_id': '921',
                    'severity': 'High',
                    'affected_function': pattern
                }
                risks.append(risk)
        
        return risks
    
    def _check_slippage_manipulation(self, contract_code: str,
                                   pool_type: PoolType) -> List[Dict[str, Any]]:
        """Check for slippage manipulation vulnerabilities"""
        risks = []
        
        # Look for swap functions without proper slippage protection
        swap_functions = ['swap', 'swapExactTokensForTokens', 'swapTokensForExactTokens']
        
        for func in swap_functions:
            if func in contract_code:
                func_content = self._extract_function_content(contract_code, func)
                
                # Check if there's slippage protection
                has_slippage_check = (
                    'amountOutMin' in func_content or
                    'amountInMax' in func_content or
                    'slippage' in func_content.lower()
                )
                
                if not has_slippage_check:
                    risk = {
                        'detector': 'liquidity_pool_analyzer',
                        'title': 'Slippage Manipulation Vulnerability',
                        'description': f"Swap function '{func}' lacks proper slippage protection, "
                                   "making it vulnerable to front-running and sandwich attacks.",
                        'swc_id': '922',
                        'severity': 'Medium',
                        'affected_function': func
                    }
                    risks.append(risk)
        
        return risks
    
    def _check_sandwich_attacks(self, contract_code: str,
                              pool_type: PoolType) -> List[Dict[str, Any]]:
        """Check for sandwich attack vulnerabilities"""
        risks = []
        
        # Look for MEV-related patterns
        mev_patterns = [
            'frontrun',
            'mev',
            'arbitrage'
        ]
        
        if any(pattern in contract_code.lower() for pattern in mev_patterns):
            risk = {
                'detector': 'liquidity_pool_analyzer',
                'title': 'Sandwich Attack Vulnerability',
                'description': "Contract contains patterns that could be exploited for "
                           "sandwich attacks, where attackers profit from slippage "
                           "by placing orders before and after victim transactions.",
                'swc_id': '923',
                'severity': 'Medium'
            }
            risks.append(risk)
        
        return risks
    
    def _extract_function_content(self, contract_code: str, function_name: str) -> str:
        """Extract the content of a specific function from contract code"""
        lines = contract_code.split('\n')
        in_function = False
        brace_count = 0
        function_content = []
        
        for line in lines:
            if function_name in line and 'function' in line:
                in_function = True
                function_content.append(line)
                continue
            
            if in_function:
                function_content.append(line)
                brace_count += line.count('{') - line.count('}')
                
                if brace_count <= 0 and '}' in line:
                    break
        
        return '\n'.join(function_content)


class RugPullDetector:
    """Specialized detector for rug pull patterns"""
    
    def __init__(self):
        self.rug_pull_patterns = {
            'honeypot': {
                'indicators': ['onlyOwner', 'transfer', 'lock'],
                'severity': 'Critical'
            },
            'liquidity_drain': {
                'indicators': ['removeLiquidity', 'withdraw', 'drain'],
                'severity': 'Critical'
            },
            'fee_manipulation': {
                'indicators': ['setFee', 'updateFee', 'fee'],
                'severity': 'High'
            }
        }
    
    def detect_rug_pull_patterns(self, contract_code: str) -> List[Dict[str, Any]]:
        """Detect rug pull patterns in contract code"""
        risks = []
        
        # Check for honeypot patterns
        honeypot_risks = self._check_honeypot_patterns(contract_code)
        risks.extend(honeypot_risks)
        
        # Check for liquidity manipulation
        liquidity_risks = self._check_liquidity_manipulation(contract_code)
        risks.extend(liquidity_risks)
        
        # Check for fee manipulation
        fee_risks = self._check_fee_manipulation(contract_code)
        risks.extend(fee_risks)
        
        return risks
    
    def _check_honeypot_patterns(self, contract_code: str) -> List[Dict[str, Any]]:
        """Check for honeypot patterns"""
        risks = []
        
        # Look for transfer restrictions
        transfer_restricted = (
            'onlyOwner' in contract_code and 'transfer' in contract_code
        )
        
        # Look for sell restrictions
        sell_restricted = (
            'sell' in contract_code.lower() and 
            ('onlyOwner' in contract_code or 'require' in contract_code)
        )
        
        if transfer_restricted or sell_restricted:
            risk = {
                'detector': 'rug_pull_detector',
                'title': 'Honeypot Pattern Detected',
                'description': "Contract contains transfer restrictions that prevent "
                           "normal users from selling tokens, indicating a potential honeypot.",
                'swc_id': '924',
                'severity': 'Critical'
            }
            risks.append(risk)
        
        return risks
    
    def _check_liquidity_manipulation(self, contract_code: str) -> List[Dict[str, Any]]:
        """Check for liquidity manipulation patterns"""
        risks = []
        
        # Look for functions that can remove liquidity unfairly
        unfair_removal_patterns = [
            'emergencyRemove',
            'ownerRemove',
            'forceRemove'
        ]
        
        for pattern in unfair_removal_patterns:
            if pattern in contract_code:
                risk = {
                    'detector': 'rug_pull_detector',
                    'title': 'Unfair Liquidity Removal',
                    'description': f"Contract contains '{pattern}' function that allows "
                               "unfair removal of liquidity, indicating potential rug pull risk.",
                    'swc_id': '925',
                    'severity': 'Critical'
                }
                risks.append(risk)
        
        return risks
    
    def _check_fee_manipulation(self, contract_code: str) -> List[Dict[str, Any]]:
        """Check for fee manipulation patterns"""
        risks = []
        
        # Look for modifiable fees
        fee_modification_patterns = [
            'setFee',
            'updateFee',
            'changeFee'
        ]
        
        for pattern in fee_modification_patterns:
            if pattern in contract_code:
                # Check if only owner can modify fees
                if 'onlyOwner' in contract_code:
                    risk = {
                        'detector': 'rug_pull_detector',
                        'title': 'Fee Manipulation Risk',
                        'description': f"Contract allows fee modification via '{pattern}' "
                                   "function, which could be abused to set excessive fees.",
                        'swc_id': '926',
                        'severity': 'High'
                    }
                    risks.append(risk)
        
        return risks
