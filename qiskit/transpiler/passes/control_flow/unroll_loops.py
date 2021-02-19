from qiskit.circuit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from qiskit.transpiler import TransformationPass


class UnrollLoops(TransformationPass):
    def run(self, dag):
        # Could do same for if/while loop if expressions are compile-time constant
        loop_nodes = dag.named_nodes('for_loop')
        
        for loop_node in loop_nodes:
            unrolled_block = QuantumCircuit(len(loop_node.qargs), len(loop_node.cargs))
            for parameter_value in range(loop_node.op.start, loop_node.op.stop, loop_node.op.increment):
                loop_iteration = loop_node.op.block.bind_parameters({loop_node.op.loop_parameter: parameter_value})
                # Need to check loop_parameters are added to circuit.parameters on _append (so nested loops like
                # for i in range(10): for j in range(i): work)

                unrolled_block.append(loop_iteration, unrolled_block.qubits, unrolled_block.clbits)
                
            dag.substitute_node_with_dag(loop_node, circuit_to_dag(unrolled_block))

        # KDK We need to remove from _subcircuits, but need to ensure they are not reused elsewhere.
        # subcircuits as Dict[Circ, List[Instr]] and if len(value) == 1, can drop
                
        return dag
