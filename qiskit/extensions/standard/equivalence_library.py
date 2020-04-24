# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Standard gates."""


# pylint: disable=invalid-name

from qiskit.qasm import pi
from qiskit.circuit import EquivalenceLibrary, Parameter, QuantumCircuit, QuantumRegister

from . import (
    HGate,
    CHGate,
    MSGate,
    RGate,
    RCCXGate,
    RC3XGate,
    C3XGate,
    C4XGate,
    RXGate,
    CRXGate,
    RXXGate,
    RYGate,
    CRYGate,
    RZGate,
    CRZGate,
    RZZGate,
    SGate,
    SdgGate,
    SwapGate,
    CSwapGate,
    iSwapGate,
    DCXGate,
    TGate,
    TdgGate,
    U1Gate,
    CU1Gate,
    U2Gate,
    U3Gate,
    CU3Gate,
    XGate,
    CXGate,
    CCXGate,
    YGate,
    CYGate,
    RYYGate,
    ZGate,
    CZGate,
)


_sel = StandardEquivalenceLibrary = EquivalenceLibrary()


# Import existing gate definitions

# HGate

q = QuantumRegister(1, 'q')
def_h = QuantumCircuit(q)
def_h.append(U2Gate(0, pi), [q[0]], [])
_sel.add_equivalence(HGate(), def_h, validate=False)

# CHGate

