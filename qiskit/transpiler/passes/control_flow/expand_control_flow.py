import retworkx as rx

from qiskit.circuit import ControlFlowOp, Instruction, Qubit, Clbit, ForLoopOp, WhileLoopOp, KernelFunctionOp, ClassicalRegister, QuantumRegister, IfElseOp
from qiskit.dagcircuit import DAGCircuit, DAGNode
from qiskit.converters import circuit_to_dag
from qiskit.transpiler import TransformationPass

class ExpandControlFlow(TransformationPass):
    def run(self, dag):
        for node in dag.op_nodes():
            if isinstance(node.op, ControlFlowOp):
                block_dags=[circuit_to_dag(block) for block in node.op._blocks]

                repl_dag = DAGCircuit()
                repl_dag.add_qubits([Qubit() for _ in node.qargs])
                repl_dag.add_clbits([Clbit() for _ in node.cargs])

                # Need these not to be "ControlFlowOps", but can be better than just Instructions
                entry_op = Instruction('enter_' + node.op.name, len(node.qargs), len(node.cargs), [])
                placeholder_ops = [
                    Instruction('ph', len(node.qargs), len(node.cargs), [])
                    for _ in block_dags
                ]
                exit_op = Instruction('exit_' + node.op.name, len(node.qargs), len(node.cargs), [])              

                repl_dag.apply_operation_back(entry_op, repl_dag.qubits, repl_dag.clbits)

                # Add an entry and exit node for each block.
                # N.B this will break some conventions as we'll no longer have 1 to 1 on
                # input to output wires

                for ph_op in placeholder_ops:
                    # For each block, add a placeholder (to be replaced with the block)
                    # plus an entry and exit node to collect all the input output wires
                    repl_dag.apply_operation_back(Instruction('ph_enter', len(node.qargs), len(node.cargs), []), repl_dag.qubits, repl_dag.clbits)
                    repl_dag.apply_operation_back(ph_op, repl_dag.qubits, repl_dag.clbits)
                    repl_dag.apply_operation_back(Instruction('ph_exit', len(node.qargs), len(node.cargs), []), repl_dag.qubits, repl_dag.clbits)

                repl_dag.apply_operation_back(exit_op, repl_dag.qubits, repl_dag.clbits)

                dag.substitute_node_with_dag(node, repl_dag)

                # Need to do substitute into main dag before wire mangling
                # Also, have no reference to our nodes anymore

                ph_node_ids = [nd_id for nd_id in rx.topological_sort(dag._multi_graph)
                               if dag._multi_graph[nd_id].name == 'ph']
                entry_node_id = dag._multi_graph.predecessor_indices(
                    dag._multi_graph.predecessor_indices(ph_node_ids[0])[0])[0]
                exit_node_id = dag._multi_graph.successor_indices(
                    dag._multi_graph.successor_indices(ph_node_ids[-1])[0])[0]

                # Don't have a great way to splice in gate fan in, so add all the branches sequentially, then go back and rewire
                ph_boundaries = []

                for ph_node_id, block_dag in zip(ph_node_ids, block_dags):
                    ph_enter_id = dag._multi_graph.predecessor_indices(ph_node_id)[0]
                    ph_exit_id = dag._multi_graph.successor_indices(ph_node_id)[1]
                    ph_boundaries.append((ph_enter_id, ph_exit_id))

                    block_node = dag.substitute_node_with_dag(dag._multi_graph[ph_node_id], block_dag)

                for ph_enter_id, ph_exit_id in ph_boundaries:
                    dag._multi_graph.add_edges_from([
                        (entry_node_id, child_index, edge_data)
                        for (_, child_index, edge_data)
                        in dag._multi_graph.out_edges(ph_enter_id)
                    ])

                    dag._multi_graph.remove_node(ph_enter_id)

                    dag._multi_graph.add_edges_from([
                        (parent_index, exit_node_id, edge_data)
                        for (parent_index, _, edge_data)
                        in dag._multi_graph.in_edges(ph_exit_id)
                    ])
                    dag._multi_graph.remove_node(ph_exit_id)


                if isinstance(node.op, (ForLoopOp, WhileLoopOp)):
                    if isinstance(node.op, ForLoopOp):
                        condition = KernelFunctionOp(len(node.cargs))
                    else:
                        condition = KernelFunctionOp(len(node.cargs))

                    condition_node_id = dag._add_op_node(condition, [], node.cargs)

                    dag._multi_graph.add_edges_from([
                        (exit_node_id, condition_node_id, carg)
                        for carg in node.cargs
                    ])
                    cond_reg = ClassicalRegister(1)  # Single clbit visualizaiton bug
                    cond_bit = cond_reg[0]
                    dag.add_creg(cond_reg)
                    dag._multi_graph.remove_edge(dag.input_map[cond_bit]._node_id, dag.output_map[cond_bit]._node_id)
                    dag._multi_graph.add_edge(dag.input_map[cond_bit]._node_id, condition_node_id, cond_bit)
                    dag._multi_graph.add_edge(condition_node_id, entry_node_id, cond_bit)
                    dag._multi_graph.add_edge(entry_node_id, dag.output_map[cond_bit]._node_id, cond_bit)

                # if isinstance(node.op, IfElseOp):
                #     cond_dag = DAGCircuit()
                #     cond_dag.add_qreg(QuantumRegister(len(node.qargs)))
                #     cond_dag.add_creg(ClassicalRegister(len(node.cargs)))

                #     cond_dag.apply_operation_back(entry_op, cond_dag.qubits, cond_dag.clbits)
                #     cond_dag.apply_operation_back(KernelFunctionOp(len(node.cargs)), [], cond_dag.clbits)

                #     dag.substitute_node_with_dag(dag._multi_graph[entry_node_id], cond_dag)
                # The s_n_w_d here severs ties to the other branches, to leave off for now.

        return dag
                    

                    

                
                
                
                
    
