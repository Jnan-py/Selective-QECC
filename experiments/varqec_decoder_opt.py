import argparse
import time
import csv
import random
from itertools import combinations, product
from steane.decoders import syndrome_map as MW_SYNDROME_MAP
from steane.stabilizers import syndrome, is_in_normalizer, stab_set
from steane.pauli_utils import pauli_mul_str

N = 7
PAULI_LETTERS = ['X', 'Y', 'Z']

def build_candidates(max_w=3):
    cand = ['IIIIIII']
    for w in range(1, max_w+1):
        for positions in combinations(range(N), w):
            for types in product(PAULI_LETTERS, repeat=w):
                s = list('I' * N)
                for pos, t in zip(positions, types):
                    s[pos] = t
                cand.append(''.join(s))
    return cand

ALL_CANDIDATES = build_candidates(3)

def enumerate_patterns():
    paulis = ['I','X','Y','Z']
    patterns = []
    for mask in range(4**N):
        s = []
        x = mask
        allI = True
        for _ in range(N):
            d = x % 4
            x //= 4
            sym = paulis[d]
            s.append(sym)
            if sym != 'I':
                allI = False
        if allI:
            continue
        pstr = ''.join(s)[::-1]
        wt = sum(1 for c in pstr if c != 'I')
        patterns.append((pstr, wt))
    return patterns

PATTERNS = enumerate_patterns()
NPAT = len(PATTERNS)  

SYNDROME_TO_INDICES = {}
for idx, (pstr, wt) in enumerate(PATTERNS):
    s = syndrome(pstr)
    SYNDROME_TO_INDICES.setdefault(s, []).append(idx)

SYNDROME_TO_CANDIDATES = {}
for c in ALL_CANDIDATES:
    s = syndrome(c)
    SYNDROME_TO_CANDIDATES.setdefault(s, []).append(c)

MW_MAP = dict(MW_SYNDROME_MAP)

def precompute(p, bias):
    bx, by, bz = bias
    probs = [0.0] * NPAT
    for idx, (pstr, wt) in enumerate(PATTERNS):
        prob = 1.0
        for ch in pstr:
            if ch == 'I':
                prob *= (1.0 - p)
            else:
                if ch == 'X':
                    prob *= p * bx
                elif ch == 'Y':
                    prob *= p * by
                else:
                    prob *= p * bz
        probs[idx] = prob

    prob_logical = {}
    for s, idx_list in SYNDROME_TO_INDICES.items():
        cand_list = SYNDROME_TO_CANDIDATES.get(s, ['IIIIIII'])
        arr = [0.0] * len(cand_list)
        for ci, cand in enumerate(cand_list):
            tot = 0.0
            for idx in idx_list:
                pstr = PATTERNS[idx][0]
                _, residual = pauli_mul_str(pstr, cand)
                if is_in_normalizer(residual) and residual not in stab_set:
                    tot += probs[idx]
            arr[ci] = tot
        prob_logical[s] = (cand_list, arr)
    return probs, prob_logical

def exact_pL(decoder_map, prob_logical):
    total = 0.0
    for s, (cand_list, arr) in prob_logical.items():
        corr = decoder_map.get(s, MW_MAP.get(s, 'IIIIIII'))
        try:
            i = cand_list.index(corr)
        except ValueError:
            i = 0
        total += arr[i]
    return total

def harmful_weight2(decoder_map):
    details = []
    for (i,j) in combinations(range(N), 2):
        for a,b in product(PAULI_LETTERS, repeat=2):
            p = list('I'*N)
            p[i] = a; p[j] = b
            pstr = ''.join(p)
            s = syndrome(pstr)
            corr = decoder_map.get(s, MW_MAP.get(s, 'IIIIIII'))
            _, residual = pauli_mul_str(pstr, corr)
            if is_in_normalizer(residual) and residual not in stab_set:
                details.append((pstr, corr, residual))
    return details

