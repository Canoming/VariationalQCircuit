import numpy as np

from qutip import Qobj
from qutip.qip.operations.gates import gate_sequence_product
from qutip.qip.circuit import QubitCircuit
from qutip.tensor import tensor

from ..bitfunc import BitVec,inner

############ Circuit ##################

def dst_circ(N):
    qc = QubitCircuit(N*2)
    for i in range(N):
        qc.add_gate("CNOT",i+N,i)
        qc.add_gate("SNOT",i)
    return qc

############ Measurements ##################

def com_measure(state):
    """
    Measurement in computational basis
    """
    if state.type == "ket" or state.type == "bra":
        prob = np.abs(state.full().flatten())**2
    elif state.type == "oper":
        prob = state.diag()
    else:
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)
    return prob

def dst_measurement(state,sample_size=1,prob_out=False):
    """destructive swap test"""
    N = len(state.dims[0])
    # Random output
    statein = tensor(state,state)
    stateout = statein.transform(gate_sequence_product(dst_circ(N).propagators()))

    prob = com_measure(stateout)
    if prob_out:
        return prob
    dst = np.random.choice(4**N,sample_size,p=prob)
    mresult= [BitVec(uint= result,length=N*2) for result in dst]
    return mresult # raw output

############ Post process ##################

def dst_postp(samples,parti=None):
    N = len(samples) # number of samples
    parity = np.zeros(N)
    n = samples[0].len//2
    if parti == None:
        for i in range(N):
            parity[i] = 1-2*inner(samples[i][0:n],samples[i][n:2*n]).int  # Inner product. Convert bit to +-1
        return parity.sum()/N
    purity = 1
    for part in parti:
        for i in range(N):
            parity[i] = 1-2*([samples[i][k] & samples[i][k+n] for k in part].count(True)%2)
        purity = purity*parity.sum()/N
    return purity

############ Test Function ##################

def dst(state,parti=None,sample_size=1):
    sample = dst_measurement(state,sample_size)
    purity = dst_postp(sample,parti)
    return purity