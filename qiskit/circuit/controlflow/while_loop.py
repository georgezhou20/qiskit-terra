from .control_flow import ControlFlowOp

class WhileLoopOp(ControlFlowOp):
    def __init__(self, num_qubits, num_clbits, condition, block):
        self.condition = condition  # Kernel[[*bits]] -> bit
        self.block = block  # QuantumCircuit
        super().__init__('while_loop', num_qubits, num_clbits, [])

        self._blocks = [block]
