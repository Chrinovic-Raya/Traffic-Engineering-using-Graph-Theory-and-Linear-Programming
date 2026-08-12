# ======================================================
# GA2 Flow Generator for NSS370S
# Author: Dr A. Brandt (CPUT)
# ======================================================
# Automatically assigns topology (NSFNET/GEANT2)
# and generates SCF + MCF demand data.
# ======================================================
import math
import pandas as pd

# === Student input ===
student_number = "222170972"  # <-- Replace with your own

# === Derived values ===
digits = [int(x) for x in student_number]
S = sum(digits)
L = digits[-1]
SL = digits[-2] if len(digits) >= 2 else 0
TL = digits[-3] if len(digits) >= 3 else 0

# === Automatic topology assignment ===
if S % 2 == 0:
    topology = "NSFNET"
    N = 14
else:
    topology = "GEANT2"
    N = 32

print("=====================================================")
print("=== Assigned Topology ===")
print("=====================================================")
print(f"Student number : {student_number}")
print(f"Sum of digits : {S}")
print(f"Assigned topology: {topology} (N = {N} nodes)")
print("-----------------------------------------------------\n")

# === Single-Commodity Flow (SCF) ===
S2 = 10 * SL + L
s = (S2 % N) + 1
S3 = 100 * TL + 10 * SL + L
t = (S3 % N) + 1
if s == t:
    t = ((t) % N) + 1
d1 = 10 * S

print("=====================================================")
print("=== Single-Commodity Flow (SCF) ===")
print("=====================================================")
print(f"Source node (s) : {s}")
print(f"Destination node (t): {t}")
print(f"Demand (d1) : {d1} Mbps")
print("-----------------------------------------------------\n")

scf_df = pd.DataFrame([{"source": s, "destination": t, "demand_Mbps": d1}])
scf_filename = f"scf__{student_number}.csv"
scf_df.to_csv(scf_filename, index=False)

# === Multi-Commodity Flow (MCF) ===
K = 5
p = 1 + (S % 4)
alphas = [0.40, 0.60, 0.80, 1.00, 1.20]
rows = []
for k in range(1, K + 1):
    sk = ((s + (k - 1) * p - 1) % N) + 1
    tk = ((t + (k - 1) * 2 * p - 1) % N) + 1
    if sk == tk:
        tk = (tk % N) + 1
    dk = round(alphas[k - 1] * d1)
    rows.append({"commodity": k, "source": sk, "destination": tk, "demand_Mbps": dk})

mcf_df = pd.DataFrame(rows)
mcf_filename = f"demands_{student_number}.csv"
mcf_df.to_csv(mcf_filename, index=False)

print("=====================================================")
print("=== Multi-Commodity Flow (MCF) ===")
print("=====================================================")
print(f"Step size (p): {p}\n")
for _, r in mcf_df.iterrows():
    print(f"Commodity {r['commodity']}: s={r['source']}, t={r['destination']}, demand={r['demand_Mbps']} Mbps")
print("\n-----------------------------------------------------")
print("MCF Demand Table")
print("-----------------------------------------------------")
print(mcf_df.to_string(index=False))
print("-----------------------------------------------------")
print(f"Saved SCF file: {scf_filename}")
print(f"Saved MCF file: {mcf_filename}")
print("=====================================================\n")
print(f"Quick summary: Student {student_number} -> Topology={topology}, s={s}, t={t}, d1={d1} Mbps, step size p={p}")