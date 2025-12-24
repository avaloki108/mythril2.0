"""
Feature extraction for ML-based analysis
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from collections import Counter

from mythril.laser.ethereum.state.global_state import GlobalState
from mythril.laser.ethereum.state.machine_state import MachineState
from mythril.disassembler.disassembly import Disassembly


@dataclass
class CodeFeatures:
    """Container for extracted code features"""
    
    # Opcode features
    opcode_frequency: Dict[str, int]
    opcode_sequences: List[str]
    
    # Control flow features
    jump_count: int
    loop_count: int
    function_count: int
    
    # State features
    storage_operations: int
    external_calls: int
    delegate_calls: int
    
    # Economic features
    ether_operations: int
    balance_checks: int
    transfer_operations: int
    
    # DeFi specific features
    oracle_interactions: int
    flash_loan_patterns: int
    liquidity_operations: int
    
    # Security features
    reentrancy_patterns: int
    overflow_patterns: int
    access_control_checks: int
    
    def to_vector(self) -> np.ndarray:
        """Convert features to numerical vector for ML"""
        vector = []
        
        # Opcode frequency (top 20 opcodes)
        common_opcodes = [
            'PUSH1', 'POP', 'DUP1', 'SWAP1', 'SLOAD', 'SSTORE',
            'CALL', 'DELEGATECALL', 'STATICCALL', 'RETURN',
            'REVERT', 'JUMPI', 'JUMP', 'ADD', 'SUB', 'MUL',
            'DIV', 'MOD', 'EQ', 'LT'
        ]
        
        for opcode in common_opcodes:
            vector.append(self.opcode_frequency.get(opcode, 0))
        
        # Control flow features
        vector.extend([
            self.jump_count,
            self.loop_count, 
            self.function_count
        ])
        
        # State features
        vector.extend([
            self.storage_operations,
            self.external_calls,
            self.delegate_calls
        ])
        
        # Economic features
        vector.extend([
            self.ether_operations,
            self.balance_checks,
            self.transfer_operations
        ])
        
        # DeFi features
        vector.extend([
            self.oracle_interactions,
            self.flash_loan_patterns,
            self.liquidity_operations
        ])
        
        # Security features
        vector.extend([
            self.reentrancy_patterns,
            self.overflow_patterns,
            self.access_control_checks
        ])
        
        return np.array(vector, dtype=np.float32)


class FeatureExtractor:
    """Extracts features from smart contract code for ML analysis"""
    
    def __init__(self):
        self.defi_patterns = {
            'oracle': ['oracle', 'price', 'feed', 'chainlink', 'band'],
            'flash_loan': ['flash', 'loan', 'borrow', 'aave', 'dydx'],
            'liquidity': ['liquidity', 'pool', 'swap', 'uniswap', 'sushiswap'],
            'governance': ['vote', 'proposal', 'governance', 'delegate']
        }
        
        self.security_patterns = {
            'reentrancy': ['call', 'transfer', 'send', 'external'],
            'overflow': ['add', 'sub', 'mul', 'div', 'safemath'],
            'access_control': ['onlyowner', 'require', 'modifier', 'auth']
        }
    
    def extract_features(self, global_state: GlobalState) -> CodeFeatures:
        """Extract features from global state"""
        
        # Get current instruction and context
        instruction = global_state.get_current_instruction()
        mstate = global_state.mstate
        
        # Initialize feature counters
        opcode_freq = Counter()
        opcode_sequences = []
        
        # Extract from current instruction
        if instruction:
            opcode = instruction.get('opname', '')
            opcode_freq[opcode] += 1
        
        # Analyze machine state
        storage_ops = self._count_storage_operations(mstate)
        external_calls = self._count_external_calls(mstate)
        delegate_calls = self._count_delegate_calls(mstate)
        
        # Economic operations
        ether_ops = self._count_ether_operations(mstate)
        balance_checks = self._count_balance_checks(mstate)
        transfer_ops = self._count_transfer_operations(mstate)
        
        # DeFi patterns (simplified)
        oracle_interactions = 0
        flash_loan_patterns = 0
        liquidity_operations = 0
        
        # Security patterns
        reentrancy_patterns = self._detect_reentrancy_patterns(global_state)
        overflow_patterns = self._detect_overflow_patterns(mstate)
        access_control_checks = self._detect_access_control(global_state)
        
        return CodeFeatures(
            opcode_frequency=dict(opcode_freq),
            opcode_sequences=opcode_sequences,
            jump_count=self._count_jumps(mstate),
            loop_count=0,  # Would need more sophisticated analysis
            function_count=0,  # Would need contract-level analysis
            storage_operations=storage_ops,
            external_calls=external_calls,
            delegate_calls=delegate_calls,
            ether_operations=ether_ops,
            balance_checks=balance_checks,
            transfer_operations=transfer_ops,
            oracle_interactions=oracle_interactions,
            flash_loan_patterns=flash_loan_patterns,
            liquidity_operations=liquidity_operations,
            reentrancy_patterns=reentrancy_patterns,
            overflow_patterns=overflow_patterns,
            access_control_checks=access_control_checks
        )
    
    def extract_from_code(self, code: str) -> CodeFeatures:
        """Extract features from raw contract code"""
        # Simplified feature extraction from source code
        opcode_freq = Counter()
        
        # Count DeFi patterns
        oracle_count = sum(1 for pattern in self.defi_patterns['oracle'] 
                          if pattern.lower() in code.lower())
        flash_loan_count = sum(1 for pattern in self.defi_patterns['flash_loan'] 
                              if pattern.lower() in code.lower())
        liquidity_count = sum(1 for pattern in self.defi_patterns['liquidity'] 
                             if pattern.lower() in code.lower())
        
        # Count security patterns
        reentrancy_count = sum(1 for pattern in self.security_patterns['reentrancy'] 
                              if pattern.lower() in code.lower())
        overflow_count = sum(1 for pattern in self.security_patterns['overflow'] 
                            if pattern.lower() in code.lower())
        access_control_count = sum(1 for pattern in self.security_patterns['access_control'] 
                                  if pattern.lower() in code.lower())
        
        return CodeFeatures(
            opcode_frequency=dict(opcode_freq),
            opcode_sequences=[],
            jump_count=code.count('jump'),
            loop_count=code.count('for') + code.count('while'),
            function_count=code.count('function'),
            storage_operations=code.count('storage'),
            external_calls=code.count('call'),
            delegate_calls=code.count('delegatecall'),
            ether_operations=code.count('ether') + code.count('wei'),
            balance_checks=code.count('balance'),
            transfer_operations=code.count('transfer'),
            oracle_interactions=oracle_count,
            flash_loan_patterns=flash_loan_count,
            liquidity_operations=liquidity_count,
            reentrancy_patterns=reentrancy_count,
            overflow_patterns=overflow_count,
            access_control_checks=access_control_count
        )
    
    def _count_storage_operations(self, mstate: MachineState) -> int:
        """Count storage operations in machine state"""
        # This would analyze the stack and memory for SLOAD/SSTORE patterns
        return 0
    
    def _count_external_calls(self, mstate: MachineState) -> int:
        """Count external calls"""
        return 0
    
    def _count_delegate_calls(self, mstate: MachineState) -> int:
        """Count delegate calls"""
        return 0
    
    def _count_ether_operations(self, mstate: MachineState) -> int:
        """Count ether-related operations"""
        return 0
    
    def _count_balance_checks(self, mstate: MachineState) -> int:
        """Count balance check operations"""
        return 0
    
    def _count_transfer_operations(self, mstate: MachineState) -> int:
        """Count transfer operations"""
        return 0
    
    def _count_jumps(self, mstate: MachineState) -> int:
        """Count jump operations"""
        return 0
    
    def _detect_reentrancy_patterns(self, global_state: GlobalState) -> int:
        """Detect reentrancy patterns"""
        return 0
    
    def _detect_overflow_patterns(self, mstate: MachineState) -> int:
        """Detect overflow patterns"""
        return 0
    
    def _detect_access_control(self, global_state: GlobalState) -> int:
        """Detect access control patterns"""
        return 0