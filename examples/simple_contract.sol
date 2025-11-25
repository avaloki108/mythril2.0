// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleVulnerable {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    // Vulnerable: No access control on selfdestruct
    function destroy() public {
        selfdestruct(payable(msg.sender));
    }
    
    // Vulnerable: Integer overflow in older Solidity versions
    function add(uint a, uint b) public pure returns (uint) {
        return a + b;
    }
}
