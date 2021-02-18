from .control_flow import ControlFlowOp

class ForLoopOp(ControlFlowOp):
    def __init__(self, num_qubits, num_clbits, loop_parameter, start, stop, increment, block):
        self.loop_parameter = loop_parameter
        self.start = start
        self.stop = stop
        self.increment = increment
        self.block = block  # QuantumCircuit[loop_parameter]
        super().__init__('for_loop', num_qubits, num_clbits, [])

        self._blocks = [block]
