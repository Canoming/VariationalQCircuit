import numpy as np

from qutip.qip.circuit import *

class Ansatz:
    """
    The class of ansatzs
    
    Parameters
    ----------
        x: list
            The parameters of the ansatz.
        N: int
            Number of qubits.
        ansatz: string
            The name of ansatz.
        arg_value:
            An position holder for special ansatzes.
    Attributes
    -------
        N: int
            Number of qubits.
        dims: list
            Dimension list of the ansatz (default [2]*N).
        name: string
            The name of the ansatz.
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
    def __init__(self,x,N,ansatz="regular",**arg_value):
        self.N = N
        self.dims= [2]*self.N
        self.name = ansatz
        self.shape = None

        self.qc = None    # Generate circuits on demand
        self.inv_qc = None
        
        if self.name == "regular":
            self.shape = (N,3)
        elif self.name == "CNN4_1":
            self.shape = (N,3)
        elif self.name == "CNN4_2":
            self.shape = (N,3)
        elif arg_value != None:
            try:
                self.shape = arg_value['shape']
            except KeyError:
                raise ValueError("arg 'shape' need to be provided for ansatz: %s" % ansatz)
        else:
            raise ValueError("Unkown ansatz: %s" % ansatz)
        
        self.para  = np.array(x).reshape(self.shape)
        self.arg = arg_value

    def set_circuit(self):
        self.qc = QubitCircuit(self.N)
        if self.name == "regular":
            i = 0
            for angles in self.para:
                self.qc.add_gate("RZ", i, None, angles[0])
                self.qc.add_gate("RX", i, None, angles[1])
                self.qc.add_gate("RZ", i, None, angles[2])
                i+=1
            for j in range(self.N-1):
                self.qc.add_gate("CNOT",j,j+1)
        elif self.name == "CNN4_1":
            i = 0
            for angles in self.para:
                self.qc.add_gate("RZ", i, None, angles[0])
                self.qc.add_gate("RX", i, None, angles[1])
                self.qc.add_gate("RZ", i, None, angles[2])
                i+=1
            for j in range(self.N-1):
                if j //2 == 0:
                    self.qc.add_gate("CNOT",j,j+1)
        elif self.name == "CNN4_2":
            i = 0
            for angles in self.para:
                self.qc.add_gate("RZ", i, None, angles[0])
                self.qc.add_gate("RX", i, None, angles[1])
                self.qc.add_gate("RZ", i, None, angles[2])
                i+=1
            for j in range(self.N-1):
                if j <2:
                    self.qc.add_gate("CNOT",j,j+2)
        elif self.arg != None:
            try:
                self.qc = self.arg['structure'](self.para)
            except KeyError:
                raise ValueError("arg 'structure' need to be provided for ansatz: %s" % ansatz)
        else:
            raise ValueError("Unkown ansatz: %s" % ansatz)
        return self.qc

    def set_inv_circuit(self):  # It's necessary since the reverse_circuit in qutip didn't take the inverse of gates.
        self.inv_qc = QubitCircuit(self.N)
        if self.name == "regular":
            for j in reversed(range(self.N-1)): # CNOT in inverses order
                self.inv_qc.add_gate("CNOT",j,j+1)
            i = 0
            for angles in reversed(self.para):
                self.inv_qc.add_gate("RZ", i, None, -angles[2])
                self.inv_qc.add_gate("RZ", i, None, -angles[1])
                self.inv_qc.add_gate("RX", i, None, -angles[0])
                i+=1
            return self.inv_qc
        else:
            raise ValueError("Unkown ansatz: %s" % ansatz)

class vcirc:
    """
    Generate the variational circuit

    Parameters
    ----------
        N: int
            The number of qubits in the circuit.
    Return
    ------
        qc: QubitCircuit
    """
    def __init__(self,N):
        self.N = N
        self.dims = [2]*self.N
        self.ansatzes = []

        self.qc = None      # Generate circuit on demand
        self.inv_qc = None

    def add_ansatz(self,x,ansatz="regular",index=None,**arg_value):
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
            self.ansatzes.append(Ansatz(x,self.N,ansatz,**arg_value))
        else:
            for position in index:
                self.ansatzes.insert(position,Ansatz(x,self.N,ansatz,arg_value))

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
