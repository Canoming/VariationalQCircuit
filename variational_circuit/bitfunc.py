import numpy as np

# TODO: Finish the class
class bitarray():
    def __init__(self,N,buffer=np.array([0])):
        obj = super().__new__(cls,(N,),np.uint8,buffer)
        return obj
    
    def HamWeight(self):
        return self.count(1)

def inner(a,b):
    n = len(a)
    if len(b) != n:
        raise ValueError('Incapable length')
    temp = False
    for i in range(n):
        temp ^= a[i]&b[i]
    return int(temp)