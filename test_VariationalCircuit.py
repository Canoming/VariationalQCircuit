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

#--------------------------------------------------------

print("Test ptest")

vc = vcirc(N)
L=2
vc.add_ansatz(np.zeros(N*3)) # add one layer
x0 = np.zeros(N*3*L) # init parameters

vc.update_ansatzes(x0)

print("ptest(x0):", ptest(Input,vc.qc,parti=[[0,1],[2,3]]))

#--------------------------------------------------------

print("Test qdr_cost on full system")

vc = vcirc(n)
L=2
vc.add_ansatz(np.zeros(n*3)) # add one layer
x0 = np.zeros(n*3*L) # init parameters

state2 = Input.ptrace([2,3])

vc.update_ansatzes(x0)

print("qdr_cost(x0)):",qdr_cost(state2,r_state,vc.qc))

#----------------------------------------------

print("Test qdr_cost on subsystem")

vc = vcirc(N)
L=2
vc.add_ansatz(np.zeros(N*3)) # add one layer
x0 = np.zeros(N*3*L) # init parameters

vc.update_ansatzes(x0)

print("qdr_cost(x0,ref_sys=[2,3]):",qdr_cost(Input,r_state,vc.qc,ref_sys=[2,3]))

#------------------------

print('the end')