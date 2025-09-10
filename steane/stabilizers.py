from .pauli_utils import pauli_mul_str, commutes

S=[
 "XXXXIII","XXIIXXI","XIXIXIX",
 "ZZZZIII","ZZIIZZI","ZIZIZIZ"
]

stab_set=set()
for mask in range(1<<len(S)):
    cur="IIIIIII"
    for i in range(len(S)):
        if (mask>>i)&1: _,cur=pauli_mul_str(cur,S[i])
    stab_set.add(cur)

def syndrome(p): return tuple(0 if commutes(p,s) else 1 for s in S)
def is_in_normalizer(op): return all(commutes(op,s) for s in S)
