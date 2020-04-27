# variational_circuit
Variational quantum circuit module. Provides support to variational circuits on mixed states. Based on [QuTiP](qutip.org)

Three modules are provided:
* `measure`: provides some measures of qubit systems
    * `sep_purity`: measure the purity of subsystems.
    * `fid_ref`: measure the fidelity between the subsystem of a state and a reference state.
    * `c_entropy`: measure the entropy of the output of the measurement in computational basis.
* `vcirc`: provides variational circuit class
    * Create a variational circuit instance with N qubits: `vc = vcirc(N)`
    * Add a layer of ansatz by `vc.add_ansatz(x)`
    * Customized structure can be used `vc.add_ansatz(x,structure=custom_struc)`
    * Define structure as functions:
    ```python
    def custom_struc(parameters,N,inv=False):
        qc = QubitCircuit(N)
        shape = (M,) # desired shape of parameters
        para = parameters.reshape(shape)
        # qc.add_gate(...) ... add quatnum gates ...
        return qc,shape
    ```
* `optimize`: utilize `scipy.optimize` to optimize variational circuits
    * `circ_maximize` and `circ_minimize`:
    ```python
        res = circ_minimize(x0,input_state,circuit,test_function,*args)
    ```
