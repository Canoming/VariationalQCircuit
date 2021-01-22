import pytest

import numpy as np

from variational_circuit.measure import *
from variational_circuit.vcirc import *

from qutip.states import bell_state
from qutip.qip.qubits import qubit_states
from qutip.metrics import fidelity

zero_state = qubit_states(2)
zero_qubit = qubit_states(1)
bell = bell_state()

vc = vcirc(2)

def test_add_ansatz():
    vc.add_ansatz([0,0,0,0,0,0])
    vc.add_ansatz([0,0,0,0,0,0])

    assert vc.structures == [('regular', None, {}), ('regular', None, {})]
    assert (vc.ansatzes[0].para == np.array([0,0,0,0,0,0])).all()
    assert (vc.ansatzes[1].para == np.array([0,0,0,0,0,0])).all()

def test_update_circuit():
    vc.update_ansatzes([1,1,1,1,1,1,1,1,1,1,1,1])
    assert (vc.ansatzes[0].para == np.array([1,1,1,1,1,1])).all()
    assert (vc.ansatzes[1].para == np.array([1,1,1,1,1,1])).all()
    vc.update_ansatzes([[2,2,2,2,2,2],[2,2,2,2,2,2]])
    assert (vc.ansatzes[0].para == np.array([2,2,2,2,2,2])).all()
    assert (vc.ansatzes[1].para == np.array([2,2,2,2,2,2])).all()
    vc.update_ansatzes([3,3,3,3,3,3],[1])
    assert (vc.ansatzes[0].para == np.array([2,2,2,2,2,2])).all()
    assert (vc.ansatzes[1].para == np.array([3,3,3,3,3,3])).all()

def test_sep_purity():
    assert sep_purity(bell) == bell.purity()
    assert sep_purity(bell,[[0],[1]]) == bell.ptrace([0]).purity() * bell.ptrace([1]).purity()

def test_fid_ref():
    assert fid_ref(bell,zero_state) == fidelity(bell,zero_state)
    assert fid_ref(bell,zero_qubit,[0]) == fidelity(bell.ptrace([0]),zero_qubit)

@pytest.mark.random
def test_dst():
    assert dst(bell,bell, sample_size=10**5) == pytest.approx(bell.purity(),0.05)
    assert dst(bell,bell, [[0],[1]], sample_size=10**5) == pytest.approx(bell.ptrace([0]).purity()*bell.ptrace([1]).purity(),0.05)