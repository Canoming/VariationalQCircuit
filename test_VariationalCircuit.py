import numpy as np

from variational_circuit.varicirc import *
from variational_circuit.measure import *
from scipy.optimize import minimize
from time import time

from qutip.random_objects import rand_ket
from qutip.qip.qubits import qubit_states
from qutip.tensor import tensor

N = 4 # number of qubits
n = 2 # number of reduced qubits

# Random inputs (qubit state)
Input = rand_ket(2**N,dims=[[2]*N,[1]*N])
# Reference State
r_state = qubit_states(n)

# Set the variational circuit

vc = vcirc(N)
L=2
vc.add_ansatz(np.zeros(N*3)) # add one layer
x0 = np.zeros(N*3*L) # init parameters

vc.update_ansatzes(x0)

print(qcirc_test(Input,vc.qc,[[0,1],[2,3]],sample_size=1000,test_func=dst))
print(qcirc_test(Input,vc.qc,[[0,1],[2,3]],test_func=sep_purity))

#--------------------------------------------------------

print("Test ptest")

vc = vcirc(N)
L=2
vc.add_ansatz(np.zeros(N*3)) # add one layer
x0 = np.zeros(N*3*L) # init parameters

vc.update_ansatzes(x0)

print("ptest(x0):", qcirc_test(Input,vc.qc,[[0,1],[2,3]],test_func=sep_purity))
print("ptest(x0) by sampling:", qcirc_test(Input,vc.qc,[[0,1],[2,3]],1000,test_func=sep_purity_sample))

#--------------------------------------------------------

print("Test qdr_cost on full system")

vc = vcirc(n)
L=2
vc.add_ansatz(np.zeros(n*3)) # add one layer
x0 = np.zeros(n*3*L) # init parameters

state2 = Input.ptrace([2,3])

vc.update_ansatzes(x0)

print("qdr_cost(x0)):", qcirc_test(state2,vc.qc,r_state,test_func=fid_ref))

#----------------------------------------------

print("Test qdr_cost on subsystem")

vc = vcirc(N)
L=2
vc.add_ansatz(np.zeros(N*3)) # add one layer
x0 = np.zeros(N*3*L) # init parameters

vc.update_ansatzes(x0)

print("qdr_cost(x0,ref_sys=[2,3]):",
    qcirc_test(
        Input,vc.qc,
        r_state,[2,3],test_func=fid_ref))

#------------------------

print('the end')