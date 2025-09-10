# Methods: Selective Quantum Error Correction (VarQEC) for VQCs

This repository implements the simulations and proofs behind:

**Yalla Jnan Devi Satya Prasad**  
_Selective Quantum Error Correction for Variational Quantum Classifiers:  
Exact Error-Suppression Bounds and Trainability Analysis_  
TechRxiv. September 09, 2025.  
DOI: [10.36227/techrxiv.175743242.27149404/v1](https://doi.org/10.36227/techrxiv.175743242.27149404/v1)

---

## 1. Steane Code [[7,1,3]]

- 7 physical qubits encode 1 logical qubit with distance 3.
- Stabilizer generators used:

XXXXIII
XXIIXXI
XIXIXIX
ZZZZIII
ZZIIZZI
ZIZIZIZ

- Logical operators:
  - \( X_L = XXXXXXX \)
  - \( Z_L = ZZZZZZZ \)

---

## 2. Harmful Error Enumeration

- Enumerate all weight-2 Pauli errors (147 harmful patterns found).
- Classify residuals as **X-like, Y-like, Z-like** using commutation with logicals.
- CSV export: `harmful_patterns.csv`.

---

## 3. Monte Carlo Simulation

- Apply i.i.d. depolarizing noise with parameter \(p\).
- Decode using **minimum-weight decoder (MWD)**.
- Compute exact logical failure probability \(p_L\).
- Fit analytic constant:  
  \[
  p_L \approx \alpha p^2, \quad \alpha = H/9 = 16.\overline{3}
  \]

---

## 4. VarQEC Optimization

- For each syndrome, instead of fixed minimum-weight correction, optimize a **parametric recovery map**.
- Optimize via coordinate descent:
  - Sweep through syndromes.
  - Change correction operator if it reduces logical failure.
- Tracks empirical \(p_L\) vs. MWD.

---

## 5. Biased Noise Extension

- Supports biased noise channels (e.g., 80% X errors, 10% Y, 10% Z).
- VarQEC shows **dramatic improvement** under biased noise (sometimes full suppression at leading order).

---

## 6. Files

- `steane_enum.py`: syndrome map + harmful error enumeration.
- `monte_carlo_pl_fit.py`: logical error probability estimation + analytic fit.
- `varqec_decoder_opt.py`: VarQEC optimization under depolarizing noise.
- `biased_sweep.py`: sweep over biased noise parameters and compare MWD vs. VarQEC.
- `methods.md`: this file.
