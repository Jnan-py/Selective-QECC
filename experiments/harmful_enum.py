from itertools import combinations, product
from steane.stabilizers import syndrome, stab_set, is_in_normalizer, S
from steane.pauli_utils import pauli_mul_str, commutes
from steane.decoders import syndrome_map, logical_failure, residual_after_correction

harmful=[]
for (i,j) in combinations(range(7),2):
    for a,b in product(['X','Y','Z'],repeat=2):
        p=list('I'*7); p[i]=a; p[j]=b; pstr=''.join(p)
        s=syndrome(pstr); corr=syndrome_map[s]
        _,residual=pauli_mul_str(pstr,corr)
        if logical_failure(residual):
            harmful.append((pstr,corr,residual))

print("Total harmful weight-2 =",len(harmful))
print("Sample:",harmful[:10])
