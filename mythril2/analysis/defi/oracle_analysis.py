"""
Oracle manipulation detection and price feed analysis for DeFi protocols
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re

# Note: IssueAnnotation import commented out to avoid circular dependencies
# from mythril2.analysis.issue_annotation import IssueAnnotation
# from mythril2.laser.ethereum.state.global_state import GlobalState


class OracleType(Enum):
    CHAINLINK = "chainlink"
    UNISWAP_TWAP = "uniswap_twap"
    CUSTOM_ORACLE = "custom"
    PRICE_FEED = "price_feed"


class ManipulationType(Enum):
    FLASH_LOAN_ATTACK = "flash_loan_attack"
    PRICE_MANIPULATION = "price_manipulation"
    TIME_MANIPULATION = "time_manipulation"
    FEED_MANIPULATION = "feed_manipulation"


@dataclass
class OracleConfig:
    """Configuration for oracle analysis"""
    oracle_type: OracleType
    update_threshold: float
    deviation_threshold: float
    heartbeat_period: int
    trusted_sources: List[str]


@dataclass
class PriceData:
    """Price data point for analysis"""
    price: float
    timestamp: int
    source: str
    volume: Optional[float] = None


class OracleManipulationDetector:
    """Detects oracle manipulation vulnerabilities"""
    
    def __init__(self):
        self.oracle_patterns = {
            OracleType.CHAINLINK: {
                'indicators': ['Chainlink', 'AggregatorV3Interface', 'latestRoundData'],
                'vulnerabilities': ['flash_loan_manipulation', 'stale_data']
            },
            OracleType.UNISWAP_TWAP: {
                'indicators': ['UniswapV2Oracle', 'TWAP', 'averagePrice'],
                'vulnerabilities': ['low_liquidity_manipulation', 'short_timeframe']
            },
            OracleType.CUSTOM_ORACLE: {
                'indicators': ['setPrice', 'updatePrice', 'customOracle'],
                'vulnerabilities': ['admin_control', 'centralization']
            }
        }
        
        self.manipulation_patterns = {
            ManipulationType.FLASH_LOAN_ATTACK: {
                'indicators': ['flashloan', 'swap', 'price', 'same_block'],
                'severity': 'Critical',
                'description': 'Flash loan used to manipulate oracle prices'
            },
            ManipulationType.PRICE_MANIPULATION: {
                'indicators': ['price', 'manipulation', 'control'],
                'severity': 'High',
                'description': 'Direct price manipulation detected'
            }
        }
    
    def analyze_oracle_security(self, contract_code: str) -> List[Dict[str, Any]]:
        """Analyze oracle security vulnerabilities in contract code"""
        issues = []
        
        # Detect oracle configuration
        oracle_configs = self._detect_oracle_configs(contract_code)
        
        for config in oracle_configs:
            # Check for flash loan manipulation vulnerability
            flash_loan_issues = self._check_flash_loan_manipulation(contract_code, config)
            issues.extend(flash_loan_issues)
            
            # Check for stale data vulnerability
            stale_data_issues = self._check_stale_data_vulnerability(contract_code, config)
            issues.extend(stale_data_issues)
            
            # Check for centralization risks
            centralization_issues = self._check_centralization_risks(contract_code, config)
            issues.extend(centralization_issues)
            
            # Check for low liquidity manipulation
            liquidity_issues = self._check_liquidity_manipulation(contract_code, config)
            issues.extend(liquidity_issues)
        
        return issues
    
    def _detect_oracle_configs(self, contract_code: str) -> List[OracleConfig]:
        """Detect oracle configurations from contract code"""
        configs = []
        
        # Look for Chainlink oracles
        if 'Chainlink' in contract_code or 'AggregatorV3Interface' in contract_code:
            config = OracleConfig(
                oracle_type=OracleType.CHAINLINK,
                update_threshold=0.01,  # 1%
                deviation_threshold=0.05,  # 5%
                heartbeat_period=3600,  # 1 hour
                trusted_sources=['chainlink']
            )
            configs.append(config)
        
        # Look for Uniswap TWAP oracles
        if 'TWAP' in contract_code or 'averagePrice' in contract_code:
            config = OracleConfig(
                oracle_type=OracleType.UNISWAP_TWAP,
                update_threshold=0.005,  # 0.5%
                deviation_threshold=0.02,  # 2%
                heartbeat_period=600,  # 10 minutes
                trusted_sources=['uniswap']
            )
            configs.append(config)
        
        # Look for custom oracles
        if 'setPrice' in contract_code or 'updatePrice' in contract_code:
            config = OracleConfig(
                oracle_type=OracleType.CUSTOM_ORACLE,
                update_threshold=0.001,  # 0.1%
                deviation_threshold=0.01,  # 1%
                heartbeat_period=300,  # 5 minutes
                trusted_sources=[]
            )
            configs.append(config)
        
        return configs
    
    def _check_flash_loan_manipulation(self, contract_code: str,
                                     config: OracleConfig) -> List[Dict[str, Any]]:
        """Check for flash loan manipulation vulnerabilities"""
        issues = []
        
        # Look for patterns that indicate vulnerability to flash loan manipulation
        vulnerable_patterns = [
            'latestRoundData',
            'priceFeed',
            'getPrice',
            'swap'
        ]
        
        pattern_count = sum(1 for pattern in vulnerable_patterns if pattern in contract_code)
        
        # Check if contract uses price data in the same transaction as swaps
        if pattern_count >= 2 and 'flashloan' in contract_code.lower():
            issue = {
                'detector': "oracle_manipulation_detector",
                'title': "Flash Loan Oracle Manipulation Vulnerability",
                'description': "Contract is vulnerable to flash loan attacks where oracle prices "
                           "can be manipulated within the same transaction to exploit price-dependent logic.",
                'swc_id': "910",
                'severity': "Critical"
            }
            issues.append(issue)
        
        return issues
    
    def _check_stale_data_vulnerability(self, contract_code: str,
                                      config: OracleConfig) -> List[Dict[str, Any]]:
        """Check for stale data vulnerabilities"""
        issues = []
        
        # Look for timestamp checks
        has_timestamp_check = 'updatedAt' in contract_code or 'timestamp' in contract_code
        
        # Look for heartbeat checks
        has_heartbeat_check = 'heartbeat' in contract_code or 'period' in contract_code
        
        if not has_timestamp_check and not has_heartbeat_check:
            issue = {
                'detector': "oracle_manipulation_detector",
                'title': "Stale Oracle Data Vulnerability",
                'description': "Contract does not verify the freshness of oracle data, "
                           "potentially allowing exploitation of stale or outdated prices.",
                'swc_id': "911",
                'severity': "High"
            }
            issues.append(issue)
        
        return issues
    
    def _check_centralization_risks(self, contract_code: str,
                                  config: OracleConfig) -> List[Dict[str, Any]]:
        """Check for centralization risks in oracles"""
        issues = []
        
        # Look for admin control patterns
        admin_patterns = ['onlyOwner', 'admin', 'setPrice', 'updatePrice']
        
        if config.oracle_type == OracleType.CUSTOM_ORACLE:
            admin_control_count = sum(1 for pattern in admin_patterns if pattern in contract_code)
            
            if admin_control_count >= 1:
                issue = {
                    'detector': "oracle_manipulation_detector",
                    'title': "Centralized Oracle Control Risk",
                    'description': "Custom oracle has centralized control mechanisms that could "
                               "be exploited to manipulate price data.",
                    'swc_id': "912",
                    'severity': "Medium"
                }
                issues.append(issue)
        
        return issues
    
    def _check_liquidity_manipulation(self, contract_code: str,
                                    config: OracleConfig) -> List[Dict[str, Any]]:
        """Check for low liquidity manipulation vulnerabilities"""
        issues = []
        
        if config.oracle_type == OracleType.UNISWAP_TWAP:
            # Look for short TWAP periods
            if 'period' in contract_code.lower() or 'window' in contract_code.lower():
                # Check if the TWAP period is too short
                short_period_indicators = ['300', '600', '900']  # 5, 10, 15 minutes
                
                for period in short_period_indicators:
                    if period in contract_code:
                        issue = {
                            'detector': "oracle_manipulation_detector",
                            'title': "Short TWAP Period Vulnerability",
                            'description': f"TWAP oracle uses a short period ({period} seconds), "
                                       "making it vulnerable to price manipulation with low capital.",
                            'swc_id': "913",
                            'severity': "Medium"
                        }
                        issues.append(issue)
                        break
        
        return issues


class PriceFeedAnalyzer:
    """Analyzes price feed data for manipulation patterns"""
    
    def __init__(self):
        self.price_sources = {
            'chainlink': {
                'update_interval': 3600,  # 1 hour
                'deviation_threshold': 0.05,  # 5%
                'confidence_threshold': 0.95
            },
            'uniswap': {
                'update_interval': 300,  # 5 minutes
                'deviation_threshold': 0.02,  # 2%
                'confidence_threshold': 0.90
            },
            'custom': {
                'update_interval': 60,  # 1 minute
                'deviation_threshold': 0.01,  # 1%
                'confidence_threshold': 0.80
            }
        }
    
    def analyze_price_feed(self, price_data: List[PriceData], 
                         source: str) -> Dict[str, Any]:
        """Analyze price feed for manipulation patterns"""
        
        if not price_data:
            return {'status': 'no_data'}
        
        source_config = self.price_sources.get(source, self.price_sources['custom'])
        
        # Calculate basic statistics
        prices = [p.price for p in price_data]
        timestamps = [p.timestamp for p in price_data]
        
        price_mean = np.mean(prices)
        price_std = np.std(prices)
        price_volatility = price_std / price_mean if price_mean > 0 else 0
        
        # Detect anomalies
        anomalies = self._detect_price_anomalies(price_data, source_config)
        
        # Check for manipulation patterns
        manipulation_indicators = self._check_manipulation_patterns(
            price_data, source_config
        )
        
        return {
            'source': source,
            'price_mean': price_mean,
            'price_volatility': price_volatility,
            'anomalies': anomalies,
            'manipulation_indicators': manipulation_indicators,
            'confidence_score': self._calculate_confidence_score(
                price_data, anomalies, manipulation_indicators
            )
        }
    
    def _detect_price_anomalies(self, price_data: List[PriceData],
                              config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect price anomalies in the data"""
        anomalies = []
        
        if len(price_data) < 2:
            return anomalies
        
        # Calculate price changes
        for i in range(1, len(price_data)):
            prev_price = price_data[i-1].price
            curr_price = price_data[i].price
            
            if prev_price > 0:
                price_change = abs(curr_price - prev_price) / prev_price
                
                if price_change > config['deviation_threshold']:
                    anomalies.append({
                        'type': 'price_spike',
                        'timestamp': price_data[i].timestamp,
                        'price_change': price_change,
                        'severity': 'high' if price_change > config['deviation_threshold'] * 2 else 'medium'
                    })
        
        return anomalies
    
    def _check_manipulation_patterns(self, price_data: List[PriceData],
                                   config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for manipulation patterns in price data"""
        indicators = []
        
        if len(price_data) < 3:
            return indicators
        
        # Check for rapid price changes
        for i in range(2, len(price_data)):
            price_1 = price_data[i-2].price
            price_2 = price_data[i-1].price
            price_3 = price_data[i].price
            
            # Look for pump and dump patterns
            if price_1 < price_2 > price_3:
                pump_magnitude = (price_2 - price_1) / price_1 if price_1 > 0 else 0
                dump_magnitude = (price_2 - price_3) / price_2 if price_2 > 0 else 0
                
                if pump_magnitude > 0.05 and dump_magnitude > 0.05:  # 5% threshold
                    indicators.append({
                        'type': 'pump_and_dump',
                        'timestamp': price_data[i].timestamp,
                        'pump_magnitude': pump_magnitude,
                        'dump_magnitude': dump_magnitude
                    })
        
        # Check for stale data
        if len(price_data) >= 2:
            last_update = price_data[-1].timestamp
            second_last_update = price_data[-2].timestamp
            time_diff = last_update - second_last_update
            
            if time_diff > config['update_interval'] * 2:  # Double the expected interval
                indicators.append({
                    'type': 'stale_data',
                    'timestamp': last_update,
                    'time_since_update': time_diff
                })
        
        return indicators
    
    def _calculate_confidence_score(self, price_data: List[PriceData],
                                  anomalies: List[Dict[str, Any]],
                                  manipulation_indicators: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for price feed reliability"""
        base_score = 1.0
        
        # Reduce score based on anomalies
        for anomaly in anomalies:
            if anomaly['severity'] == 'high':
                base_score -= 0.2
            else:
                base_score -= 0.1
        
        # Reduce score based on manipulation indicators
        base_score -= len(manipulation_indicators) * 0.15
        
        return max(0.0, min(1.0, base_score))