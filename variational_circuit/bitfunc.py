from bitstring import BitArray

class BitVec(BitArray):
    def __init__(self,auto=None, length=None,offset=None,**kwargs):
        super().__init__()
    
    def HamWeight(self):
        return self.count(1)

def inner(a,b):
    c = a & b
    temp = False
    for bit in c:
        temp ^ bit
    return BitVec(bool=temp)
        


if __name__ == "__main__":
    a = BitVec('0x00')
    print(a.bin)
