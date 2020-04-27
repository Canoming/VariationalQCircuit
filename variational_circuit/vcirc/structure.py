from qutip.qip.circuit import QubitCircuit

def regular(para,N,inv=False):
    qc = QubitCircuit(N)
    i = 0
    if not inv:
        for angles in para:
            qc.add_gate("RZ", i, None, angles[0])
            qc.add_gate("RX", i, None, angles[1])
            qc.add_gate("RZ", i, None, angles[2])
            i+=1
        for j in range(N-1):
            qc.add_gate("CNOT",j,j+1)
    else:
        for j in reversed(range(N-1)): # CNOT in inverses order
            qc.add_gate("CNOT",j,j+1)
        for angles in reversed(self.para):
            qc.add_gate("RZ", i, None, -angles[2])
            qc.add_gate("RZ", i, None, -angles[1])
            qc.add_gate("RX", i, None, -angles[0])
            i+=1
    return qc,(N,3)


def CNN4_1(para,N,inv=False):
    qc = QubitCircuit(N)
    i = 0
    if not inv:
        for angles in para:
            qc.add_gate("RZ", i, None, angles[0])
            qc.add_gate("RX", i, None, angles[1])
            qc.add_gate("RZ", i, None, angles[2])
            i+=1
        for j in range(N-1):
            if j //2 == 0:
                qc.add_gate("CNOT",j,j+1)
    else:
        raise ValueError('Inverse circuit undefined')
    return qc,(N,3)

def CNN4_2(para,N,inv=False):
    qc = QubitCircuit(N)
    i = 0
    if not inv:
        for angles in para:
            qc.add_gate("RZ", i, None, angles[0])
            qc.add_gate("RX", i, None, angles[1])
            qc.add_gate("RZ", i, None, angles[2])
            i+=1
        for j in range(N-1):
            if j <2:
                qc.add_gate("CNOT",j,j+N//2)
    else:
        raise ValueError('Inverse circuit undefined')
    return qc,(N,3)