# %%
from variational_circuit.vcirc import *
from variational_circuit.measure import *
from variational_circuit.optimize import *
from time import time

from qutip.random_objects import rand_ket
from qutip.qip.qubits import qubit_states
from qutip.tensor import tensor

# %% [markdown]
# Three samples that reduce the dimension of a quantum state are given

# %%  Generate random input
N = 4 # number of qubits
n = 2 # number of reduced qubits

# Random inputs (qubit state)
Input = rand_ket(2**N,dims=[[2]*N,[1]*N])
# Input2 = rand_ket(2**N,dims=[[2]*N,[1]*N])
# Input = 0.99*Input*Input.dag() + 0.01*Input2*Input2.dag()  # To add some inpurity

# Reference State
r_state = qubit_states(n)   # 0 state

# %% Reduce the dimension of a quantum state by bring one of the subsystem to 0 state
print("quantum dimensionality reduction")
vc1 = vcirc(N)

for L in np.arange(1,5):    # number of ansatz
    vc1.add_ansatz(np.zeros(N*3)) # add one layer
    t0 = time()
    x0 = np.zeros(N*3*L) # init parameters

    res = circ_maximize(x0,Input,vc1,fid_ref,r_state,[2,3],opt_method='powell')
    print("L=",L,"Result=",res.fun,"Iterated",res.nit,"tiems; running time=",time()-t0,"seconds")
    if 1-res.fun < 1e-5:
        break

out = vc1.apply_to(Input,update=True)

print("result fidelity is",fid_ref(tensor(out.ptrace([0,1]),r_state*r_state.dag()),out))

# %% Reduce the dimension of a quantum state by first disentangle the qubits, and then bring one of the subsystem to 0 state.
print("disentangling")
vc2 = vcirc(N)

for L in np.arange(1,5):    # number of ansatz
    vc2.add_ansatz(np.zeros(N*3)) # add one layer
    t0 = time()
    x0 = np.zeros(N*3*L) # init parameters

    res = circ_maximize(x0,Input,vc1,sep_purity,[[0,1],[2,3]],opt_method='powell')
    print("L=",L,"Result=",res.fun,"Iterated",res.nit,"tiems; running time=",time()-t0,"seconds")
    if 1-res.fun < 1e-5:
        break

print("The second phase")
vc21 = vcirc(n)

out = vc2.apply_to(Input,update=True)
state2 = out.ptrace([2,3])

for L in np.arange(1,5):
    vc21.add_ansatz(np.zeros(n*3)) # add one layer
    t0 = time()
    x0 = np.zeros(n*3*L) # init parameters

    res = circ_maximize(x0,state2,vc21,fid_ref,r_state,opt_method='powell')
    print("L=",L,"Result=",res.fun,"Iterated",res.nit,"tiems; running time=",time()-t0,"seconds")
    if 1-res.fun < 1e-5:
        break

out2 = vc21.apply_to(state2,update=True)
final = tensor(out.ptrace([0,1]),out2)

print("result fidelity is",fid_ref(final,tensor(out.ptrace([0,1]),r_state*r_state.dag())))

# %% Reduce the dimension of a quantum state by minimize the entropy of one of the state.
print("dimensionality reduction with arbitrary classical memory")
vc3 = vcirc(N)

for L in np.arange(1,5):    # number of ansatz
    vc3.add_ansatz(np.zeros(N*3)) # add one layer
    t0 = time()
    x0 = np.zeros(N*3*L) # init parameters

    res = circ_minimize(x0,Input,vc3,c_entropy,[2,3],opt_method='powell')
    print("L=",L,"Result=",res.fun,"Iterated",res.nit,"tiems; running time=",time()-t0,"seconds")
    if res.fun < 1e-5:
        break

out = vc3.apply_to(Input)
conv_ref = out.ptrace([2,3])
print("The ref state is",conv_ref)
print("result fidelity is",fid_ref(tensor(out.ptrace([0,1]),conv_ref),out))
