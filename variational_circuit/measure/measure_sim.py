import numpy as np

from qutip.metrics import fidelity
from scipy.stats import entropy

############ Test Functions ##################

def sep_purity(state,parti=None):
    """Purity of the disentangled system"""
    if parti == None:
        return state.purity()
    purity = 1
    for part in parti:
        purity = purity*state.ptrace(part).purity()
    return purity

def c_entropy(state,target=None):
    """Entropy of the computational basis output"""
    if target!=None:
        state = state.ptrace(target)
    if state.type == "oper":
        diag = state.diag()
        return entropy(diag,base=2)
    return 0

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