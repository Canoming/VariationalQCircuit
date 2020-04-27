import numpy as np

from qutip.qip.circuit import gate_sequence_product,QubitCircuit
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
        structure: function
            The function defining the ansatz
        arg_value: position holder for special ansatzes.
    Attributes
    -------
        N: int
            Number of qubits.
        dims: list
            Dimension list of the ansatz (default [2]*N).
        structure: function
            The function defining the ansatz
        shape: tuple
            The shape of the parameters.
        para: list
            The parameters of the ansatz.
        qc: QubitCircuit
            The ansatz with given parameters.
        inv_qc: QubitCircuit
            The inverse of ansatz with given parameters.
    Functions
    -------
        set_circuit():
            Setup `qc` as `QubitCircuit`.
        set_inv_circuit():
            Setup `qc` as `QubitCircuit`.
    """
    def __init__(self,x,N,structure=regular,**arg_value):
        self.N = N
        self.dims= [2]*self.N
        self.structure = structure
        self.para  = np.array(x)
        self.arg = arg_value
        
        set_circuit()
        
        self.pare.reshape(self.shape)
        
        self.inv_qc = None # Generate inverse circuits on demand

    def set_circuit(self):
        self.qc,self.shape = self.structure(self.para,self.N,**self.arg)
        return self.qc

    # TODO: rewrite the inverse function in qutip.
    def set_inv_circuit(self):  # It's necessary since the reverse_circuit in qutip doesn't take the inverse of gates but only the order.
        self.inv_qc,self.shape = self.structure(self.para,self.N,**self.arg,inv=True)
        return self.inv_qc

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
        inv_qc: QubitCircuit
            The inverse of the variational cricuit.
        statein: Qobj
            The input state
        stateout: Qobj
            The output state
    """
    def __init__(self,N):
        self.N = N
        self.dims = [2]*self.N
        self.ansatzes = []

        self.qc = None      # Generate circuit on demand
        self.inv_qc = None

        self.statein= None
        self.stateout = None
    
    def add_input(self,statein):
        if (statein.dims[0] != [2]*self.N):
            raise ValueError("Invalid input state, must be state on %s qubits system." % N)
        self.statein = statein
    
    def compress(self):
        """
        Get the matrix of the variational circuit

        Return
        ------
            Matrix representation of the variational circuit.
        """
        return gate_sequence_product(self.propagators().propagators())

    def apply_to(self,statein=None,update=False):
        if statein == None:
            if self.statein == None:
                raise ValueError("Input must be provided")
            else:
                self.stateout = self.statein.transform(self.compress())
                return self.stateout
        else:
            stateout = statein.transform(self.compress())
            if update:
                self.stateout = stateout
                self.statein = statein
        return stateout

    def add_ansatz(self,x,structure=regular,index=None,**arg_value):
        """
        Adds an ansatz to the circuit.

        Parameters
        ----------
            x : list
                The list of parameters for the ansatz.
            ansatz : string
                The name of ansatz
            index: Int
                The position to insert the ansatz. Insert to the end if None.
            arg_value:
                An position holder for special ansatzes.
        """
        if index is None:
            self.ansatzes.append(ansatz(x,self.N,structure,**arg_value))
        else:
            for position in index:
                self.ansatzes.insert(position,ansatz(x,self.N,structure,arg_value))

    def remove_ansatz(self,index=None,end=None,name=None,remove="first"):
        """
        Remove an ansatz from a specific index or between two indexes or the
        first, last or all instances of a particular gate.

        Parameters
        ----------
            index : int
                Location of gate to be removed.
            end : int
                End of range of gates to be removed.
            name : str
                Ansatz name to be removed.
            remove : str
                If first or all gate are to be removed.
        """
        if index is not None and index <= self.N:
            if end is not None and end <= self.N:
                for i in range(end - index):
                    self.ansatzes.pop(index + i)
            elif end is not None and end > self.N:
                raise ValueError("End target exceeds number of ansatzes.")
            else:
                self.ansatzes.pop(index)
        elif name is not None and remove == "first":
            for ansatz in self.ansatzes:
                if name == ansatz.name:
                    self.ansatzes.remove(ansatz)
                    break
        elif name is not None and remove == "last":
            for ansatz in reversed(self.ansatzes):
                if name == ansatz.name:
                    self.ansatzes.remove(ansatz)
                    break
        elif name is not None and remove == "all":
            for ansatz in self.ansatzes:
                if name == ansatz.name:
                    self.ansatzes.remove(ansatz)
        else:
            self.gates.pop()

    def propagators(self):
        self.qc = QubitCircuit(self.N)
        for ansatz in self.ansatzes:
            self.qc.add_circuit(ansatz.set_circuit())
        return self.qc

    def inv_propagators(self):
        self.inv_qc = QubitCircuit(self.N)
        for ansatz in reversed(self.ansatzes):
            self.inv_qc.add_circuit(ansatz.set_inv_circuit())
        return inv_qc

    def update_ansatzes(self,x_in,ansatz_li=None):
        """
        update variational circuit parameters

        Parameters
        ----------
            x_in : list
                list of parameters
        """
        temp_x = np.array(x_in)
        pos = 0
        
        if ansatz_li == None:
            for ansatz in self.ansatzes:
                if isinstance(temp_x[0],np.ndarray):                    
                    ansatz.para = temp_x[0].reshape(ansatz.shape)
                    temp_x = np.delete(temp_x,0,0)
                else:
                    ansatz.para = temp_x[0:ansatz.para.size].reshape(ansatz.shape)
                    temp_x = np.delete(temp_x,np.arange(ansatz.para.size))
        self.propagators()