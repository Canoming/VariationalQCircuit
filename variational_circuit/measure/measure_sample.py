import numpy as np

from qutip import Qobj, state_index_number, state_number_index
from qutip.qip.operations.gates import gate_sequence_product
from qutip.qip.circuit import QubitCircuit
from qutip.qip.qubits import qubit_states
from qutip.tensor import tensor

############ Circuit ##################

def postcirc_bell(N):
    qc = QubitCircuit(N*2)
    for i in range(N):
        qc.add_gate("CNOT",i+N,i)
        qc.add_gate("SNOT",i)
    return qc

def precirc_bell(N):
    qc = QubitCircuit(N*2)
    for i in range(N):
        qc.add_gate("SNOT",i)
        qc.add_gate("CNOT",i+N,i)
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
        raise ValueError("Invalid input state.")
    return prob

def dst_measurement(state,sample_size=1):
    """destructive swap test"""
    N = len(state.dims[0])

    statein = tensor(state,state)
    stateout = statein.transform(gate_sequence_product(postcirc_bell(N).propagators()))

    prob = com_measure(stateout)
    dst = np.random.choice(4**N,sample_size,p=prob)
    mresult = [state_index_number(stateout.dims[0],result) for result in dst]
    return mresult # raw output

def hst_measurement(state,qcircuit,sample_size=1):
    """Hilbert-Schmidt test"""
    N = len(state.dims[0])
    qc = QubitCircuit(N*2)
    qc.add_circuit(qcircuit)

    if state.isket:
        statein = tensor(state,qubit_states(N))
    elif state.isbra:
        statein = tensor(state,qubit_states(N).dag())
    elif state.isoper:
        statein = tensor(state,ket2dm(qubit_states(N)))
    state_preps = statein.transform(gate_sequence_product(precirc_bell(N).propagators()))
    state_out = state_preps.transform(gate_sequence_product(qc.propagators()))
    state_postps = state_out.transform(gate_sequence_product(postcirc_bell(N).propagators()))

    prob = com_measure(state_postps)
    hst = np.random.choice(4**N,sample_size,p=prob)
    mresult = [state_index_number(state_postps.dims[0],result) for result in hst]
    return mresult # raw output

############ Post process ##################

def dst_postps(samples,parti=None):
    N = len(samples) # number of samples
    parity = np.zeros(N)
    n = len(samples[0])//2
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
    purity = dst_postps(sample,parti)
    return purity

def hst(state,qc,sample_size=1):
    sample = hst_measurement(state,qc,sample_size)
    dist = sample.count(0)/len(sample)
    return dist