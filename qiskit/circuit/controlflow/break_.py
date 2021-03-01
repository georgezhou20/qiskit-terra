from ..instruction import Instruction

class BreakOp(Instruction):
    # Can be inserted only within a subblock of a loop op
    # Must span full width (qubits+cbits) of block

    def __init__(self, num_qubits, num_clbits):
        super().__init__("break", num_qubits, num_clbits, [])
