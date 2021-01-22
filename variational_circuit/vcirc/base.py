import numpy as np

from qutip.qip.circuit import gate_sequence_product,QubitCircuit
from qutip import Qobj
from .structure import regular

class ansatz:
    """
    The class of ansatzs
    
    Parameters
    ----------
        x: list
            The parameters of the ansatz.
        N: int
            Number of qubits.
        structure: func
            The function defining the ansatz
        pos: list
            The positions of the ansatz.
        arg_value: position holder for special ansatzes.
    Attributes
    -------
        N: int
            Number of qubits.
        dims: list
            Dimension list of the ansatz (default [2]*N).
        structure: function
            The function defining the ansatz
        para: list
            The parameters of the ansatz.
        qc: QubitCircuit
            The ansatz with given parameters.
    Functions
    -------
        set_circuit():
            Setup `qc` as `QubitCircuit`.
    """
    def __init__(self,x,N=None,structure=regular,pos=None,**arg_value):
        self.N = N
        if pos is not None:
            if N is not None:
                try:
                    if len(pos) != N:
                        raise ValueError("The list of qubits in `pos` doesn't match the number of qubits `N`.")
                except ValueError as ve:
                    print(ve)
                for i in range(len(pos)):
                    if pos[i]<0 or pos[i]>=N:
                        raise ValueError("The {}th position exceses the ansatz size".formate(i))
            self.N = len(pos)
        self.pos = pos
        self.dims= [2]*self.N
        self.structure = structure
        self.name = (structure.__name__,pos,arg_value)
        self.para  = np.array(x)
        self.arg = arg_value
        self.qc = None                      # generate on demand

    def set_circuit(self):
        self.qc = self.structure(self.para,self.N,**self.arg)
        return self.qc

class vcirc:
    """
    Generate the variational circuit
    
    Parameters
    ----------
        N: int
            The number of qubits in the circuit.
    Attributes
    -------
        N: int
            The number of qubits in the circuit.
        dims: list
            Dimension list of the ansatz (default [2]*N).
        qc: QubitCircuit
            The variational circuit.
        statein: Qobj
            The input state
        stateout: Qobj
            The output state
    """
    def __init__(self,N):
        self.N = N
        self.dims = [2]*self.N
        self.ansatzes = []
        self.structures = []
        self.para = []

        self.qc = None      # Generate circuit on demand

        self.statein = Qobj()
        self.stateout = Qobj()
    
    def add_input(self,statein):
        # TODO: Input on partial system
        if statein.isket or statein.isoper:
            if statein.dims[0] != self.dims:
                raise ValueError("Invalid input state, must be state on {%s} qubits system.".format(N))
        elif statein.isbra:
            if statein.dims[1] != self.dims:
                raise ValueError("Invalid input state, must be state on {%s} qubits system.".format(N))
        else:
            raise ValueError("The input should be a quantum state")
        self.statein = statein

    def compress(self):
        """
        Get the matrix of the variational circuit

        Return
        ------
            Matrix representation of the variational circuit.
        """
        return gate_sequence_product(self.propagators().propagators())

    def apply_to(self,state=None,update=False,inverse=False):
        if state != None:
                statein = state
        else:
            statein = self.statein if not inverse else self.stateout
        if not isinstance(statein,Qobj):
            raise TypeError("Input must be provided,\n{}\nis not a Qobj".format(str(state)))

        stateout = statein
        if not inverse:
            for gate in self.propagators().propagators():
                stateout = stateout.transform(gate,inverse)
        else:
            for gate in reversed(self.propagators().propagators()):
                stateout = stateout.transform(gate,inverse)

        if update:
            self.stateout = stateout if not inverse else statein
            self.statein = statein if not inverse else stateout
        return stateout

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
            self.ansatzes.append(ansatz(x,size,structure,pos,**arg_value))
        else:
            for position in index:
                self.ansatzes.insert(position,ansatz(x,size,structure,pos,**arg_value))
        self.__update_structures()
        self.__update_para()
        self.propagators()

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
        self.__update_structures()
        self.__update_para()
        self.propagators()

    def propagators(self,ansatz_li=None):
        self.qc = QubitCircuit(self.N)
        if ansatz_li is None:
            for ansa in self.ansatzes:
                if ansa.pos is None:
                    self.qc.add_circuit(ansa.set_circuit())
                elif isinstance(ansa.pos,(list,tuple,np.ndarray)):
                    self.qc.add_circuit(self.__permute_circuit(ansa.set_circuit(),ansa.pos))
                else:
                    raise ValueError('The position of ansatz {} is not valid'.format(ansa.name))
        elif isinstance(ansatz_li,(list,tuple,np.ndarray)):
            for pos in ansatz_li:
                temp_ansatz = self.ansatzes[pos]
                if temp_ansatz is None:
                    self.qc.add_circuit(temp_ansatz.set_circuit())
                elif isinstance(temp_ansatz.pos,(list,tuple,np.ndarray)):
                    self.qc.add_circuit(self.__permute_circuit(temp_ansatz.set_circuit(),temp_ansatz.pos))
                else:
                    raise ValueError('The position of ansatz {} is not valid'.format(ansa.name))

        return self.qc
    
    def __update_structures(self):
        self.structures = [ansa.name for ansa in self.ansatzes]
    
    def __update_para(self):
        self.para = [ansa.para for ansa in self.ansatzes]

    def __permute_circuit(self, qc2add, pos=None):
        """
        **Override the add_circuit function in QuTiP**

        Adds a block of a qubit circuit to the main circuit.
        Globalphase gates are not added.

        Parameters
        ----------
        qc : QubitCircuit
            The circuit block to be added to the main circuit.
        pos : list
            The arrangement of qubits.
        """
        if pos is not None:
            temp_qc = QubitCircuit(self.N)
            if max(pos) >= self.N or min(pos) < 0:
                raise NotImplementedError("Qubit allocated outside the circuit")

            for gate in qc2add.gates:
                if gate.targets is not None:
                    temp_tar = [pos[target] for target in gate.targets]
                else:
                    temp_tar = None
                if gate.controls is not None:
                    temp_ctrl = [pos[control] for control in gate.controls]
                else:
                    temp_ctrl = None
                temp_qc.add_gate(gate.name, temp_tar, temp_ctrl,
                                 gate.arg_value,gate.arg_label),
            return temp_qc
        else:
            return qc2add

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
            for ansa in self.ansatzes:
                if isinstance(x_in[head],(list,tuple,np.ndarray)):
                    ansa.para = np.array(x_in[head])
                    head += 1
                else:
                    ansa.para = np.array(x_in[head:head+len(ansa.para)])
                    head += len(ansa.para)
        elif isinstance(ansatz_li,(list,tuple,np.ndarray)):
            for i in ansatz_li:
                if isinstance(x_in[head],np.ndarray):
                    self.ansatzes[i].para = np.array(x_in[head])
                    head += 1
                else:
                    self.ansatzes[i].para = np.array(x_in[head:head+len(self.ansatzes[head].para)])
                    head += len(self.ansatzes[head].para)
        else:
            raise TypeError("ansatz_li must be a list of indexes.")
        self.__update_para()
        self.propagators()