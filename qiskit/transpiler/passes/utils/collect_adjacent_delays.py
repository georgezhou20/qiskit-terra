import logging

from pprint import pformat, pprint
from dataclasses import dataclass
from collections import defaultdict

from typing import List

from qiskit.circuit import Delay, QuantumCircuit
from qiskit.converters import circuit_to_dag
from qiskit.dagcircuit import DAGOpNode
from qiskit.transpiler import TransformationPass, CouplingMap

logger = logging.getLogger(__name__)

MIN_JOINABLE_DELAY_DURATION = 200

class CombineAdjacentDelays(TransformationPass):
    def __init__(self, cmap):
        self.cmap = cmap
        super().__init__()


    def run(self, dag):
        bit_idx_locs = {bit: idx for idx, bit in enumerate(dag.qubits)}

        # Collect and sort a list of all times where a delay starts or ends
        # These will be the places we'll examine to split/combine delay ops.
        sorted_delay_edges = sorted(
            (
                (event_type,
                 start_time if event_type == 'begin' else start_time + op_node.op.duration,
                 op_node)
                for op_node, start_time in self.property_set['node_start_time'].items()
                if (
                    op_node.op.name == 'delay'
                    and start_time != 0  # Skip delays at start of circuit
                    and start_time + op_node.op.duration < dag.duration  # Skip delays at end of circuit
                    and op_node.op.duration > MIN_JOINABLE_DELAY_DURATION
                )
                for event_type in ('begin', 'end')
            ),
        key=lambda itm: itm[1])
        joinable_delay_nodes = set(op_node for _, __, op_node in sorted_delay_edges)

        logger.info(pformat(sorted_delay_edges))

        @dataclass
        class ReplacementDelay:
            new_delay_op: Delay
            start_time: int
            end_time: int
            replacing_delay_nodes: List[DAGOpNode]

        open_delays = []  # new_delay_op start_time, replacing_delay_nodes
        closed_delays = []  # new_delay_op, start_time, end_time, replacing_delay_nodes

        def _open_delay(start_time, replacing_delay_nodes):
            delay_op = Delay(0)
            delay_op.num_qubits = len(replacing_delay_nodes)

            open_delays.append((delay_op, start_time, replacing_delay_nodes))

        def _expand_delay(start_time, existing_delay, new_replacing_delay_node):
            delay_op = Delay(0)
            delay_op.num_qubits = 1 + existing_delay[0].num_qubits

            _close_delay(existing_delay, start_time, closing_op_node=None)  # Don't auto-open a new delay.
            open_delays.append((delay_op, start_time, existing_delay[2] + [new_replacing_delay_node]))

        def _close_delay(delay, end_time, closing_op_node=None):
            delay_op, start_time, replacing_delay_nodes = delay
            open_delays.remove(delay)

            # When merging delays, we might end up opening and immediately closing a delay at the same time it started.
            # So in this case, just drop it.
            if start_time != end_time:
                delay_op.duration = end_time - start_time
                closed_delays.append((delay_op, start_time, end_time, replacing_delay_nodes))

            # If we're closing a delay on 1 qubit out of many, re-open a N-1 qubit delay on the remaining qubits
            if closing_op_node is not None and len(replacing_delay_nodes) > 1:
                _open_delay(end_time, [node for node in replacing_delay_nodes if node is not closing_op_node])

        def _combine_delays(old_delay_node, start_time, delays):
            # If we find a delay opening which is adjacent two two or more open delays.

            for delay in delays:
                _close_delay(delay, start_time)
            _open_delay(start_time,
                        [old_delay_node] + [node for delay in delays for node in delay[2]])

        for edge_type, edge_time, edge_node in sorted_delay_edges:
            adjacent_open_delays = [open_delay for open_delay in open_delays
                                    if any(
                                        self.cmap.distance(
                                            bit_idx_locs[edge_node.qargs[0]],
                                            bit_idx_locs[open_delay_qarg]) <= 1
                                           for open_delay_node in open_delay[2]
                                           for open_delay_qarg in open_delay_node.qargs)]
            if edge_type == 'begin':
                # If crossing a begin edge, check if there are any open delays that are adjacent.
                # If so, close those, and open a new delay spanning those qubits and this one.
                # If not, open a new delay.

                if len(adjacent_open_delays) == 0:
                    # Make a new delay
                    _open_delay(edge_time, [edge_node])
                else:
                    # Combine that with this
                    _combine_delays(edge_node, edge_time, adjacent_open_delays)

            if edge_type == 'end':
                # If crossing a end edge, close any open delay on this qubit (and re-open a delay on any qubits this delay had shared)
                if len(adjacent_open_delays) != 1:
                    import pdb; pdb.set_trace()
                    raise Exception("closing edge w/o an open delay?")
                else:
                    _close_delay(adjacent_open_delays[0], edge_time, edge_node)

            logger.info(pformat((
                '---exit---',
                [edge_type, edge_time, edge_node],
                ('open_delays: ', open_delays),
                ('closed_delays: ', closed_delays),
            )))

        logger.info(pformat((
            '---post_collect---',
            ('open_delays: ', open_delays),
            ('len(closed_delays): ', len(closed_delays)),
            ('len(multi_q_delays): ', len([delay for delay in closed_delays if delay[0].num_qubits > 1])),
        ))) #Expect ~30 for example qv 256

        # Rebuild dag from topological sort w/ delays deferred as much as possible
        # From there will need to manually pop delays 
        # create lookup from delay to replacements sorted by start time

        replacement_ops = defaultdict(list)  # existing_delay_node, [sorted_list_of_replacement_delays]
        for closed_delay in sorted(closed_delays, key=lambda k: (k[1], k[2])):  # Might already be in right order?
            (delay_op, start_time, end_time, replacing_delay_nodes) = closed_delay

            for replacing_delay_node in replacing_delay_nodes:
                replacement_ops[replacing_delay_node].append(closed_delay)

        out_dag = dag.copy_empty_like()

        open_delay_nodes = []
        # bug? topological_op_node key has to handle io nodes, also appears not to work if i concatinate e.g. 'a' + _sort_key
        #display(dag.draw())
        def _key(node):
            return ('a' if isinstance(node, DAGOpNode) and node.op.name == 'delay' else 'b')

        # Walk through existing dag, grabbing delays as early as possible
        water_mark = 0
        added_delay_ids = set()  # Hacks all the way down. We're adding delays repeatidly for some QV circuits, so step around for now.

        for node in dag.topological_op_nodes(key=_key):
            logger.info(pformat((
                '---dag_walk---',
                (node.op.name, [bit_idx_locs[qarg] for qarg in node.qargs]),
                ('len(open_delay_nodes)', len(open_delay_nodes)),
                ('_key(node)', _key(node)),
                ('water_mark', water_mark),
            )))

            # If it's a joinable delay, add it to open_delay_nodes
            # If its not a delay, and there are no open delay nodes, add it
            # If its not a delay, and there are open delay nodes, add any preceding delays (by qargs) and any delays which would precede them...
            # At the end, wrap up any final delays still in open_delay_nodes

            if node in joinable_delay_nodes:
                open_delay_nodes.append(node)
            else:
                if not open_delay_nodes:
                    out_dag.apply_operation_back(node.op, node.qargs, node.cargs)
                else:
                    # If we come across a node that's not a delay, we need to resolve all the delays
                    # Tracking all the way back through open_delays

                    replacements_for_open_delays = sorted(
                        (replacement_delay
                         for open_delay_node in open_delay_nodes
                         for replacement_delay in replacement_ops[open_delay_node]
                        ),
                        key=lambda c: (c[1], c[2])
                    )

                    # replacements_for_open_delays will have duplicates for multi-q delays
                    # e.g. if we had a 3q vchain, we'll open two delays, the first will have three replacements,
                    # the second will have one, but it will be the same as the middle of the above
                    # hack a quick filter now

                    seen_replacement_ids = set()
                    unique_replacements_for_open_delays = []
                    for replacement in replacements_for_open_delays:
                        if id(replacement) not in seen_replacement_ids:
                            unique_replacements_for_open_delays.append(replacement)
                            seen_replacement_ids.add(id(replacement))
                    replacements_for_open_delays = unique_replacements_for_open_delays

                    # pprint(replacements_for_open_delays)

                    if replacements_for_open_delays:
                        for replacement in replacements_for_open_delays:
                            # Should really track dependencies backwards to find out which delays to add
                            # Maybe we can cheat it since we already have a scheduled circuit
                            if water_mark < replacement[2] <= self.property_set['node_start_time'][node]:
                                if id(replacement[0]) not in added_delay_ids:
                                    added_delay_ids.add(id(replacement[0]))
                                    out_dag.apply_operation_back(replacement[0],
                                                                 [qarg for nnode in replacement[3] for qarg in nnode.qargs],
                                                                 []
                                                                 )
                        water_mark = self.property_set['node_start_time'][node]
                    else:
                        # If this is a delay that doesn't have a replacement
                        # This is hacky, it seems like we could pick up final delays here
                        for open_delay in open_delay_nodes:
                            if id(open_delay.op) not in added_delay_ids:
                                added_delay_ids.add(id(open_delay.op))
                                out_dag.apply_operation_back(open_delay.op, open_delay.qargs, open_delay.cargs)

                    #open_delay_nodes = []
                    if id(node.op) not in added_delay_ids:
                        added_delay_ids.add(id(node.op))
                        out_dag.apply_operation_back(node.op, node.qargs, node.cargs)

        # Any remaining delays
        for open_delay_node in open_delay_nodes:
            if not replacement_ops[open_delay_node] and self.property_set['node_start_time'][open_delay_node] > 0:
                if id(open_delay_node.op) not in added_delay_ids:
                    added_delay_ids.add(id(open_delay_node.op))
                    out_dag.apply_operation_back(open_delay_node.op, open_delay_node.qargs, open_delay_node.cargs)

        return out_dag
