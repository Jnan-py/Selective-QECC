# Selective Quantum Error Correction (VarQEC) for the Steane [[7,1,3]] Code

This repository contains the full implementation, proofs, and experiments for our **Selective Quantum Error Correction (VarQEC)** framework.  
We demonstrate:

- Enumeration of harmful weight-2 Pauli patterns for the Steane [[7,1,3]] code.
- Analytic formula for the logical error prefactor α = H/9.
- Monte Carlo and exact evaluation under symmetric depolarizing noise.
- VarQEC optimization under biased noise (e.g., X-biased), showing significant improvement over Minimum-Weight (MW) decoding.
- Reproducible CSV outputs and plots.

## Quickstart

Clone and install:

```bash
git clone https://github.com/Jnan-py/Selective-QECC.git
cd Selective-QECC
pip install -r requirements.txt
```

Run harmful pattern enumeration:

```bash
python experiments/harmful_enum.py
```

Run biased noise sweep (MW vs VarQEC):

```bash
python experiments/biased_sweep.py
```

CSVs will appear in data/.

## Citation

If you use this repository, please cite:

```bash

Yalla Jnan Devi Satya Prasad.
Selective Quantum Error Correction for Variational Quantum Classifiers: Exact Error-Suppression Bounds and Trainability Analysis.
TechRxiv. September 09, 2025.
DOI: [10.36227/techrxiv.175743242.27149404/v1](https://doi.org/10.36227/techrxiv.175743242.27149404/v1)

```
