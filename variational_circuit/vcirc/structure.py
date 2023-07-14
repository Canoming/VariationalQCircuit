def vcnot_1(self):
    """
    Nearby qubits, start from 0
    """
    shape = (self.N//2,)
    para = self.paras.reshape(shape)
    for j in range(self.N//2):
        self.add_gate("CRX",2*j,2*j+1,para[j])

def vcnot_2(self):
    """
    Nearby qubits, start from 1
    """
    shape = ((self.N-1)//2,)
    para = self.paras.reshape(shape)
    for j in range((self.N-1)//2):
        if 2*j < self.N-2:
            self.add_gate("CRX", 2*j+1, 2*j+2, para[j])

def vcnot_3(self):
    """
    Long range CNOT, cross half circuit
    """
    shape = (self.N//2,)
    para = self.paras.reshape(shape)
    for j in range(self.N//2):
        self.add_gate("CRX",j,j+self.N//2,para[j])

def local(self):
    """
    Only contains local unitaries
    """
    shape = (self.N,3)
    para = self.paras.reshape(shape)
    for i, angles in enumerate(para):
        self.add_gate("RZ", i, None, angles[0])
        self.add_gate("RY", i, None, angles[1])
        self.add_gate("RZ", i, None, angles[2])

def regular(self):
    """
    A layer of local unitaries + A layer of CNOT gates between all neighbors
    """
    shape = (self.N,3)
    para = self.paras.reshape(shape)
    for i, angles in enumerate(para):
        self.add_gate("RZ", i, None, angles[0])
        self.add_gate("RY", i, None, angles[1])
        self.add_gate("RZ", i, None, angles[2])
    if self.N == 1:
        return
    for j in range(self.N-1):
        self.add_gate("CNOT",j,j+1)
    self.add_gate("CNOT",self.N-1,0)