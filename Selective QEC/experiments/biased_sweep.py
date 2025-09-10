import time, csv, sys
from itertools import product
from varqec_decoder_opt import syndrome_map, steane_sample_error, decode_failure_rate, varqec_optimize

ps = [1e-3]   
biases = [(0.8,0.1,0.1), (0.6,0.2,0.2), (0.4,0.3,0.3)]
trials = 20000
max_iter = 5

def main():
    results = []
    for p in ps:
        for bx,by,bz in biases:
            print(f"\n=== Biased-noise VarQEC for Steane, p={p:.1e}, bias=({bx:.1f},{by:.1f},{bz:.1f}) ===")
            start=time.time()
            
            mw_pL = decode_failure_rate(syndrome_map, p, bias=(bx,by,bz), trials=trials)
            print(f"MW pL={mw_pL:.6e}")
            
            var_map, var_pL = varqec_optimize(syndrome_map, p, bias=(bx,by,bz),
                                              trials=trials, max_iter=max_iter)
            reduction = (mw_pL-var_pL)/mw_pL*100 if mw_pL>0 else 0.0
            print(f"VarQEC pL={var_pL:.6e}, improvement={reduction:.2f}%")
            runtime=time.time()-start
            print(f"Runtime {runtime:.2f}s")
            results.append((p,bx,by,bz,mw_pL,var_pL,reduction))
    
    with open("biased_sweep_results.csv","w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["p","biasX","biasY","biasZ","pL_MW","pL_VarQEC","reduction_percent"])
        w.writerows(results)
    print("\nSaved biased_sweep_results.csv")

if __name__=="__main__":
    main()
