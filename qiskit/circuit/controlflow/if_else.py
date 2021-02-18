from .control_flow import ControlFlowOp

class IfElseOp(ControlFlowOp):
    def __init__(self, num_qubits, num_clbits, predicate, consequent, alternative):
        self.predicate = predicate  # Kernel[*bits] -> bit
        self.consequent = consequent  # QuantumCircuit
        self.alternative = alternative  # Alternative
        super().__init__('ifelse', num_qubits, num_clbits, [])

        self._blocks = [consequent, alternative]
