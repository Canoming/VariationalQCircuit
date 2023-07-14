import numpy as np
from collections.abc import Iterable

from qutip.metrics import fidelity
from qutip.qip.circuit import CircuitSimulator, QubitCircuit
from qutip import Qobj
from scipy.stats import entropy


def com_measure(state, sel=None):
    """
    Measurement in computational basis
    """
    if not isinstance(state, Qobj):
        raise TypeError("Input must be a Qobj")

    if state.type == "ket" or state.type == "oper":
        if isinstance(sel,Iterable):
            N = len(sel)
            subsystem = sel
        else:
            N = len(state.dims[0])
            subsystem = list(range(N))
        qc = QubitCircuit(N,num_cbits=N)
        for i in range(N):
            qc.add_measurement('M{}'.format(i),[i],classical_store=i)

        sim = CircuitSimulator(qc)
        return sim.run_statistics(state.ptrace(subsystem)).get_probabilities()
    else:
        raise ValueError("Invalid input state.")

############ Test Functions ##################

def sep_purity(state,parti=None):
    """Purity of the disentangled system"""
    if parti == None:
        return state.purity()
    purity = 1
    for part in parti:
        purity = purity*state.ptrace(part).purity()
    return purity

def c_entropy(state,target=None,log_base=2):
    """Entropy of the computational basis output"""
    if target!=None:
        state = state.ptrace(target)
    return entropy(com_measure(state),base=log_base)

def fid_ref(state,r_state,ref_sys=None):
    """The fidelity between subsystem and the reference state"""
    if ref_sys != None:
        n = len(ref_sys)
    else:
        n = len(state.dims[0])
    if (r_state.dims[0] != [2]*n) and (r_state.dims[1] != [2]*n):
        raise ValueError("Invalid reference state, must be state on %s qubits system." % n)
    state_test = state
    if ref_sys != None:
        state_test = state.ptrace(ref_sys)
    fid = fidelity(state_test,r_state)
    return fid