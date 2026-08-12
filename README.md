# Traffic Engineering using Graph Theory and Linear Programming

A network optimization project that models the NSFNET backbone topology as a graph and solves Single-Commodity Flow (SCF) and Multi-Commodity Flow (MCF) traffic engineering problems using linear programming. The project combines shortest-path routing (Dijkstra's algorithm) with cost-minimizing flow optimization to analyze routing efficiency, link utilization, and network bottlenecks.

## Overview

This project addresses a core problem in network traffic engineering: how to route data through a network so that transmission cost is minimized while respecting link capacity constraints. It does this in two stages:

1. **Shortest-Path Routing** — Dijkstra's algorithm computes the lowest-cost path between a source and destination based on link weights.
2. **Flow Optimization** — Linear programming (via PuLP) computes cost-minimizing flow distributions for both a single traffic demand (SCF) and multiple simultaneous demands sharing the network (MCF).

The network used is **NSFNET**, the historical U.S. National Science Foundation backbone network, modeled as an undirected graph with 14 nodes and 21 bidirectional links, each with a 45 Mbps capacity.

Source and destination nodes, along with traffic demands, are deterministically generated from a student number seed, making each run reproducible and unique to the input identifier.

## Features

- Automatic topology assignment (NSFNET or GEANT2) and demand generation from a numeric seed
- Graph construction and visualization of the NSFNET topology using NetworkX
- Dijkstra's shortest-path computation with path and cost visualization
- Single-Commodity Flow (SCF) linear programming model (Min-Cost Flow)
- Multi-Commodity Flow (MCF) linear programming model with shared capacity constraints
- Automatic demand scaling to find a feasible solution when capacity limits are exceeded
- Link utilization analysis and bottleneck identification
- Statistical comparison between SCF and MCF performance (cost efficiency, utilization distribution, resilience)
- Generated diagrams: shortest path, SCF flow, MCF flow, and utilization charts

## Project Structure

```
.
├── Topology.py                      # Generates SCF/MCF demand data from a student number seed
├── graph.py                         # Builds the NSFNET graph and computes the Dijkstra shortest path
├── Linear_programming_models.py     # PuLP-based SCF and MCF Min-Cost Flow solvers
├── NSFNET_Links.csv                 # NSFNET topology: source, destination, weight, capacity
├── scf_<id>.csv                     # Generated SCF source/destination/demand
├── demands_<id>.csv                 # Generated MCF commodities (source/destination/demand per flow)
├── SCF_result.csv                   # SCF solver output: link flows, utilization, cost
├── MCF_result.csv                   # MCF solver output: link flows, utilization, cost
├── LinkUtilisation.csv              # Combined link utilization dataset
├── shortest_path_nsfnet.png         # Dijkstra shortest path visualization
├── SCF_flow_diagram.png             # SCF solution flow diagram
├── MCF_flow_diagram.png             # MCF solution flow diagram
└── Report.pdf                       # Full project report (methodology, formulation, results, discussion)
```

## Methodology

### 1. Topology Assignment and Demand Generation
A student/ID number is used to deterministically derive:
- The assigned topology (NSFNET if the digit sum is even, GEANT2 if odd)
- SCF source, destination, and demand
- Five MCF commodities (source-destination-demand triples) derived with a variable step size

### 2. Graph Modeling
The NSFNET topology (14 nodes, 21 links) is loaded from `NSFNET_Links.csv` and represented as an undirected graph `G = (V, E)` using NetworkX, with each edge annotated with a weight (routing cost) and a capacity (45 Mbps).

### 3. Shortest-Path Routing
Dijkstra's algorithm is used to find the minimum-cost path between the SCF source and destination based on link weights, independent of capacity constraints.

### 4. Linear Programming Formulation

**Single-Commodity Flow (SCF)**

Minimize the total routing cost subject to flow conservation and capacity constraints:

```
Minimize   Z = Σ w_ij · f_ij                for all (i,j) in E

Subject to:
  Σ f_ij − Σ f_ji = { d   if i = s
                      -d  if i = t            for all i in V
                      0   otherwise

  0 ≤ f_ij ≤ c_ij                             for all (i,j) in E
```

**Multi-Commodity Flow (MCF)**

Extends the SCF formulation to K simultaneous commodities sharing the same link capacities:

```
Minimize   Z = Σ_k Σ_(i,j) w_ij · f_ij^k

Subject to:
  Per-commodity flow conservation at every node
  Σ_k f_ij^k ≤ c_ij                           (shared capacity constraint)
  f_ij^k ≥ 0                                  (non-negativity)
```

Both models are solved using **PuLP** with the CBC solver. Since the raw demands can exceed available network capacity, both solvers apply iterative demand scaling (reducing demand until a feasible solution is found) to guarantee a solvable model.

## Results Summary

| Metric | SCF | MCF |
|---|---|---|
| Total demand | 320 Mbps (scaled to 124.0 Mbps) | 1280 Mbps (scaled to 292.8 Mbps) |
| Feasible scaling factor | 0.387 | 0.229 |
| Total cost | 1217.69 | 2845.77 |
| Average link utilization | 90.20% | 83.04% |
| Maximum link utilization | 100.00% | 100.00% |
| Cost per Mbps | 9.82 | 9.72 |

**Key findings:**
- The Dijkstra shortest path from Node 3 to Node 7 is `3 → 4 → 7` with a total cost of 6.
- SCF achieves higher average utilization but concentrates traffic on a single route, creating a single point of congestion.
- MCF distributes traffic across multiple paths, achieving a higher total cost but better load balancing and greater resilience to link failure.
- Uniform 45 Mbps link capacities forced significant demand scaling for both models (61.3% for SCF, 77.1% for MCF), illustrating a realistic capacity-constrained routing scenario.

## Technologies Used

- **Python 3**
- [NetworkX](https://networkx.org/) — graph construction, shortest-path computation, and network analysis
- [PuLP](https://coin-or.github.io/pulp/) — linear programming modeling and solving (CBC solver)
- [pandas](https://pandas.pydata.org/) — data loading and manipulation
- [Matplotlib](https://matplotlib.org/) — network topology and results visualization

## Installation

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install networkx pulp pandas matplotlib numpy
```

## Usage

Run the scripts in order:

```bash
# 1. Generate SCF and MCF demand datasets from your student/ID number
python Topology.py

# 2. Build the NSFNET graph and compute the Dijkstra shortest path
python graph.py

# 3. Solve the SCF and MCF linear programming models
python Linear_programming_models.py
```

Each script prints its results to the console and saves output CSVs and diagrams to the working directory.

## Report

The full project report — including the theoretical background, mathematical formulation, matrix representation, statistical analysis, and discussion of results — is included as `Report.pdf`.

## Author

Chrinovic Raya Tshiwaya
Network Systems 3 (NSS370S), Department of Electrical, Electronic and Computer Engineering
Cape Peninsula University of Technology

## License

This project was completed as part of an academic assignment (GA2, NSS370S) at Cape Peninsula University of Technology. Feel free to reference or adapt it for educational purposes.
