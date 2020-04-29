from qutip.qip.circuit import QubitCircuit

def local(para,N):
    qc = QubitCircuit(N)
    shape = (N,3)
    para = para.reshape(shape)
    i = 0
    for angles in para:
        qc.add_gate("RZ", i, None, angles[0])
        qc.add_gate("RX", i, None, angles[1])
        qc.add_gate("RZ", i, None, angles[2])
        i+=1
    return qc

def regular(para,N):
    qc = QubitCircuit(N)
    shape = (N,3)
    para = para.reshape(shape)
    i = 0
    for angles in para:
        qc.add_gate("RZ", i, None, angles[0])
        qc.add_gate("RX", i, None, angles[1])
        qc.add_gate("RZ", i, None, angles[2])
        i+=1
    for j in range(N-1):
        qc.add_gate("CNOT",j,j+1)
    return qc


def CNN4_1(para,N):
    qc = QubitCircuit(N)
    shape = (N,3)
    para = para.reshape(shape)
    i = 0
    for angles in para:
        qc.add_gate("RZ", i, None, angles[0])
        qc.add_gate("RX", i, None, angles[1])
        qc.add_gate("RZ", i, None, angles[2])
        i+=1
    for j in range(N-1):
        if j //2 == 0:
            qc.add_gate("CNOT",j,j+1)
    return qc

def CNN4_2(para,N,inv=False):
    qc = QubitCircuit(N)
    shape = (N,3)
    para = para.reshape(shape)
    i = 0
    for angles in para:
        qc.add_gate("RZ", i, None, angles[0])
        qc.add_gate("RX", i, None, angles[1])
        qc.add_gate("RZ", i, None, angles[2])
        i+=1
    for j in range(N-1):
        if j < N/2:
            qc.add_gate("CNOT",j,j+N//2)
    return qc