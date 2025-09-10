import time, sys, csv
from itertools import combinations, product

from steane.pauli_utils import pauli_mul_str   
from steane.stabilizers import syndrome, is_in_normalizer
from steane.decoders import residual_after_correction, logical_failure


pauli_letters = ['I', 'X', 'Y', 'Z']

def varqec_optimize(base_map, p, bias=(1/3,1/3,1/3), trials=5000, max_iter=3):    
    rec_map = {s: c for s, (w, c) in base_map.items()}
    best_pL = residual_after_correction(rec_map, p, bias=bias, trials=trials)
    print(f"[init] MW pL={best_pL:.6e}")

    for it in range(1, max_iter + 1):
        improved = False
        for syn in list(rec_map.keys()):
            old_corr = rec_map[syn]
            best_corr = old_corr
            best_val = best_pL

            for w in range(1, 3):
                for pos in combinations(range(7), w):
                    for types in product(pauli_letters, repeat=w):
                        cand = list("I" * 7)
                        for i, t in zip(pos, types):
                            cand[i] = t
                        cand = "".join(cand)

                        rec_map[syn] = cand
                        val = logical_failure(rec_map, p, bias=bias, trials=trials // 5)

                        if val < best_val:
                            best_val = val
                            best_corr = cand

            rec_map[syn] = best_corr
            if best_corr != old_corr:
                print(f" iter {it}: syndrome {syn} changed {old_corr}->{best_corr}, "
                      f"pL {best_pL:.3e}->{best_val:.3e}")
                best_pL = best_val
                improved = True

        if not improved:
            break

    return rec_map, best_pL


if __name__ == "__main__":    
    p = 1e-3
    bias = (0.8, 0.1, 0.1)   
    trials = 20000
    max_iter = 5
    
    if len(sys.argv) > 1:
        try:
            p = float(sys.argv[1])
        except Exception:
            print("Invalid argument, using default p=1e-3")

    start = time.time()
    
    mw_pL = logical_failure({s: c for s, (w, c) in syndrome.items()},
                                p, bias=bias, trials=trials)
    print(f"MW exact pL={mw_pL:.6e}")
    
    var_map, var_pL = varqec_optimize(syndrome, p, bias=bias,
                                      trials=trials, max_iter=max_iter)
    reduction = (mw_pL - var_pL) / mw_pL * 100 if mw_pL > 0 else 0.0
    print(f"VarQEC exact pL={var_pL:.6e}, reduction={reduction:.2f}%")
    print(f"Runtime {time.time()-start:.2f}s")
    
    with open("varqec_summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["p", "biasX", "biasY", "biasZ", "MW_pL", "VarQEC_pL", "reduction_percent"])
        w.writerow([p, *bias, mw_pL, var_pL, reduction])
