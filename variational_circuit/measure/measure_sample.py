import numpy as np

from ..bitfunc import inner

from qutip import Qobj, state_index_number, state_number_index
from qutip.qip.operations.gates import gate_sequence_product
from qutip.qip.circuit import QubitCircuit
from qutip.qip.qubits import qubit_states
from qutip.tensor import tensor

############ Circuit ##################

def bell_prep(N,post_proc = False):
    qc = QubitCircuit(N*2)
    if post_proc == False:
        iterator = range(N)
    else:
        iterator = reversed(range(N))
    for i in iterator:
        qc.add_gate("CNOT",i+N,i)
        qc.add_gate("SNOT",i)
    return qc

############ Measurements ##################

def com_measure(state):
    """
    Measurement in computational basis
    """
    if not isinstance(state,Qobj):
        raise TypeError("Input must be a Qobj")
    if state.type == "ket" or state.type == "bra":
        prob = np.abs(state.full().flatten())**2
    elif state.type == "oper":
        prob = np.abs(state.diag())
    else:
        raise ValueError("Invalid input state.")
    return prob

def dst_measurement(state1,state2,sample_size=1):
    """destructive swap test"""
    N = len(state1.dims[0])
    if len(state2.dims[0]) != N:
        raise ValueError("Dimensions of states dismatch.")

    statein = tensor(state1,state2)
    stateout = statein.transform(gate_sequence_product(bell_prep(N,True).propagators()))

    prob = com_measure(stateout)
    result_in_number = np.random.choice(4**N,sample_size,p=prob)
    mresult = [state_index_number(stateout.dims[0],result) for result in result_in_number]
    return mresult # raw output

def hst_measurement(state: Qobj,qcircuit,sample_size=1):
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
    state_preps = statein.transform(gate_sequence_product(bell_prep(N,True).propagators()))
    state_out = state_preps.transform(gate_sequence_product(qc.propagators()))
    state_postps = state_out.transform(gate_sequence_product(bell_prep(N).propagators()))

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
            parity[i] = 1-2*inner(samples[i][0:n],samples[i][n:2*n])  # Inner product. Convert bit to +-1
        return parity.sum()/N
    purity = 1
    for part in parti:
        for i in range(N):
            parity[i] = 1-2*([samples[i][k] & samples[i][k+n] for k in part].count(True)%2)
        purity = purity*parity.sum()/N
    return purity

############ Test Function ##################

def dst(state1: Qobj,state2: Qobj,parti: "list of partitions" =None,sample_size=1):
    sample = dst_measurement(state1,state2,sample_size)
    purity = dst_postps(sample,parti)
    return purity

def dst_source(pre_ps: callable,parti: "list of partitions" =None,sample_size=1,args=()):
    sample = []
    for _ in range(sample_size):
        state1 = pre_ps(args)
        state2 = pre_ps(args)
        sample += dst_measurement(state1,state2)
    purity = dst_postps(sample,parti)
    return purity

def hst(state,qc,sample_size=1):
    sample = hst_measurement(state,qc,sample_size)
    dist = sample.count(0)/len(sample)
    return dist