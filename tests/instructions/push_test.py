import pytest

from mythril2.disassembler.disassembly import Disassembly
from mythril2.laser.ethereum.instructions import Instruction
from mythril2.laser.ethereum.state.environment import Environment
from mythril2.laser.ethereum.state.global_state import GlobalState
from mythril2.laser.ethereum.state.machine_state import MachineState
from mythril2.laser.ethereum.state.world_state import WorldState
from mythril2.laser.ethereum.transaction.transaction_models import MessageCallTransaction
from mythril2.laser.smt import simplify, symbol_factory


def get_state(input):
    world_state = WorldState()
    account = world_state.create_account(balance=10, address=101)
    account.code = Disassembly(input)
    environment = Environment(account, None, None, None, None, None, None)
    state = GlobalState(world_state, environment, None, MachineState(gas_limit=8000000))
    state.transaction_stack.append(
        (MessageCallTransaction(world_state=WorldState(), gas_limit=8000000), None)
    )
    return state


BVV = symbol_factory.BitVecVal
BV = symbol_factory.BitVecSym

test_data = [
    ("5F", 0),  # Successful execution, stack consists of a single item, set to zero
    (
        "5F" * 1024,
        0,
    ),  # Successful execution, stack consists of 1024 items, all set to zero
]


@pytest.mark.parametrize("inputs,output", test_data)
def test_push0(inputs, output):
    # Arrange
    state = get_state(inputs)

    instruction = Instruction("push", dynamic_loader=None)

    # Act
    new_state = instruction.evaluate(state)[0]

    # Assert
    assert simplify(new_state.mstate.stack[-1]) == output
