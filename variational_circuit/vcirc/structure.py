from qutip.qip.circuit import QubitCircuit

def vcnot_1(para,N):
    qc = QubitCircuit(N)
    shape = (N//2,)
    para = para.reshape(shape)
    i = 0
    for j in range(N//2):
        qc.add_gate("CRX",2*j,2*j+1,para[j])
    return qc

def vcnot_2(para,N):
    qc = QubitCircuit(N)
    shape = (N//2,)
    para = para.reshape(shape)
    i = 0
    for j in range(N//2):
        qc.add_gate("CRX",j,j+N//2,para[j])
    return qc

def vcnot_3(para,N):
    qc = QubitCircuit(N)
    shape = (N//2,)
    para = para.reshape(shape)
    i = 0
    for j in range(N//2):
        if 2*j<N-2:
            qc.add_gate("CRX",2*j+1,2*j+2,para[j])
    return qc

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