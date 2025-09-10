pauli_mul = {
    ('I','I'):(1,'I'), ('I','X'):(1,'X'), ('I','Y'):(1,'Y'), ('I','Z'):(1,'Z'),
    ('X','I'):(1,'X'), ('Y','I'):(1,'Y'), ('Z','I'):(1,'Z'),
    ('X','X'):(1,'I'), ('Y','Y'):(1,'I'), ('Z','Z'):(1,'I'),
    ('X','Y'):(1j,'Z'), ('Y','X'):(-1j,'Z'),
    ('X','Z'):(-1j,'Y'), ('Z','X'):(1j,'Y'),
    ('Y','Z'):(1j,'X'), ('Z','Y'):(-1j,'X')
}

def pauli_mul_str(a,b):
    phase=1
    res=[]
    for ai,bi in zip(a,b):
        ph,r=pauli_mul[(ai,bi)]
        phase*=ph; res.append(r)
    return phase,''.join(res)

def commutes(p,q):
    anticomm=0
    for a,b in zip(p,q):
        if a=='I' or b=='I': continue
        if a!=b: anticomm+=1
    return anticomm%2==0
