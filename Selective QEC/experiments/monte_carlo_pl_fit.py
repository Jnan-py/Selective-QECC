import random
import numpy as np
from tqdm import trange
from steane.decoders import syndrome_map, residual_after_correction, logical_failure
from steane.stabilizers import syndrome

pauli_letters=['X','Y','Z']

def sample_error(p):
    s=['I']*7
    for i in range(7):
        if random.random()<p:
            s[i]=random.choice(pauli_letters)
    return ''.join(s)

def decode_and_check(err):
    s=syndrome(err); corr=syndrome_map[s]
    resid=residual_after_correction(err,corr)
    return 1 if logical_failure(resid) else 0

def estimate_pL(p,trials=50000):
    return sum(decode_and_check(sample_error(p)) for _ in trange(trials))/trials

if __name__=="__main__":
    ps=[1e-4,3e-4,1e-3,3e-3]
    for p in ps:
        pl=estimate_pL(p)
        print(f"p={p:.1e}, pL≈{pl:.3e}")
