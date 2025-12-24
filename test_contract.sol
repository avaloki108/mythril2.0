// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TestContract {
    uint256 public value;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function setValue(uint256 _value) public {
        require(msg.sender == owner, "Only owner can set value");
        value = _value;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Only owner can withdraw");
        payable(msg.sender).transfer(address(this).balance);
    }
}