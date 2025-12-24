"""
Economic attack modeling and flash loan analysis for DeFi protocols
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re

# Note: These imports are commented out to avoid circular dependencies
# When the laser module is refactored, these can be re-enabled
# from mythril2.analysis.issue_annotation import IssueAnnotation
# from mythril2.laser.ethereum.state.global_state import GlobalState
# from mythril2.laser.ethereum.state.machine_state import MachineState


class AttackType(Enum):
    FLASH_LOAN_ARBITRAGE = "flash_loan_arbitrage"
    SANDWICH_ATTACK = "sandwich_attack"
    MEV_EXTRACTION = "mev_extraction"
    LIQUIDITY_MANIPULATION = "liquidity_manipulation"
    ORACLE_MANIPULATION = "oracle_manipulation"
    GOVERNANCE_ATTACK = "governance_attack"


@dataclass
class EconomicModel:
    """Economic model for DeFi protocol analysis"""
    protocol_type: str
    token_reserves: Dict[str, float]
    liquidity_depth: float
    price_impact_threshold: float
    slippage_tolerance: float
    
    
@dataclass
class FlashLoanPattern:
    """Pattern detected in flash loan usage"""
    loan_amount: float
    loan_token: str
    operations: List[str]
    profit_potential: float
    risk_level: str
    attack_vector: Optional[AttackType]


class EconomicAttackModeler:
    """Models economic attacks and their profitability"""
    
    def __init__(self):
        self.attack_patterns = {
            AttackType.FLASH_LOAN_ARBITRAGE: {
                'indicators': ['flashloan', 'arbitrage', 'price_difference'],
                'min_profit_threshold': 0.01,  # 1% minimum profit
                'complexity_score': 0.7
            },
            AttackType.SANDWICH_ATTACK: {
                'indicators': ['frontrun', 'backrun', 'slippage'],
                'min_profit_threshold': 0.005,  # 0.5% minimum profit
                'complexity_score': 0.5
            },
            AttackType.MEV_EXTRACTION: {
                'indicators': ['mev', 'extraction', 'priority_fee'],
                'min_profit_threshold': 0.002,  # 0.2% minimum profit
                'complexity_score': 0.8
            }
        }
        
        self.defi_protocols = {
            'uniswap': {
                'type': 'amm',
                'fee_structure': 0.003,
                'liquidity_formula': 'constant_product'
            },
            'compound': {
                'type': 'lending',
                'interest_model': 'utilization_based',
                'collateral_factor': 0.75
            },
            'aave': {
                'type': 'lending',
                'flash_loan_fee': 0.0009,
                'health_factor_threshold': 1.0
            }
        }
    
    def analyze_economic_attack(self, contract_code: str) -> List[Dict[str, Any]]:
        """Analyze potential economic attacks in contract code
        
        Args:
            contract_code: The Solidity contract source code
            
        Returns:
            List of detected economic attack vulnerabilities
        """
        issues = []
        
        # Extract economic context from contract code
        economic_context = self._extract_economic_context_from_code(contract_code)
        
        # Check for flash loan patterns
        flash_loan_issues = self._analyze_flash_loan_patterns_in_code(contract_code, economic_context)
        issues.extend(flash_loan_issues)
        
        # Check for arbitrage opportunities
        arbitrage_issues = self._analyze_arbitrage_patterns_in_code(contract_code, economic_context)
        issues.extend(arbitrage_issues)
        
        # Check for MEV extraction
        mev_issues = self._analyze_mev_patterns_in_code(contract_code, economic_context)
        issues.extend(mev_issues)
        
        return issues
    
    def _extract_economic_context_from_code(self, contract_code: str) -> Dict[str, Any]:
        """Extract economic context from contract code"""
        context = {
            'token_balances': {},
            'price_feeds': {},
            'liquidity_pools': {},
            'flash_loan_providers': [],
            'governance_tokens': []
        }
        
        # Look for common DeFi patterns in the code
        if 'flashloan' in contract_code.lower() or 'flash loan' in contract_code.lower():
            context['flash_loan_providers'].append('detected')
            
        if 'uniswap' in contract_code.lower():
            context['liquidity_pools']['uniswap'] = 'detected'
            
        if 'compound' in contract_code.lower():
            context['lending_protocols'] = ['compound']
            
        if 'aave' in contract_code.lower():
            context['lending_protocols'] = ['aave']
        
        return context
    
    def _analyze_flash_loan_patterns_in_code(self, contract_code: str, 
                                           context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze flash loan attack patterns in contract code"""
        issues = []
        
        # Look for flash loan indicators in the code
        flash_loan_indicators = ['flashloan', 'flash loan', 'aave', 'dydx', 'uniswapV3FlashCallback']
        
        if any(indicator in contract_code.lower() for indicator in flash_loan_indicators):
            # Analyze the economic viability
            profit_analysis = self._calculate_flash_loan_profitability_from_code(contract_code, context)
            
            if profit_analysis['is_profitable']:
                issue = {
                    'detector': "economic_attack_modeler",
                    'title': "Potential Flash Loan Attack Vector",
                    'description': f"Flash loan pattern detected with potential profit of {profit_analysis['profit_estimate']:.2%}. "
                               f"Attack vector: {profit_analysis['attack_type']}",
                    'swc_id': "900",  # Custom SWC for economic attacks
                    'severity': "High" if profit_analysis['profit_estimate'] > 0.1 else "Medium"
                }
                issues.append(issue)
        
        return issues
    
    def _analyze_arbitrage_patterns_in_code(self, contract_code: str,
                                          context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze arbitrage attack patterns in contract code"""
        issues = []
        
        # Check for price discrepancies between DEXes
        arbitrage_indicators = ['uniswap', 'sushiswap', 'pancakeswap', 'arbitrage', 'price']
        
        dex_count = sum(1 for indicator in arbitrage_indicators if indicator in contract_code.lower())
        
        if dex_count >= 2:
            # Multiple DEX interactions detected
            profit_potential = 0.02  # 2% estimated profit potential
            
            issue = {
                'detector': "economic_attack_modeler",
                'title': "Arbitrage Opportunity Detected",
                'description': f"Multiple DEX interactions detected with estimated profit potential of {profit_potential:.2%}",
                'swc_id': "901",
                'severity': "Medium"
            }
            issues.append(issue)
        
        return issues
    
    def _analyze_mev_patterns_in_code(self, contract_code: str,
                                    context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze MEV extraction patterns in contract code"""
        issues = []
        
        # Check for MEV extraction opportunities
        mev_indicators = ['frontrun', 'mev', 'priority', 'gas', 'block']
        
        mev_score = sum(1 for indicator in mev_indicators if indicator in contract_code.lower())
        
        if mev_score >= 2:
            # MEV extraction opportunity detected
            issue = {
                'detector': "economic_attack_modeler",
                'title': f"MEV Extraction Opportunity",
                'description': f"MEV-related patterns detected with {mev_score} indicators",
                'swc_id': "902",
                'severity': "Low"
            }
            issues.append(issue)
        
        return issues
    
    def _calculate_flash_loan_profitability_from_code(self, contract_code: str,
                                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate profitability of potential flash loan attack from code analysis"""
        # Simple heuristic-based analysis
        profitability_score = 0.0
        
        # Look for profit-related keywords
        profit_keywords = ['profit', 'gain', 'return', 'arbitrage', 'spread']
        for keyword in profit_keywords:
            if keyword in contract_code.lower():
                profitability_score += 0.01
        
        # Look for price manipulation patterns
        if 'swap' in contract_code.lower() and 'price' in contract_code.lower():
            profitability_score += 0.02
        
        # Cap at reasonable maximum
        profitability_score = min(profitability_score, 0.15)
        
        return {
            'is_profitable': profitability_score > 0.01,
            'profit_estimate': profitability_score,
            'attack_type': AttackType.FLASH_LOAN_ARBITRAGE,
            'risk_level': 'medium' if profitability_score < 0.1 else 'high'
        }


class FlashLoanAnalyzer:
    """Specialized analyzer for flash loan attacks"""
    
    def __init__(self):
        self.flash_loan_providers = {
            'aave': {
                'fee': 0.0009,  # 0.09%
                'function_signatures': ['flashLoan', 'flashLoanSimple'],
                'callback_pattern': 'executeOperation'
            },
            'dydx': {
                'fee': 0.0,  # No fee but must maintain margin
                'function_signatures': ['initiate', 'operate'],
                'callback_pattern': 'callFunction'
            },
            'uniswap_v3': {
                'fee': 0.0,  # Pay in callback
                'function_signatures': ['flash'],
                'callback_pattern': 'uniswapV3FlashCallback'
            }
        }
        
        self.attack_patterns = {
            'price_manipulation': {
                'indicators': ['swap', 'price', 'oracle'],
                'severity': 'High'
            },
            'liquidation_attack': {
                'indicators': ['liquidate', 'collateral', 'debt'],
                'severity': 'High'
            },
            'governance_attack': {
                'indicators': ['vote', 'proposal', 'delegate'],
                'severity': 'Medium'
            }
        }
    
    def analyze_flash_loan_usage(self, contract_code: str) -> List[FlashLoanPattern]:
        """Analyze flash loan usage patterns in contract code"""
        patterns = []
        
        # Detect flash loan initiation
        if self._has_flash_loan_code(contract_code):
            pattern = self._extract_flash_loan_pattern_from_code(contract_code)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _has_flash_loan_code(self, contract_code: str) -> bool:
        """Check if contract contains flash loan code"""
        flash_loan_indicators = [
            'flashLoan', 'flashloan', 'flash loan',
            'executeOperation', 'callFunction', 'uniswapV3FlashCallback'
        ]
        
        return any(indicator in contract_code for indicator in flash_loan_indicators)
    
    def _extract_flash_loan_pattern_from_code(self, contract_code: str) -> Optional[FlashLoanPattern]:
        """Extract flash loan pattern from contract code"""
        # Simple pattern extraction based on code analysis
        loan_amount = 0.0
        loan_token = "ETH"
        operations = []
        profit_potential = 0.05  # 5% default estimate
        
        # Look for common patterns
        if 'uniswap' in contract_code.lower():
            operations.append('swap')
            profit_potential += 0.02
            
        if 'compound' in contract_code.lower() or 'aave' in contract_code.lower():
            operations.append('lend')
            profit_potential += 0.01
            
        if 'liquidate' in contract_code.lower():
            operations.append('liquidate')
            profit_potential += 0.03
        
        return FlashLoanPattern(
            loan_amount=loan_amount,
            loan_token=loan_token,
            operations=operations,
            profit_potential=min(profit_potential, 0.2),  # Cap at 20%
            risk_level='medium',
            attack_vector=AttackType.FLASH_LOAN_ARBITRAGE if 'swap' in operations else AttackType.LIQUIDITY_MANIPULATION
        )
    
    def calculate_attack_profitability(self, pattern: FlashLoanPattern,
                                     market_conditions: Dict[str, Any]) -> float:
        """Calculate profitability of flash loan attack"""
        # Economic model for calculating profitability
        base_profit = pattern.profit_potential
        
        # Adjust for market conditions
        liquidity_factor = market_conditions.get('liquidity_depth', 1.0)
        volatility_factor = market_conditions.get('volatility', 1.0)
        
        adjusted_profit = base_profit * liquidity_factor * volatility_factor
        
        # Subtract costs (gas, fees, slippage)
        total_costs = self._calculate_attack_costs(pattern, market_conditions)
        
        return max(0, adjusted_profit - total_costs)
    
    def _calculate_attack_costs(self, pattern: FlashLoanPattern,
                              market_conditions: Dict[str, Any]) -> float:
        """Calculate total costs of flash loan attack"""
        # Flash loan fees
        flash_loan_fee = pattern.loan_amount * 0.0009  # Aave fee
        
        # Gas costs
        gas_cost = market_conditions.get('gas_price', 50) * 500000 * 1e-9  # Estimated gas
        
        # Slippage costs
        slippage_cost = pattern.loan_amount * market_conditions.get('slippage', 0.005)
        
        return flash_loan_fee + gas_cost + slippage_cost