import numpy as np
from qutip.qip.circuit import *

class Ansatz:
    """
    Generate the ansatz
    
    Parameters
    ----------
        x: list
            The parameters of the Ansatz
    Attributes
    -------
        N: int
            Number of qubits.
        dims: list
            Dimension of the ansatz (default [2]*N).
        qc: QubitCircuit
            The ansatz with given parameters.
        inv_qc: QubitCircuit
            The inverse of ansatz with given parameters.
        arg_value:
            An position holder for special ansatzes.
    """
    def __init__(self,x,N,ansatz="regular",arg_value=None):
        # Init
        self.N = N
        self.dims= [2]*self.N
        self.name = ansatz
        self.para = x

        self.qc = None    # Generate circuit on demand
        self.inv_qc = None

        # Setup parameters
        if self.name == "regular":
            # Dimension Check
            if not isinstance(x[0],(list,np.ndarray,tuple)):
                if len(x)%3 != 0:
                    raise ValueError("Ansatz dimension doesn't match\n3 parameters are required for each qubit.")
                else:
                    self.para = np.split(x,len(x)//3)
            if len(self.para) != self.N:
                raise ValueError("Ansatz dimension doesn't match\n%s parameters are required." % 3*self.N)
        else:
            raise ValueError("Unkown ansatz %s" % ansatz)

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
                self.qc.add_gate("CNOT",j,j+1, None)
            return self.qc
        else:
            raise ValueError("Unkown ansatz: %s" % ansatz)

    def set_inv_circuit(self):  # It's necessary since the reverse_circuit in qutip didn't take the inverse of gates.
        self.inv_qc = QubitCircuit(self.N)
        if self.name == "regular":
            for j in reversed(range(self.N-1)): # CNOT in inverses order
                self.inv_qc.add_gate("CNOT",j,j+1, None)
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

    def add_ansatz(self,x,ansatz="regular",index=None,arg_value=None):
        """
        Adds an ansatz to the circuit.

        Parameters
        ----------
            x : list
                The list of parameters for the ansatz.
            ansatz : str
                The structure of ansatz
        """
        if index is None:
            self.ansatzes.append(Ansatz(x,self.N,ansatz,arg_value))
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

    def update_ansatzes(self,x_in):
        """
        update variational circuit parameters

        Parameters
        ----------
            x_in : list
                list of parameters
        """
        temp_x = np.array(x_in)
        pos = 0
        for i in range(len(self.ansatzes)):
            if isinstance(self.ansatzes[i].para[0],(list,tuple,np.ndarray)):
                for j in range(len(self.ansatzes[i].para)):
                    n = len(self.ansatzes[i].para[j])
                    self.ansatzes[i].para[j] = x_in[pos:pos+n]
                    pos+=n
            else:
                ansatz.para = np.delete(temp_x,np.arange(len(ansatz.para)))
        self.propagators()
