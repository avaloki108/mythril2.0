"""
Governance attack vector detection for voting manipulation and proposal spam
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Note: IssueAnnotation import commented out to avoid circular dependencies
# from mythril2.analysis.issue_annotation import IssueAnnotation
# from mythril2.laser.ethereum.state.global_state import GlobalState


class GovernanceType(Enum):
    TOKEN_VOTING = "token_voting"
    DELEGATED_VOTING = "delegated_voting"
    QUADRATIC_VOTING = "quadratic_voting"
    MULTISIG = "multisig"
    TIMELOCK = "timelock"


class AttackVector(Enum):
    FLASH_LOAN_VOTING = "flash_loan_voting"
    VOTE_BUYING = "vote_buying"
    PROPOSAL_SPAM = "proposal_spam"
    TIMELOCK_BYPASS = "timelock_bypass"
    DELEGATION_ATTACK = "delegation_attack"
    QUORUM_MANIPULATION = "quorum_manipulation"


@dataclass
class GovernanceConfig:
    """Configuration for governance analysis"""
    governance_type: GovernanceType
    voting_token: str
    proposal_threshold: float
    quorum_threshold: float
    voting_period: int
    timelock_delay: int


class GovernanceAttackDetector:
    """Detects governance attack vectors and vulnerabilities"""
    
    def __init__(self):
        self.governance_patterns = {
            GovernanceType.TOKEN_VOTING: {
                'functions': ['propose', 'vote', 'execute'],
                'vulnerabilities': ['flash_loan_voting', 'vote_buying']
            },
            GovernanceType.DELEGATED_VOTING: {
                'functions': ['delegate', 'vote', 'propose'],
                'vulnerabilities': ['delegation_attack', 'vote_concentration']
            },
            GovernanceType.TIMELOCK: {
                'functions': ['queue', 'execute', 'cancel'],
                'vulnerabilities': ['timelock_bypass', 'admin_override']
            }
        }
        
        self.attack_patterns = {
            AttackVector.FLASH_LOAN_VOTING: {
                'indicators': ['flashloan', 'vote', 'same_transaction'],
                'severity': 'Critical',
                'description': 'Flash loan used to temporarily acquire voting power'
            },
            AttackVector.PROPOSAL_SPAM: {
                'indicators': ['multiple_proposals', 'low_threshold'],
                'severity': 'Medium',
                'description': 'Proposal spam to overwhelm governance'
            },
            AttackVector.TIMELOCK_BYPASS: {
                'indicators': ['admin_override', 'emergency_function'],
                'severity': 'High',
                'description': 'Mechanism to bypass timelock delays'
            }
        }
    
    def analyze_governance_security(self, contract_code: str) -> List[Dict[str, Any]]:
        """Analyze governance security vulnerabilities in contract code"""
        issues = []
        
        # Detect governance configuration
        gov_config = self._detect_governance_config(contract_code)
        
        if gov_config:
            # Check for flash loan voting vulnerability
            flash_loan_issues = self._check_flash_loan_voting(contract_code, gov_config)
            issues.extend(flash_loan_issues)
            
            # Check for proposal spam vulnerability
            spam_issues = self._check_proposal_spam(contract_code, gov_config)
            issues.extend(spam_issues)
            
            # Check for timelock bypass
            timelock_issues = self._check_timelock_bypass(contract_code, gov_config)
            issues.extend(timelock_issues)
            
            # Check for vote concentration
            concentration_issues = self._check_vote_concentration(contract_code, gov_config)
            issues.extend(concentration_issues)
        
        return issues
    
    def _detect_governance_config(self, contract_code: str) -> Optional[GovernanceConfig]:
        """Detect governance configuration from contract code"""
        # Look for governance patterns
        if 'propose' in contract_code and 'vote' in contract_code:
            # Extract configuration parameters
            proposal_threshold = self._extract_threshold(contract_code, 'proposal')
            quorum_threshold = self._extract_threshold(contract_code, 'quorum')
            
            return GovernanceConfig(
                governance_type=GovernanceType.TOKEN_VOTING,
                voting_token='GOV',  # Default
                proposal_threshold=proposal_threshold,
                quorum_threshold=quorum_threshold,
                voting_period=7 * 24 * 3600,  # 1 week default
                timelock_delay=2 * 24 * 3600   # 2 days default
            )
        
        return None
    
    def _extract_threshold(self, contract_code: str, threshold_type: str) -> float:
        """Extract threshold values from contract code"""
        # Simple pattern matching for threshold values
        patterns = [
            f'{threshold_type}Threshold',
            f'{threshold_type}Quorum',
            f'{threshold_type}Requirement'
        ]
        
        for pattern in patterns:
            if pattern in contract_code:
                # Look for percentage values
                import re
                matches = re.findall(r'(\d+)\s*\/\s*(\d+)', contract_code)
                for match in matches:
                    if len(match) == 2:
                        numerator = int(match[0])
                        denominator = int(match[1])
                        return numerator / denominator if denominator > 0 else 0.01
        
        # Default thresholds
        if threshold_type == 'proposal':
            return 0.01  # 1%
        elif threshold_type == 'quorum':
            return 0.04  # 4%
        
        return 0.01
    
    def _check_flash_loan_voting(self, contract_code: str,
                               gov_config: GovernanceConfig) -> List[Dict[str, Any]]:
        """Check for flash loan voting vulnerabilities"""
        issues = []
        
        # Look for voting power calculation patterns
        if 'getVotes' in contract_code or 'balanceOf' in contract_code:
            # Check if there are any time-based restrictions
            has_time_restriction = (
                'block.timestamp' in contract_code or
                'timeLock' in contract_code or
                'snapshot' in contract_code.lower()
            )
            
            if not has_time_restriction:
                issue = {
                    'detector': "governance_attack_detector",
                    'title': "Flash Loan Governance Attack Vulnerability",
                    'description': "Governance system is vulnerable to flash loan attacks where attackers "
                               "can temporarily acquire large voting power to pass malicious proposals. "
                               "Consider implementing voting power snapshots or minimum holding periods.",
                    'swc_id': "930",
                    'severity': "Critical"
                }
                issues.append(issue)
        
        return issues
    
    def _check_proposal_spam(self, contract_code: str,
                           gov_config: GovernanceConfig) -> List[Dict[str, Any]]:
        """Check for proposal spam vulnerabilities"""
        issues = []
        
        if gov_config.proposal_threshold < 0.01:  # 1% threshold
            issue = {
                'detector': "governance_attack_detector",
                'title': "Proposal Spam Vulnerability",
                'description': "Low proposal threshold allows attackers to spam governance with "
                           "numerous proposals, potentially overwhelming the system and voters. "
                           "Consider increasing proposal threshold or implementing rate limiting.",
                'swc_id': "931",
                'severity': "Medium"
            }
            issues.append(issue)
        
        return issues
    
    def _check_timelock_bypass(self, contract_code: str,
                             gov_config: GovernanceConfig) -> List[Dict[str, Any]]:
        """Check for timelock bypass vulnerabilities"""
        issues = []
        
        # Look for bypass mechanisms
        bypass_patterns = [
            'emergency',
            'cancel',
            'override',
            'executeImmediately',
            'skipTimelock'
        ]
        
        for pattern in bypass_patterns:
            if pattern in contract_code:
                issue = {
                    'detector': "governance_attack_detector",
                    'title': "Timelock Bypass Mechanism Detected",
                    'description': f"Contract contains '{pattern}' mechanisms that could bypass "
                               "timelock delays, potentially allowing immediate execution "
                               "of critical changes. This undermines the security provided by timelocks.",
                    'swc_id': "932",
                    'severity': "High"
                }
                issues.append(issue)
                break
        
        return issues
    
    def _check_vote_concentration(self, contract_code: str,
                                gov_config: GovernanceConfig) -> List[Dict[str, Any]]:
        """Check for vote concentration risks"""
        issues = []
        
        # Look for delegation mechanisms
        if 'delegate' in contract_code:
            # Check if there are limits on delegation
            has_delegation_limits = (
                'maxDelegation' in contract_code or
                'delegationLimit' in contract_code or
                'cap' in contract_code
            )
            
            if not has_delegation_limits:
                issue = {
                    'detector': "governance_attack_detector",
                    'title': "Unlimited Delegation Risk",
                    'description': "Governance system allows unlimited delegation without caps, "
                               "which could lead to excessive vote concentration and reduced "
                               "decentralization.",
                    'swc_id': "933",
                    'severity': "Medium"
                }
                issues.append(issue)
        
        return issues