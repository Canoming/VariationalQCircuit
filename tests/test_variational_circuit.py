import pytest

from variational_circuit.measure import *

from qutip.states import bell_state
from qutip.qip.qubits import qubit_states
from qutip.metrics import fidelity

zero_state = qubit_states(2)
zero_qubit = qubit_states(1)
bell = bell_state()

def test_sep_purity():
    # print('ptest =', sep_purity(bell))
    assert sep_purity(bell) == bell.purity()
def test_sep_purity2():
    # print('ptest [[0],[1]] =', sep_purity(bell,[[0],[1]]))
    assert sep_purity(bell,[[0],[1]]) == bell.ptrace([0]).purity() * bell.ptrace([1]).purity()

def test_fid_ref():
    print('fid_ref =', fid_ref(bell,zero_state))
    assert fid_ref(bell,zero_state) == fidelity(bell,zero_state)
def test_fid_ref2():
    print('fid_ref [0] =', fid_ref(bell,zero_qubit,[0]))
    assert fid_ref(bell,zero_qubit,[0]) == fidelity(bell.ptrace([0]),zero_qubit)

@pytest.mark.random
def test_dst():
    print('dst =', dst(bell, sample_size=10**5))
    assert dst(bell, sample_size=10**5) == pytest.approx(bell.purity(),0.05)
@pytest.mark.random
def test_dst():
    print('dst =', dst(bell, [[0],[1]], sample_size=10**5))
    assert dst(bell, [[0],[1]], sample_size=10**5) == pytest.approx(bell.ptrace([0]).purity()*bell.ptrace([1]).purity(),0.05)