import numpy as np
from qutip.qobj import Qobj
from qutip.qip.operations.gates import gate_sequence_product
from qutip.metrics import fidelity

def sep_purity(state,parti=None):
    """Purity of the disentangled system"""
    if parti = None
        N = len(state.dims[0])
        parti = [np.arange(N//2),np.arange(N//2,N)]
        print("Partition is",parti)
    pur1 = state.ptrace(parti[0]).purity()
    pur2 = state.ptrace(parti[1]).purity()
    purity = pur1*pur2
    return purity

def ptest(statein,circuit,parti=None):
    """
    Purity test of state

    Parameters
    ----------
    statein: Qobj
        The input state, can be ket, bra or density operator.
    circuit: QubitCircuit
        Target circuit
    parti : list
        The partiion of the system, which defines how the states are disentangled.
    """
    N = circuit.N
    if (statein.dims[0] != [2]*N) and (statein.dims[1] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)
    prop = gate_sequence_product(circuit.propagators())
    if statein.type == "oper":
        stateout = prop*statein*prop.dag()
    elif statein.type == "ket":
        stateout = prop*statein
    elif statein.type == "bra":
        stateout = statein*prop.dag()
    else:
        raise ValueError("Invalid input state")
    return statein.purity()-sep_purity(stateout,parti)

def fid_ref(state,r_state,ref_sys=None):
    """The fidelity between subsystem and the reference state"""
    if ref_sys != None:
        state_test = state.ptrace(ref_sys)
    fid = fidelity(state_test,r_state)
    return fid

def qdr_cost(statein,r_state,circuit,ref_sys=None):
    """
    Cost function for Quantum Dimensionality Reduction

    Parameters
    ----------
    statein: Qobj
        The input state, can be ket, bra or density operator.
    r_state: Qobj
        The reference state, can be ket, bra or density operator.
    circuit: QubitCircuit
        Target circuit
    residue_sys: list
        The subsystem, which need to be measured with state
    """
    N = circuit.N
    # Dimension Check
    if (statein.dims[0] != [2]*N) and (statein.dims[1] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)
    n = len(ref_sys)
    if (r_state.dims[0] != [2]*n) and (r_state.dims[1] != [2]*n):
        raise ValueError("Invalid reference state, must be state on %s qubits system." % n)
    prop = gate_sequence_product(circuit.propagators())

    if statein.type == "oper":
        stateout = prop*statein*prop.dag()
    elif statein.type == "ket":
        stateout = prop*statein
    elif statein.type == "bra":
        stateout = statein*prop.dag()
    else:
        raise ValueError("Invalid input state")
        
    return 1-fid_ref(stateout,r_state,ref_sys)