q = QuantumRegister(2, 'q')
def_ch = QuantumCircuit(q)
for inst, qargs, cargs in [
        (SGate(), [q[1]], []),
        (HGate(), [q[1]], []),
        (TGate(), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (TdgGate(), [q[1]], []),
        (HGate(), [q[1]], []),
        (SdgGate(), [q[1]], [])
]:
    def_ch.append(inst, qargs, cargs)
_sel.add_equivalence(CHGate(), def_ch, validate=False)

# MSGate

for num_qubits in range(2, 20):
    q = QuantumRegister(num_qubits, 'q')
    theta = Parameter('theta')
    def_ms = QuantumCircuit(q)
    for i in range(num_qubits):
        for j in range(i + 1, num_qubits):
            def_ms.append(RXXGate(theta), [q[i], q[j]])
    _sel.add_equivalence(MSGate(num_qubits, theta), def_ms, validate=False)

# RGate

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
phi = Parameter('phi')
def_r = QuantumCircuit(q)
def_r.append(U3Gate(theta, phi - pi / 2, -phi + pi / 2), [q[0]])
_sel.add_equivalence(RGate(theta, phi), def_r, validate=False)

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
def_part_r = QuantumCircuit(q)
#def_r.append(U3Gate(theta, phi - pi / 2, -phi + pi / 2), [q[0]])
def_part_r.append(RXGate(theta), [q[0]])
_sel.add_equivalence(RGate(theta, 0), def_part_r, validate=False)

# RCCXGate

q = QuantumRegister(3, 'q')
def_rccx = QuantumCircuit(q)
for inst, qargs, cargs in [
        (HGate(), [q[2]], []),
        (TGate(), [q[2]], []),
        (CXGate(), [q[1], q[2]], []),
        (TdgGate(), [q[2]], []),
        (CXGate(), [q[0], q[2]], []),
        (TGate(), [q[2]], []),
        (CXGate(), [q[1], q[2]], []),
        (TdgGate(), [q[2]], []),
        (HGate(), [q[2]], []),
]:
    def_rccx.append(inst, qargs, cargs)
_sel.add_equivalence(RCCXGate(), def_rccx, validate=False)

# RC3XGate

q = QuantumRegister(4, 'q')
def_rc3x = QuantumCircuit(q)
for inst, qargs, cargs in [
        (HGate(), [q[3]], []),
        (TGate(), [q[3]], []),
        (CXGate(), [q[2], q[3]], []),
        (TdgGate(), [q[3]], []),
        (HGate(), [q[3]], []),
        (CXGate(), [q[0], q[3]], []),
        (TGate(), [q[3]], []),
        (CXGate(), [q[1], q[3]], []),
        (TdgGate(), [q[3]], []),
        (CXGate(), [q[0], q[3]], []),
        (TGate(), [q[3]], []),
        (CXGate(), [q[1], q[3]], []),
        (TdgGate(), [q[3]], []),
        (HGate(), [q[3]], []),
        (TGate(), [q[3]], []),
        (CXGate(), [q[2], q[3]], []),
        (TdgGate(), [q[3]], []),
        (HGate(), [q[3]], []),
]:
    def_rc3x.append(inst, qargs, cargs)
_sel.add_equivalence(RC3XGate(), def_rc3x, validate=False)

# C3XGate name conflicts with MCXGate
# # C3XGate

# q = QuantumRegister(4, 'q')
# def_c3x = QuantumCircuit(q)
# for inst, qargs, cargs in [
#         (HGate(), [q[3]], []),
#         (CU1Gate(-pi/4), [q[0], q[3]], []),
#         (HGate(), [q[3]], []),
#         (CXGate(), [q[0], q[1]], []),
#         (HGate(), [q[3]], []),
#         (CU1Gate(pi/4), [q[1], q[3]], []),
#         (HGate(), [q[3]], []),
#         (CXGate(), [q[0], q[1]], []),
#         (HGate(), [q[3]], []),
#         (CU1Gate(-pi/4), [q[1], q[3]], []),
#         (HGate(), [q[3]], []),
#         (CXGate(), [q[1], q[2]], []),
#         (HGate(), [q[3]], []),
#         (CU1Gate(pi/4), [q[2], q[3]], []),
#         (HGate(), [q[3]], []),
#         (CXGate(), [q[0], q[2]], []),
#         (HGate(), [q[3]], []),
#         (CU1Gate(-pi/4), [q[2], q[3]], []),
#         (HGate(), [q[3]], []),
#         (CXGate(), [q[1], q[2]], []),
#         (HGate(), [q[3]], []),
#         (CU1Gate(pi/4), [q[2], q[3]], []),
#         (HGate(), [q[3]], []),
#         (CXGate(), [q[0], q[2]], []),
#         (HGate(), [q[3]], []),
#         (CU1Gate(-pi/4), [q[2], q[3]], []),
#         (HGate(), [q[3]], [])
# ]:
#     def_c3x.append(inst, qargs, cargs)
# _sel.add_equivalence(C3XGate(), def_c3x, validate=False)


# C4XGate name conflicts with MCXGate
# # C4XGate

# q = QuantumRegister(5, 'q')
# def_c4x = QuantumCircuit(q)
# for inst, qargs, cargs in [
#         (HGate(), [q[4]], []),
#         (CU1Gate(-pi / 2), [q[3], q[4]], []),
#         (HGate(), [q[4]], []),
#         (C3XGate(), [q[0], q[1], q[2], q[3]], []),
#         (HGate(), [q[4]], []),
#         (CU1Gate(pi / 2), [q[3], q[4]], []),
#         (HGate(), [q[4]], []),
#         (C3XGate(), [q[0], q[1], q[2], q[3]], []),
#         (C3XGate(pi / 8), [q[0], q[1], q[2], q[4]], []),
# ]:
#     def_c4x.append(inst, qargs, cargs)
# _sel.add_equivalence(C4XGate(), def_c4x, validate=False)

# RXGate

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
def_rx = QuantumCircuit(q)
def_rx.append(RGate(theta, 0), [q[0]], [])
_sel.add_equivalence(RXGate(theta), def_rx, validate=False)

# CRXGate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_crx = QuantumCircuit(q)
for inst, qargs, cargs in [
        (U1Gate(pi / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U3Gate(-theta / 2, 0, 0), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U3Gate(theta / 2, -pi / 2, 0), [q[1]], [])
]:
    def_crx.append(inst, qargs, cargs)
_sel.add_equivalence(CRXGate(theta), def_crx, validate=False)

# RXXGate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_rxx = QuantumCircuit(q)
for inst, qargs, cargs in [
        (HGate(), [q[0]], []),
        (HGate(), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U1Gate(theta), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (HGate(), [q[1]], []),
        (HGate(), [q[0]], []),
]:
    def_rxx.append(inst, qargs, cargs)
_sel.add_equivalence(RXXGate(theta), def_rxx, validate=False)

# RYGate

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
def_ry = QuantumCircuit(q)
def_ry.append(RGate(theta, pi / 2), [q[0]], [])
_sel.add_equivalence(RYGate(theta), def_ry, validate=False)

# CRYGate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_cry = QuantumCircuit(q)
for inst, qargs, cargs in [
        (U3Gate(theta / 2, 0, 0), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U3Gate(-theta / 2, 0, 0), [q[1]], []),
        (CXGate(), [q[0], q[1]], [])
]:
    def_cry.append(inst, qargs, cargs)
_sel.add_equivalence(CRYGate(theta), def_cry, validate=False)

# RYYGate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_ryy = QuantumCircuit(q)
for inst, qargs, cargs in [
        (RXGate(pi / 2), [q[0]], []),
        (RXGate(pi / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (RZGate(theta), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (RXGate(-pi / 2), [q[0]], []),
        (RXGate(-pi / 2), [q[1]], []),
]:
    def_ryy.append(inst, qargs, cargs)
_sel.add_equivalence(RYYGate(theta), def_ryy, validate=False)

# RZGate

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
def_rz = QuantumCircuit(q)
def_rz.append(U1Gate(theta), [q[0]], [])
_sel.add_equivalence(RZGate(theta), def_rz, validate=False)

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
rz_to_rxry = QuantumCircuit(q)
rz_to_rxry.append(RXGate(pi/2), [q[0]], [])
rz_to_rxry.append(RYGate(-theta), [q[0]], [])
rz_to_rxry.append(RXGate(-pi/2), [q[0]], [])
_sel.add_equivalence(RZGate(theta), rz_to_rxry, validate=False)

# CRZGate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_crz = QuantumCircuit(q)
for inst, qargs, cargs in [
        (U1Gate(theta / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U1Gate(-theta / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], [])
]:
    def_crz.append(inst, qargs, cargs)
_sel.add_equivalence(CRZGate(theta), def_crz, validate=False)

# RZZGate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_rzz = QuantumCircuit(q)
for inst, qargs, cargs in [
        (CXGate(), [q[0], q[1]], []),
        (U1Gate(theta), [q[1]], []),
        (CXGate(), [q[0], q[1]], [])
]:
    def_rzz.append(inst, qargs, cargs)
_sel.add_equivalence(RZZGate(theta), def_rzz, validate=False)

# SGate

q = QuantumRegister(1, 'q')
def_s = QuantumCircuit(q)
def_s.append(U1Gate(pi / 2), [q[0]], [])
_sel.add_equivalence(SGate(), def_s, validate=False)

# SdgGate

q = QuantumRegister(1, 'q')
def_sdg = QuantumCircuit(q)
def_sdg.append(U1Gate(-pi / 2), [q[0]], [])
_sel.add_equivalence(SdgGate(), def_sdg, validate=False)

# SwapGate

q = QuantumRegister(2, 'q')
def_swap = QuantumCircuit(q)
for inst, qargs, cargs in [
        (CXGate(), [q[0], q[1]], []),
        (CXGate(), [q[1], q[0]], []),
        (CXGate(), [q[0], q[1]], [])
]:
    def_swap.append(inst, qargs, cargs)
_sel.add_equivalence(SwapGate(), def_swap, validate=False)

# iSwapGate

q = QuantumRegister(2, 'q')
def_iswap = QuantumCircuit(q)
for inst, qargs, cargs in [
        (SGate(), [q[0]], []),
        (SGate(), [q[1]], []),
        (HGate(), [q[0]], []),
        (CXGate(), [q[0], q[1]], []),
        (CXGate(), [q[1], q[0]], []),
        (HGate(), [q[1]], [])
]:
    def_iswap.append(inst, qargs, cargs)
_sel.add_equivalence(iSwapGate(), def_iswap, validate=False)

# DCXGate

q = QuantumRegister(2, 'q')
def_dcx = QuantumCircuit(q)
for inst, qargs, cargs in [
        (CXGate(), [q[0], q[1]], []),
        (CXGate(), [q[1], q[0]], [])
]:
    def_dcx.append(inst, qargs, cargs)
_sel.add_equivalence(DCXGate(), def_dcx, validate=False)

q = QuantumRegister(2, 'q')
dcx_to_iswap = QuantumCircuit(q)
for inst, qargs, cargs in [
        (HGate(), [q[0]], []),
        (SdgGate(), [q[0]], []),
        (SdgGate(), [q[1]], []),
        (iSwapGate(), [q[0], q[1]], []),
        (HGate(), [q[1]], [])
]:
    dcx_to_iswap.append(inst, qargs, cargs)
_sel.add_equivalence(DCXGate(), dcx_to_iswap, validate=False)

# CSwapGate

q = QuantumRegister(3, 'q')
def_cswap = QuantumCircuit(q)
for inst, qargs, cargs in [
        (CXGate(), [q[2], q[1]], []),
        (CCXGate(), [q[0], q[1], q[2]], []),
        (CXGate(), [q[2], q[1]], [])
]:
    def_cswap.append(inst, qargs, cargs)
_sel.add_equivalence(CSwapGate(), def_cswap, validate=False)

# TGate

q = QuantumRegister(1, 'q')
def_t = QuantumCircuit(q)
def_t.append(U1Gate(pi / 4), [q[0]], [])
_sel.add_equivalence(TGate(), def_t, validate=False)

# TdgGate

q = QuantumRegister(1, 'q')
def_tdg = QuantumCircuit(q)
def_tdg.append(U1Gate(-pi / 4), [q[0]], [])
_sel.add_equivalence(TdgGate(), def_tdg, validate=False)

# U1Gate

q = QuantumRegister(1, 'q')
phi = Parameter('phi')
lam = Parameter('lam')
def_u2 = QuantumCircuit(q)
def_u2.append(U3Gate(pi / 2, phi, lam), [q[0]], [])
_sel.add_equivalence(U2Gate(phi, lam), def_u2, validate=False)

# CU1Gate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
def_cu1 = QuantumCircuit(q)
for inst, qargs, cargs in [
        (U1Gate(theta / 2), [q[0]], []),
        (CXGate(), [q[0], q[1]], []),
        (U1Gate(-theta / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U1Gate(theta / 2), [q[1]], [])
]:
    def_cu1.append(inst, qargs, cargs)
_sel.add_equivalence(CU1Gate(theta), def_cu1, validate=False)

# U2Gate

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
def_u1 = QuantumCircuit(q)
def_u1.append(U3Gate(0, 0, theta), [q[0]], [])
_sel.add_equivalence(U1Gate(theta), def_u1, validate=False)

# U3Gate

q = QuantumRegister(1, 'q')
theta = Parameter('theta')
phi = Parameter('phi')
lam = Parameter('lam')
u3_qasm_def = QuantumCircuit(q)
u3_qasm_def.rz(lam, 0)
u3_qasm_def.rx(pi/2, 0)
u3_qasm_def.rz(theta+pi, 0)
u3_qasm_def.rx(pi/2, 0)
u3_qasm_def.rz(phi+3*pi, 0)
_sel.add_equivalence(U3Gate(theta, phi, lam), u3_qasm_def, validate=False)

# CU3Gate

q = QuantumRegister(2, 'q')
theta = Parameter('theta')
phi = Parameter('phi')
lam = Parameter('lam')
def_cu3 = QuantumCircuit(q)
for inst, qargs, cargs in [
        (U1Gate((lam + phi) / 2), [q[0]], []),
        (U1Gate((lam - phi) / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U3Gate(-theta / 2, 0, -(phi + lam) / 2), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (U3Gate(theta / 2, phi, 0), [q[1]], [])
]:
    def_cu3.append(inst, qargs, cargs)
_sel.add_equivalence(CU3Gate(theta, phi, lam), def_cu3, validate=False)

# XGate

q = QuantumRegister(1, 'q')
def_x = QuantumCircuit(q)
def_x.append(U3Gate(pi, 0, pi), [q[0]], [])
_sel.add_equivalence(XGate(), def_x, validate=False)

# CXGate

from qiskit.quantum_info.synthesis.ion_decompose import cnot_rxx_decompose
for plus_ry in [False, True]:
    for plus_rxx in [False, True]:
        cx_to_rxx = cnot_rxx_decompose(plus_ry, plus_rxx)
        _sel.add_equivalence(CXGate(), cx_to_rxx, validate=False)

# CCXGate

q = QuantumRegister(3, 'q')
def_ccx = QuantumCircuit(q)
for inst, qargs, cargs in [
        (HGate(), [q[2]], []),
        (CXGate(), [q[1], q[2]], []),
        (TdgGate(), [q[2]], []),
        (CXGate(), [q[0], q[2]], []),
        (TGate(), [q[2]], []),
        (CXGate(), [q[1], q[2]], []),
        (TdgGate(), [q[2]], []),
        (CXGate(), [q[0], q[2]], []),
        (TGate(), [q[1]], []),
        (TGate(), [q[2]], []),
        (HGate(), [q[2]], []),
        (CXGate(), [q[0], q[1]], []),
        (TGate(), [q[0]], []),
        (TdgGate(), [q[1]], []),
        (CXGate(), [q[0], q[1]], [])
]:
    def_ccx.append(inst, qargs, cargs)
_sel.add_equivalence(CCXGate(), def_ccx, validate=False)

# YGate

q = QuantumRegister(1, 'q')
def_y = QuantumCircuit(q)
def_y.append(U3Gate(pi, pi / 2, pi / 2), [q[0]], [])
_sel.add_equivalence(YGate(), def_y, validate=False)

# CYGate

q = QuantumRegister(2, 'q')
def_cy = QuantumCircuit(q)
for inst, qargs, cargs in [
        (SdgGate(), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (SGate(), [q[1]], [])
]:
    def_cy.append(inst, qargs, cargs)
_sel.add_equivalence(CYGate(), def_cy, validate=False)

# ZGate

q = QuantumRegister(1, 'q')
def_z = QuantumCircuit(q)
def_z.append(U1Gate(pi), [q[0]], [])
_sel.add_equivalence(ZGate(), def_z, validate=False)

# CZGate

q = QuantumRegister(2, 'q')
def_cz = QuantumCircuit(q)
for inst, qargs, cargs in [
        (HGate(), [q[1]], []),
        (CXGate(), [q[0], q[1]], []),
        (HGate(), [q[1]], [])
]:
    def_cz.append(inst, qargs, cargs)
_sel.add_equivalence(CZGate(), def_cz, validate=False)
