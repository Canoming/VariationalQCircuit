import numpy as np

import warnings
from qutip.qip.circuit import QubitCircuit,CircuitSimulator, _para_gates, Gate, Measurement
from qutip import Qobj
from .structure import regular

class Ansatz(QubitCircuit):
    """
    The class of ansatzs
    
    Parameters
    ----------
    x: list
        The parameters of the ansatz.
    N: int
        Number of qubits.
    user_gates: dict
        Self defined gates
    dims: list
        A list of integer for the dimension of each composite system.
        e.g [2,2,2,2,2] for 5 qubits system. If None, qubits system
        will be the default option.
    num_cbits : int
        Number of classical bits in the system.
    structure: method
        The function defining the ansatz
    arg_value: dict
        position holder for special ansatzes.
    """
    def __init__(self, x, N:int, user_gates:dict = None,
            dims:list = None, num_cbits:int = 0,structure = regular,
            pos:list = None, **arg_value):
        
        QubitCircuit.__init__(self, N, user_gates = user_gates,
            dims = dims, num_cbits = num_cbits)

        self.arg = arg_value
        self.paras  = np.array(x)

        self.sim = None     # Generate on demand

        self.__updated = False # generate unitary only if necessary
        self.__result = None   # Initialize the result

        if pos is None:
            self.pos = list(range(N))
        else:
            self.pos = pos

        self.structure = structure
        self.structure(self)

    @property
    def info(self) -> str:
        """
        Get the information
        """
        return f"(structure: {self.structure.__name__}, size: {self.N}, \
positions: {self.pos}, arguments: {self.arg})"

    def _sync_para(self):
        paras = []
        for gate in self.gates:
            if gate.name in _para_gates:
                if gate.arg_value is None:
                    raise ValueError(f"The parameter of the gate {gate.name} \
                        is missing.")
                else:
                    paras.append(gate.arg_value)
            elif gate.name in self.user_gates:
                if gate.arg_value is not None:
                    paras.append(gate.arg_value)
            else:
                if gate.arg_value is not None:
                    gate.arg_value = None
                    warnings.warn(f"The parameter of the gate {gate.name} \
                        is deleted.")
        
        self.paras = np.array(paras)

    def update(self, x = None, gate_li:list = None):
        """
        Update the parameters of the ansatz.

        Parameters
        ----------
        x: array
            The new parameters.
        gate_li: list
            The index of the gates to be updated.
        """

        head = 0

        if x is not None:
            if gate_li is None:
                # Check length
                if len(x) != len(self.paras):
                    raise ValueError(f"{len(self.paras)} parameters are \
required, but {len(x)} are provided.")

                self.paras = np.array(x[0:len(self.paras)])       # update parameters

                for i, gate in enumerate(self.gates):
                    if isinstance(gate,Gate) and gate.arg_value is not None:
                        try:
                            gate.arg_value = self.paras[head]
                            head += 1
                        except IndexError:
                            raise ValueError(f"run out of parameters at gate {i}")

            elif isinstance(gate_li,(list,tuple,np.ndarray)):
                # Check length
                if len(x) != len(gate_li):
                    raise ValueError("The number of parameters does not match the list of gates.")

                for i in gate_li:
                    if self.gates[i].arg_value is not None:
                        try:
                            self.gates[i].arg_value = x[head]
                            head += 1
                        except IndexError:
                            raise ValueError(f"run out of parameters at gate {i}")
                self._sync_para()
        else:
            self._sync_para()
        
        self.__updated = True

    @property
    def unitary(self) -> list:
        if not self.__updated:
            return self.compress()
        else:
            return self.sim.ops

    @property
    def result(self):
        if not self.__updated:
            self.compress()
            
        return self.__result

    def compress(self) -> list:
        """
        Get the matrix of the ansatz

        Return
        ------
            Matrix representation of the ansatz.
        """
        self.sim = CircuitSimulator(self, state=None, precompute_unitary=True)
        self.__updated = True

        return self.sim.ops

