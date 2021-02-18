from .instruction import Instruction

class KernelFunctionOp(Instruction):
    def __init__(self, clbits, src=None):
        self.src = src  # python function, signature TBD (*bits -> bit ?)
        super().__init__('kernel', 0, clbits, [])
