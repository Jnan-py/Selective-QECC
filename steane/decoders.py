import itertools
from .stabilizers import syndrome, is_in_normalizer, stab_set
from .pauli_utils import pauli_mul_str

pauli_letters=['X','Y','Z']

syndrome_map={}
for w in range(1,4):
    for pos in itertools.combinations(range(7),w):
        for types in itertools.product(pauli_letters,repeat=w):
            s=list('I'*7)
            for ppos,t in zip(pos,types): s[ppos]=t
            err=''.join(s); syn=syndrome(err)
            if syn not in syndrome_map or w<sum(x!='I' for x in syndrome_map[syn]):
                syndrome_map[syn]=err

syndrome_map[tuple([0]*6)]="IIIIIII"

def residual_after_correction(err,corr): return pauli_mul_str(err,corr)[1]
def logical_failure(resid): return is_in_normalizer(resid) and resid not in stab_set

def min_weight_decoder(): return dict(syndrome_map)