class Vcirc(QubitCircuit):
    """
    Generate the variational circuit
    
    Parameters
    ----------
        N: int
            The number of qubits in the circuit.
        dims: list
            Dimension list of the ansatz (default [2]*N).
        qc: QubitCircuit
            The variational circuit.
        statein: Qobj
            The input state.
        result: CircuitResult
            The result of the previous run.
    """
    def __init__(self, N:int, user_gates:dict = None,
            dims:list = None, num_cbits:int = 0):

        QubitCircuit.__init__(self, N, user_gates = user_gates,
                dims = dims, num_cbits = num_cbits)

        self.ansatzes = []

        self.sim = None     # Generate on demand

        self.__updated = False # generate unitary only if necessary
        self.__result = None   # Initialize the result

        self.statein = None    # Initialize the input state
    
    def add_input(self, statein:Qobj):
        # TODO: Input on partial system
        if statein.isket or statein.isoper:
            if statein.dims[0] != self.dims:
                raise ValueError("Invalid input state, must be a state on \
                    {%s} qubits system.".format(self.N))
        elif statein.isbra:
            if statein.dims[1] != self.dims:
                raise ValueError("Invalid input state, must be state on \
                    {%s} qubits system.".format(self.N))
        else:
            raise ValueError("The input should be a quantum state")
        self.statein = statein
        self.__updated = False  # Reset the flag

    @property
    def info(self):
        return [ansa.info for ansa in self.ansatzes]

    @property
    def paras(self):
        return [ansa.paras for ansa in self.ansatzes]

    @property
    def unitary(self) -> list:
        if not self.__updated:
            return self.compress()
        else:
            return self.sim.ops

    @property
    def result(self):
        if not self.__updated:
            self.compress()
            
        return self.__result

    def compress(self,ansatz_li:list = []) -> list:
        """
        Get the matrix of the variational circuit

        Return
        ------
            Matrix representation of the variational circuit.
        """
        if len(ansatz_li) == 0:
            self.gates = []
            for ansatz in self.ansatzes:
                self.add_circuit(self.__permute_circuit(ansatz,ansatz.pos))
            self.sim = CircuitSimulator(self, state=self.statein, precompute_unitary=True)
            self.__updated = True

            return self.sim.ops
        else:
            return [self.ansatzes[i].compress()[0] for i in ansatz_li]

    def apply_to(self,statein:Qobj = None,stat:bool = False):
        """
        Apply the circuit to a state.
        Return the quantum state if `stat` is `False` and return the ensemble
        of the computational basis measurements is `stat` is `True`.
        """
        if not self.__updated:
            self.compress()

        if statein != None:
                self.sim.initialize(state=statein)
        
        if stat:
            self.__result = self.sim.run_statistics(statein)
        else:
            self.__result = self.sim.run(statein)

        return self.__result.get_final_states()[0]

    def add_ansatz(self,x,structure=regular,pos=None,index=None,**arg_value):
        """
        Adds an ansatz to the circuit.

        Parameters
        ----------
            x : list
                The list of parameters for the ansatz.
            structure: func
                The function defining the ansatz.
            pos: list
                The position of the ansatz. If `None`, assume the same size
                as the circuit in natural order.
            index: int
                The position to insert the ansatz. Insert to the end if `None`.
            arg_value:
                An position holder for special ansatzes.
        """
        if pos is None:
            size = self.N
        else:
            size = len(pos)
        if index is None:
            self.ansatzes.append(Ansatz(x, size, structure=structure,
            pos=pos, **arg_value))
        else:
            for position in index:
                self.ansatzes.insert(position,Ansatz(x, size,
                structure=structure, pos=pos,**arg_value))
        self.__updated = False

    def remove_ansatz(self,index=None,end=None,name=None,remove="first"):
        """
        Remove an ansatz from a specific index or between two indexes or the
        first, last or all instances of a particular gate.

        Parameters
        ----------
            index : int
                Location of ansatz to be removed.
            end : int
                End of range of ansatz to be removed.
            name : str
                Ansatz name to be removed.
            remove : str
                Remove the
                1. first
                2. last
                3. all
        """
        if index is not None:
            if index > self.N:
                raise ValueError("Index exceeds number of ansatzes.")
            if end is not None:
                if end <= self.N:
                    for i in range(end - index):
                        self.ansatzes.pop(index + i)
                else:
                    raise ValueError("End target exceeds number of ansatzes.")
            else:
                self.ansatzes.pop(index)
        elif name is not None and remove == "first":
            for i in range(len(self.ansatzes)):
                if name == self.ansatzes[i].name[0]:
                    self.ansatzes.pop(i)
                    break
        elif name is not None and remove == "last":
            for i in reversed(range(len(self.ansatzes))):
                if name == self.ansatzes[self.N-i].name[0]:
                    self.ansatzes.pop(i)
                    break
        elif name is not None and remove == "all":
            for i in reversed(range(len(self.ansatzes))):
                if name == self.ansatzes[i].name[0]:
                    self.ansatzes.pop(i)
        else:
            self.ansatzes.pop()
        self.__updated = False

    def update_ansatzes(self,x_in,ansatz_li=None):
        """
        Update variational circuit parameters

        Parameters
        ----------
            x_in : list
                list of parameters.
            ansatz_li: list
                list of index of the ansatzs to be updated.
        """
        head = 0
        
        if ansatz_li == None:
            for i,ansa in enumerate(self.ansatzes):
                try:
                    if len(ansa.paras) == 0: # skip empty ansatzes
                        continue
                    if isinstance(x_in[head],(list,tuple,np.ndarray)):
                        ansa.update(x_in[head])
                        head += 1
                    else:
                        ansa.update(np.array(x_in[head:head+len(ansa.paras)]))
                        head += len(ansa.paras)
                except IndexError:
                    raise ValueError('run out of parameters at ansatz {}'.format(i))
        elif isinstance(ansatz_li,(list,tuple,np.ndarray)):
            for i in ansatz_li:
                if isinstance(x_in[head],(list,tuple,np.ndarray)):
                    self.ansatzes[i].update(np.array(x_in[head]))
                    head += 1
                else:
                    self.ansatzes[i].update(np.array(x_in[head:head+len(self.ansatzes[i].paras)]))
                    head += len(self.ansatzes[i].paras)
        else:
            raise TypeError("ansatz_li must be a list of indexes.")
        self.__updated = False
    
    # FIXME: Override the add_circuit function in QubitCircuit
    def __permute_circuit(self, qc2add:QubitCircuit, pos=None) -> QubitCircuit:
        """
        Adds a block of a qubit circuit to the main circuit.
        Globalphase gates are not added.

        Parameters
        ----------
        qc2add : QubitCircuit
            The circuit block to be added to the main circuit.
        pos : list
            The arrangement of qubits.
        """
        if pos is None:        # For default positions, add the circuit directly
            return qc2add
        
        if max(pos) >= self.N or min(pos) < 0:
            raise IndexError("Qubit allocated outside the circuit")
            
        temp_qc = QubitCircuit(self.N)

        for op in qc2add.gates:
            if op.targets is not None:
                temp_tar = [pos[target] for target in op.targets]
            else:
                temp_tar = None

            if isinstance(op, Gate):
                if op.controls is not None:
                    temp_ctrl = [pos[control] for control in op.controls]
                else:
                    temp_ctrl = None
                temp_qc.add_gate(op.name, temp_tar, temp_ctrl,
                                 op.arg_value,op.arg_label)
            elif isinstance(op, Measurement):
                self.add_measurement(
                    op.name, temp_tar,
                    classical_store=op.classical_store)
            else:
                raise TypeError("The circuit to be added contains unknown \
                    operator {}".format(op))
        return temp_qc