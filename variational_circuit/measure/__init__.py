from qutip.qip.operations.gates import gate_sequence_product

from variational_circuit.measure.measure_sample import dst
from variational_circuit.measure.measure_sim import sep_purity, fid_ref, c_entropy

def qcirc_test(statein,circuit,*args,test_func=sep_purity,**kwargs):
    N = circuit.N
    if (statein.dims[0] != [2]*N) and (statein.dims[1] != [2]*N):
        raise ValueError("Invalid input state, must be state on %s qubits system." % N)
    prop = gate_sequence_product(circuit.propagators())

    stateout = statein.transform(prop)
    if args:
        if kwargs:
            return test_func(stateout,*args,**kwargs),stateout
        else:
            return test_func(stateout,*args),stateout
    else:
        if kwargs:
            return test_func(stateout,**kwargs),stateout
        else:
            return test_func(stateout),stateout