def varqec_optimize_exact(p, bias, max_iters=10, randomize=False, verbose=True):
    _, prob_logical = precompute(p, bias)    
    decoder_map = {s: MW_MAP.get(s, 'IIIIIII') for s in prob_logical.keys()}
    pL = exact_pL(decoder_map, prob_logical)
    history = [pL]
    if verbose:
        print(f"[init] p={p:.3e}, MW exact p_L = {pL:.8e}")

    syndromes = list(prob_logical.keys())
    if randomize:
        random.shuffle(syndromes)

    for it in range(max_iters):
        improved = False
        if verbose:
            print(f"Iteration {it+1}/{max_iters}")
        for s in syndromes:
            cand_list, arr = prob_logical[s]
            cur_corr = decoder_map.get(s, MW_MAP.get(s, 'IIIIIII'))
            try:
                cur_idx = cand_list.index(cur_corr)
            except ValueError:
                cur_idx = 0
            cur_val = arr[cur_idx]
            min_idx = int(min(range(len(arr)), key=lambda k: arr[k]))
            min_val = arr[min_idx]
            if min_val + 1e-18 < cur_val - 1e-18:
                decoder_map[s] = cand_list[min_idx]
                pL += (min_val - cur_val)
                if verbose:
                    print(f"  syndrome {s}: {cur_corr} -> {cand_list[min_idx]} reduces pL by {cur_val-min_val:.3e}")
                improved = True
        history.append(pL)
        if not improved:
            if verbose:
                print("No improvement; stopping.")
            break
    return decoder_map, history

def write_csv(details, fname):
    with open(fname, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['error','correction','residual'])
        for row in details:
            w.writerow(row)

def parse_args():
    parser = argparse.ArgumentParser(description="VarQEC exact optimizer")
    parser.add_argument('--p', type=float, default=1e-3, help='physical error rate p')
    parser.add_argument('--bias', type=float, nargs=3, default=(0.8,0.1,0.1),
                        help='bias triple pX pY pZ (will be normalized if needed)')
    parser.add_argument('--max-iters', type=int, default=10)
    parser.add_argument('--randomize', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()
    p = args.p
    bx, by, bz = args.bias
    ssum = bx + by + bz
    if abs(ssum - 1.0) > 1e-12:
        bx, by, bz = bx/ssum, by/ssum, bz/ssum
    bias = {'X': bx, 'Y': by, 'Z': bz}

    t0 = time.time()
    _, prob_logical = precompute(p, bias)
    mw_map = {s: MW_MAP.get(s, 'IIIIIII') for s in prob_logical.keys()}
    pL_mw = exact_pL(mw_map, prob_logical)
    details_mw = harmful_weight2(mw_map)
    write_csv(details_mw, "harmful_patterns_mw.csv")
    print(f"MW exact p_L = {pL_mw:.8e}, harmful_weight2 = {len(details_mw)}")

    best_map, history = varqec_optimize_exact(p, bias, max_iters=args.max_iters, randomize=args.randomize, verbose=True)
    pL_var = history[-1]
    details_var = harmful_weight2(best_map)
    write_csv(details_var, "harmful_patterns_varqec.csv")
    pL_mw_val = pL_mw
    pL_var_val = pL_var
    reduction = (pL_mw_val - pL_var_val) / pL_mw_val * 100.0 if pL_mw_val > 0 else (100.0 if pL_var_val==0 else 0.0)
    print(f"\nVarQEC exact p_L = {pL_var_val:.8e}, harmful_weight2 = {len(details_var)}")
    print(f"Relative reduction in p_L: {reduction:.6f}%")

    with open("varqec_summary.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["p","biasX","biasY","biasZ","pL_mw","pL_var","reduction_pct","H_mw","H_var"])
        w.writerow([p, bx, by, bz, f"{pL_mw_val:.8e}", f"{pL_var_val:.8e}", f"{reduction:.6f}", len(details_mw), len(details_var)])

    t1 = time.time()
    print(f"Total runtime: {t1 - t0:.2f} s")

if __name__ == "__main__":
    main()
