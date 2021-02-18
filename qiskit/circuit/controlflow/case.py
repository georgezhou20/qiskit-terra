from .control_flow import ControlFlowOp

class CaseOp(ControlFlowOp):
    def __init__(self, num_qubits, num_clbits, pred_fn_list):
        self.pred_fn_list = pred_fn_list
        super().__init__('case', num_qubits, num_clbits, [])

        self._blocks = [fn for (pred, fn) in pred_fn_list]
