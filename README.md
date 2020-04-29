# variational_circuit
Variational quantum circuit module. Provides support to variational circuits on mixed states. Based on [QuTiP](qutip.org)

Three sub-modules are provided:
* `measure`: provides some measures of qubit systems
    * `sep_purity`: measure the purity of subsystems.
    * `fid_ref`: measure the fidelity between the subsystem of a state and a reference state.
    * `c_entropy`: measure the entropy of the output of the measurement in computational basis.
    * `dst`: use *destructive swap test* [[10.1103/PhysRevA.87.052330](https://arxiv.org/ct?url=https%3A%2F%2Fdx.doi.org%2F10.1103%2FPhysRevA.87.052330&v=839f8497)] to obtain purity of [sub]systems.
* `vcirc`: provides variational circuit class
    * Create a variational circuit instance with N qubits: `vc = vcirc(N)`
    * Input state can be attached: `vc.add_input(state)`
    * Add a layer of ansatz by `vc.add_ansatz(x)`
        * Customized structure can be used `vc.add_ansatz(x,structure=custom_struc)`
        * Define structure as functions:
            ```python
            def custom_struc(parameters,N):
                qc = QubitCircuit(N)
                # qc.add_gate(...) ... add quatnum gates ...
                return qc
            ```
    * Evaluation is simple: `vc.apply_to(state)`
* `optimize`: utilize `scipy.optimize` to optimize variational circuits
    * `circ_maximize` and `circ_minimize`:
        ```python
            res = circ_minimize(x0,input_state,vcircuit,test_function,*args)
        ```
