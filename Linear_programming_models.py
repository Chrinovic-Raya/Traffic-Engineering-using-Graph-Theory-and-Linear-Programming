"""
GA2 Project: Min-Cost Flow Solver for NSFNET
Student: 222170972
Using PuLP 
"""

import pulp
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ============================================================
# STEP 1: Load NSFNET Topology from CSV
# ============================================================

print("="*60)
print("LOADING NSFNET TOPOLOGY FROM CSV")
print("="*60)

# Read NSFNET links from CSV file
nsfnet_df = pd.read_csv("NSFNET_Links.csv")
print(f"Loaded {len(nsfnet_df)} edges from NSFNET.csv")
print()

# Create bidirectional graph from CSV
G = nx.Graph()
for _, row in nsfnet_df.iterrows():
    src = int(row['Source'])
    dst = int(row['Destination'])
    cap = int(row['Capacity_Mbps'])
    wt = int(row['Weight'])
    G.add_edge(src, dst, capacity=cap, weight=wt)

nodes = list(G.nodes())
edges = list(G.edges())

print("="*60)
print("NSFNET TOPOLOGY LOADED")
print("="*60)
print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")
print(f"Total Capacity: {len(edges) * 45} Mbps")
print()

# ============================================================
# STEP 2: Load SCF Problem Data from CSV
# ============================================================

print("="*60)
print("LOADING SCF DATA FROM CSV")
print("="*60)

# Read SCF data from CSV file
scf_df = pd.read_csv("scf_222170972.csv")
scf_source = int(scf_df.loc[0, 'source'])
scf_dest = int(scf_df.loc[0, 'destination'])
scf_demand = int(scf_df.loc[0, 'demand_Mbps'])

print(f"Loaded SCF data from scf_222170972.csv")
print()

print("="*60)
print("SINGLE-COMMODITY FLOW (SCF) PROBLEM")
print("="*60)
print(f"Source: Node {scf_source}")
print(f"Destination: Node {scf_dest}")
print(f"Demand: {scf_demand} Mbps")
print()

# ============================================================
# STEP 3: Solve SCF using Min-Cost Flow (PuLP)
# ============================================================
# STEP SCF-3 Actual function
def solve_scf_min_cost(G, source, dest, demand, scaling_factor=1.0):
    """
    Solve Single-Commodity Min-Cost Flow using PuLP
    
    Mathematical Formulation:
    
    Decision Variables:
        f[i,j] = flow on edge (i,j)
    
    Objective:
        Minimize Σ weight[i,j] × f[i,j]
    
    Constraints:
        1. Flow conservation: Σ f[i,j] - Σ f[j,i] = supply[i]
        2. Capacity: 0 ≤ f[i,j] ≤ capacity[i,j]
        3. Supply vector: supply[source] = demand, supply[dest] = -demand, else 0
    """
    
    scaled_demand = demand * scaling_factor
    
    # Create LP problem
    prob = pulp.LpProblem("SCF_Min_Cost_Flow", pulp.LpMinimize)
    
    # Decision variables: flow on each edge (both directions)
    flow_vars = {}
    for (i, j) in G.edges():
        flow_vars[(i,j)] = pulp.LpVariable(f"f_{i}_{j}", lowBound=0, 
                                           upBound=G[i][j]['capacity'])
        flow_vars[(j,i)] = pulp.LpVariable(f"f_{j}_{i}", lowBound=0, 
                                           upBound=G[i][j]['capacity'])
    
    # Objective: Minimize total cost
    cost_expr = []
    for (i, j) in G.edges():
        weight = G[i][j]['weight']
        cost_expr.append(weight * flow_vars[(i,j)])
        cost_expr.append(weight * flow_vars[(j,i)])
    
    prob += pulp.lpSum(cost_expr), "Total_Cost"
    
    # Constraints: Flow conservation at each node
    for node in G.nodes():
        # Determine supply/demand for this node
        if node == source:
            supply_val = scaled_demand
        elif node == dest:
            supply_val = -scaled_demand
        else:
            supply_val = 0
        
        # Outgoing flow - Incoming flow = supply
        outgoing = []
        incoming = []
        
        for neighbor in G.neighbors(node):
            outgoing.append(flow_vars[(node, neighbor)])
            incoming.append(flow_vars[(neighbor, node)])
        
        prob += pulp.lpSum(outgoing) - pulp.lpSum(incoming) == supply_val, \
                f"FlowConservation_Node_{node}"
    
    # Solve
    # STEP SCF-4 actual solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Check status
    status = pulp.LpStatus[prob.status]
    
    if status == "Optimal":
        return prob, flow_vars, scaled_demand, True
    else:
        return prob, None, scaled_demand, False


def _decompose_directed_flows_to_paths(flow_map, source, dest, eps=1e-6):
    """
    Decompose a directed flow (dict of (u,v)->flow) into a set of simple paths
    from source to dest with associated flow amounts using successive
    shortest-path extraction on the positive-capacity residual graph.

    Returns a list of (path_list, flow_amount).
    """
    DG = nx.DiGraph()
    for (u, v), val in flow_map.items():
        if val is None:
            continue
        f = float(val)
        if f > eps:
            DG.add_edge(u, v, capacity=f)

    paths = []
    while True:
        try:
            path = nx.shortest_path(DG, source=source, target=dest)
        except nx.NetworkXNoPath:
            break

        # bottleneck capacity along the path
        bottleneck = min(DG[u][v]['capacity'] for u, v in zip(path, path[1:]))
        paths.append((path, bottleneck))

        # subtract bottleneck from edges; remove edges with ~zero capacity
        for u, v in zip(path, path[1:]):
            DG[u][v]['capacity'] -= bottleneck
            if DG[u][v]['capacity'] <= eps:
                DG.remove_edge(u, v)

    return paths

# Try solving with scaling if need
# SOLVE SCF STEP S-1
print("Attempting to solve SCF with original demand...")
scaling_factor = 1.0
max_iterations = 20

for iteration in range(max_iterations):
    # SOLVE SCF STEP SCF-2 Function Call
    prob, flow_vars, scaled_demand, is_feasible = solve_scf_min_cost(
        G, scf_source, scf_dest, scf_demand, scaling_factor
    )
    
    if is_feasible:
        print(f"✓ FEASIBLE at scaling factor: {scaling_factor:.3f}")
        print(f"  Scaled demand: {scaled_demand:.1f} Mbps")
        print(f"  Objective value (total cost): {pulp.value(prob.objective):.2f}")
        scf_scaling = scaling_factor
        break
    else:
        print(f"✗ Infeasible at scaling {scaling_factor:.3f}, trying {scaling_factor*0.9:.3f}...")
        scaling_factor *= 0.9
else:
    print("ERROR: Could not find feasible solution after scaling")
    flow_vars = None
    scf_scaling = 0

print()

# ============================================================
# STEP 4: Display SCF Results
# ============================================================

scf_flow_data = {}  # Store for visualization
# STEP SCF-6 Display Results
if flow_vars:
    print("="*60)
    print("SCF SOLUTION - LINK UTILIZATION")
    print("="*60)
    
    results = []
    total_flow_used = 0
    
    for (i, j) in G.edges():
        flow_ij = pulp.value(flow_vars[(i,j)])
        flow_ji = pulp.value(flow_vars[(j,i)])
        capacity = G[i][j]['capacity']
        weight = G[i][j]['weight']
        
        # Store flow data for visualization
        scf_flow_data[(i,j)] = flow_ij
        scf_flow_data[(j,i)] = flow_ji
        
        if flow_ij > 0.01 or flow_ji > 0.01:
            if flow_ij > flow_ji:
                net_flow = flow_ij
                direction = f"{i}→{j}"
            else:
                net_flow = flow_ji
                direction = f"{j}→{i}"
            
            utilization = (net_flow / capacity) * 100
            
            results.append({
                'Link': direction,
                'Flow (Mbps)': net_flow,
                'Capacity (Mbps)': capacity,
                'Utilization (%)': utilization,
                'Cost': net_flow * weight
            })
            
            total_flow_used += net_flow * weight
    
    df_scf = pd.DataFrame(results)
    print(df_scf.to_string(index=False))
    print()
    print(f"Total Cost: {total_flow_used:.2f}")
    print(f"Average Utilization: {df_scf['Utilization (%)'].mean():.2f}%")
    print(f"Max Utilization: {df_scf['Utilization (%)'].max():.2f}%")
    print()
    # Decompose SCF flows into explicit source->destination paths and print
    try:
        # build directed net-flow map from flow_vars
        directed = {}
        for (i, j) in G.edges():
            f_ij = pulp.value(flow_vars[(i, j)]) or 0.0
            f_ji = pulp.value(flow_vars[(j, i)]) or 0.0
            net = f_ij - f_ji
            if net > 1e-6:
                directed[(i, j)] = net
            elif net < -1e-6:
                directed[(j, i)] = -net

        scf_paths = _decompose_directed_flows_to_paths(directed, scf_source, scf_dest)
        print("SCF - decomposed paths (source -> ... -> dest : flow Mbps):")
        if scf_paths:
            for idx, (p, f) in enumerate(scf_paths, 1):
                path_str = ' -> '.join(str(n) for n in p)
                print(f"  {idx}. {path_str} : {f:.2f} Mbps")
        else:
            print("  (no simple source->dest path found in SCF flows)")
    except Exception as e:
        print(f"Warning: could not decompose SCF flows: {e}")

    # Save to CSV
    df_scf.to_csv('SCF_result.csv', index=False)
    print("✓ Saved: SCF_result.csv")
    print()

# ============================================================
# STEP 5: Load MCF Problem Data from CSV
# ============================================================

print("="*60)
print("LOADING MCF DATA FROM CSV")
print("="*60)

# Read MCF data from CSV file
mcf_df = pd.read_csv("demands_222170972.csv")
print(f"Loaded MCF data from demands_222170972.csv")
print()

# Convert DataFrame to list of dictionaries
mcf_commodities = []
for _, row in mcf_df.iterrows():
    mcf_commodities.append({
        'k': int(row['commodity']),
        'source': int(row['source']),
        'dest': int(row['destination']),
        'demand': int(row['demand_Mbps'])
    })

print("="*60)
print("MULTI-COMMODITY FLOW (MCF) PROBLEM")
print("="*60)
for comm in mcf_commodities:
    print(f"Commodity {comm['k']}: Node {comm['source']} → {comm['dest']}, "
          f"Demand = {comm['demand']} Mbps")
print(f"Total Demand: {sum(c['demand'] for c in mcf_commodities)} Mbps")
print()
# STEP MCF-1 Function definition
def solve_mcf_min_cost(G, commodities, scaling_factor=1.0):
    """
    Solve Multi-Commodity Min-Cost Flow using PuLP
    
    Decision Variables:
        f_k[i,j] = flow of commodity k on edge (i,j)
    
    Objective:
        Minimize Σ_k Σ_(i,j) weight[i,j] × f_k[i,j]
    
    Constraints:
        1. Flow conservation for each commodity k at each node
        2. Capacity: Σ_k f_k[i,j] ≤ capacity[i,j]
    """
    
    # Scale demands
    scaled_commodities = [{**c, 'demand': c['demand'] * scaling_factor} 
                          for c in commodities]
    
    prob = pulp.LpProblem("MCF_Min_Cost_Flow", pulp.LpMinimize)
    
    # Decision variables: flow for each commodity on each edge
    flow_vars = {}
    for comm in scaled_commodities:
        k = comm['k']
        for (i, j) in G.edges():
            flow_vars[(k,i,j)] = pulp.LpVariable(f"f_{k}_{i}_{j}", lowBound=0)
            flow_vars[(k,j,i)] = pulp.LpVariable(f"f_{k}_{j}_{i}", lowBound=0)
    
    # Objective: Minimize total cost across all commodities
    cost_expr = []
    for comm in scaled_commodities:
        k = comm['k']
        for (i, j) in G.edges():
            weight = G[i][j]['weight']
            cost_expr.append(weight * flow_vars[(k,i,j)])
            cost_expr.append(weight * flow_vars[(k,j,i)])
    
    prob += pulp.lpSum(cost_expr), "Total_Cost"
    
    # Constraint 1: Flow conservation for each commodity
    for comm in scaled_commodities:
        k = comm['k']
        source = comm['source']
        dest = comm['dest']
        demand = comm['demand']
        
        for node in G.nodes():
            if node == source:
                supply_val = demand
            elif node == dest:
                supply_val = -demand
            else:
                supply_val = 0
            
            outgoing = [flow_vars[(k, node, neighbor)] for neighbor in G.neighbors(node)]
            incoming = [flow_vars[(k, neighbor, node)] for neighbor in G.neighbors(node)]
            
            prob += pulp.lpSum(outgoing) - pulp.lpSum(incoming) == supply_val, \
                    f"FlowConservation_Commodity_{k}_Node_{node}"
    
    # Constraint 2: Total flow on each edge ≤ capacity
    for (i, j) in G.edges():
        total_flow_ij = [flow_vars[(comm['k'], i, j)] for comm in scaled_commodities]
        total_flow_ji = [flow_vars[(comm['k'], j, i)] for comm in scaled_commodities]
        
        capacity = G[i][j]['capacity']
        
        prob += pulp.lpSum(total_flow_ij) <= capacity, f"Capacity_{i}_{j}"
        prob += pulp.lpSum(total_flow_ji) <= capacity, f"Capacity_{j}_{i}"
    
    # Solve
    # STEP MCF-4 actual solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    status = pulp.LpStatus[prob.status]
    
    if status == "Optimal":
        return prob, flow_vars, scaled_commodities, True
    else:
        return prob, None, scaled_commodities, False

# Try solving MCF with scaling
print("Attempting to solve MCF...")
scaling_factor = 1.0
# STEP MCF-2 Function call
for iteration in range(max_iterations):
    prob_mcf, flow_vars_mcf, scaled_comms, is_feasible = solve_mcf_min_cost(
        G, mcf_commodities, scaling_factor
    )
    
    if is_feasible:
        print(f"✓ FEASIBLE at scaling factor: {scaling_factor:.3f}")
        print(f"  Total scaled demand: {sum(c['demand'] for c in scaled_comms):.1f} Mbps")
        print(f"  Objective value (total cost): {pulp.value(prob_mcf.objective):.2f}")
        mcf_scaling = scaling_factor
        break
    else:
        print(f"✗ Infeasible at scaling {scaling_factor:.3f}, trying {scaling_factor*0.9:.3f}...")
        scaling_factor *= 0.9
else:
    print("ERROR: Could not find feasible solution for MCF")
    flow_vars_mcf = None
    mcf_scaling = 0

print()

# ============================================================
# STEP 6: Display MCF Results
# ============================================================

mcf_flow_data = {}  # Store for visualization
# STEP MCF-5 display.
if flow_vars_mcf:
    print("="*60)
    print("MCF SOLUTION - LINK UTILIZATION")
    print("="*60)
    
    link_results = []
    
    for (i, j) in G.edges():
        capacity = G[i][j]['capacity']
        weight = G[i][j]['weight']
        
        # Sum flows across all commodities
        total_flow_ij = sum(pulp.value(flow_vars_mcf[(c['k'], i, j)]) 
                           for c in scaled_comms)
        total_flow_ji = sum(pulp.value(flow_vars_mcf[(c['k'], j, i)]) 
                           for c in scaled_comms)
        
        # Store for visualization
        mcf_flow_data[(i,j)] = total_flow_ij
        mcf_flow_data[(j,i)] = total_flow_ji
        
        if total_flow_ij > 0.01 or total_flow_ji > 0.01:
            net_flow = max(total_flow_ij, total_flow_ji)
            utilization = (net_flow / capacity) * 100
            
            link_results.append({
                'Link': f"{i}↔{j}",
                'Flow (Mbps)': net_flow,
                'Capacity (Mbps)': capacity,
                'Utilization (%)': utilization,
            })
    
    df_mcf = pd.DataFrame(link_results)
    print(df_mcf.to_string(index=False))
    print()
    print(f"Average Utilization: {df_mcf['Utilization (%)'].mean():.2f}%")
    print(f"Max Utilization: {df_mcf['Utilization (%)'].max():.2f}%")
    print()
    # Decompose MCF flows per commodity and print paths
    try:
        for comm in scaled_comms:
            k = comm['k']
            src = comm['source']
            dst = comm['dest']

            directed_k = {}
            for (i, j) in G.edges():
                f_ij = pulp.value(flow_vars_mcf[(k, i, j)]) or 0.0
                f_ji = pulp.value(flow_vars_mcf[(k, j, i)]) or 0.0
                net = f_ij - f_ji
                if net > 1e-6:
                    directed_k[(i, j)] = net
                elif net < -1e-6:
                    directed_k[(j, i)] = -net

            paths_k = _decompose_directed_flows_to_paths(directed_k, src, dst)
            print(f"Commodity {k} - decomposed paths (source -> ... -> dest : flow Mbps):")
            if paths_k:
                for idx, (p, f) in enumerate(paths_k, 1):
                    path_str = ' -> '.join(str(n) for n in p)
                    print(f"  {idx}. {path_str} : {f:.2f} Mbps")
            else:
                print("  (no simple source->dest path found for this commodity)")
            print()
    except Exception as e:
        print(f"Warning: could not decompose MCF flows: {e}")

    # Save to CSV
    df_mcf.to_csv('MCF_result.csv', index=False)
    df_mcf.to_csv('LinkUtilisation.csv', index=False)
    print("✓ Saved: MCF_result.csv")
    print("✓ Saved: LinkUtilisation.csv")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)

# ============================================================
# STEP 7: VISUALIZATION - SCF Flow Diagram
# ============================================================

if flow_vars and scf_flow_data:
    print("\nGenerating SCF visualization...")
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Layout
    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)
    
    # Determine node colors for SCF
    node_colors = []
    for node in G.nodes():
        if node == scf_source:
            node_colors.append('green')
        elif node == scf_dest:
            node_colors.append('red')
        else:
            node_colors.append('lightblue')
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=900, node_color=node_colors,
                          edgecolors='black', linewidths=2, ax=ax)
    
    # Node labels
    labels = {i: str(i) for i in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, 
                           font_weight='bold', ax=ax)
    
    # Draw all edges in light gray
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=3, 
                          edge_color='black', alpha=0.3, ax=ax)
    
    # Draw edges with flow - thickness proportional to flow
    flow_edges = []
    edge_widths = []
    edge_labels = {}
    
    for (i, j) in G.edges():
        flow_ij = scf_flow_data.get((i,j), 0)
        flow_ji = scf_flow_data.get((j,i), 0)
        
        if flow_ij > 0.01:
            flow_edges.append((i, j))
            edge_widths.append(max(2, flow_ij / 5))  # Scale width
            edge_labels[(i,j)] = f"{flow_ij:.1f}"
        
        if flow_ji > 0.01:
            flow_edges.append((j, i))
            edge_widths.append(max(2, flow_ji / 5))
            edge_labels[(j,i)] = f"{flow_ji:.1f}"
    
    # Draw flow edges
    nx.draw_networkx_edges(G, pos, edgelist=flow_edges, width=edge_widths,
                          edge_color='red', alpha=0.7, arrows=True,
                          arrowsize=20, arrowstyle='->', ax=ax)
    
    # Edge labels showing flow amounts
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=12, font_color='darkred',
                                 bbox=dict(boxstyle='round,pad=0.3', 
                                          facecolor='white', alpha=0.7), ax=ax)
    
    # Legend
    legend_elements = [
        Patch(facecolor='green', edgecolor='black', label=f'Source: Node {scf_source}'),
        Patch(facecolor='red', edgecolor='black', label=f'Destination: Node {scf_dest}'),
        Patch(facecolor='lightblue', edgecolor='black', label='Other Nodes'),
        plt.Line2D([0], [0], color='red', linewidth=4, label='Flow Path (thickness ∝ flow)'),
        plt.Line2D([0], [0], color='lightgray', linewidth=2, label='Unused Links')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.95)
    
    # Title
    plt.title(f"Single-Commodity Flow (SCF) Solution\n"
              f"Node {scf_source} → Node {scf_dest} | Demand: {scaled_demand:.1f} Mbps | "
              f"Scaling: {scf_scaling:.3f} | Total Cost: {total_flow_used:.2f}",
              fontsize=14, fontweight='bold', pad=20)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('SCF_flow_diagram.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: SCF_flow_diagram.png")
    plt.close()

# ============================================================
# STEP 8: VISUALIZATION - MCF Flow Diagram (Enhanced with Color Coding)
# ============================================================

if flow_vars_mcf and mcf_flow_data:
    print("Generating enhanced MCF visualization with color-coded commodities...")
    
    # Create a larger figure to accommodate the detailed legend
    fig, ax = plt.subplots(figsize=(18, 14))
    
    # Layout (same as SCF for consistency)
    pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)
    
    # Collect all source and destination nodes from commodities
    mcf_sources = set(c['source'] for c in scaled_comms)
    mcf_dests = set(c['dest'] for c in scaled_comms)
    
    # Define distinct colors for each commodity
    commodity_colors = {
        1: 'red',
        2: 'blue', 
        3: 'green',
        4: 'orange',
        5: 'purple'
    }
    
    # Determine node colors for MCF
    node_colors = []
    for node in G.nodes():
        if node in mcf_sources and node in mcf_dests:
            node_colors.append('gold')  # Both source and dest
        elif node in mcf_sources:
            node_colors.append('limegreen')
        elif node in mcf_dests:
            node_colors.append('lightcoral')
        else:
            node_colors.append('lightblue')
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=900, node_color=node_colors,
                          edgecolors='black', linewidths=2, ax=ax)
    
    # Node labels
    labels = {i: str(i) for i in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12,
                           font_weight='bold', ax=ax)
    
    # Draw all edges in light gray
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=2,
                          edge_color='lightgray', alpha=0.4, ax=ax)
    
    # Draw flow edges for each commodity with distinct colors
    edge_widths = []
    edge_colors = []
    flow_edges = []
    edge_labels = {}
    
    # First pass: collect all flow information
    commodity_flows = {k: [] for k in range(1, 6)}
    
    for comm in scaled_comms:
        k = comm['k']
        color = commodity_colors[k]
        
        for (i, j) in G.edges():
            flow_ij = pulp.value(flow_vars_mcf[(k, i, j)])
            flow_ji = pulp.value(flow_vars_mcf[(k, j, i)])
            
            if flow_ij > 0.01:
                commodity_flows[k].append(((i, j), flow_ij, color))
            
            if flow_ji > 0.01:
                commodity_flows[k].append(((j, i), flow_ji, color))
    
    # Draw flows commodity by commodity (thicker lines for higher flows)
    for k in range(1, 6):
        for (edge, flow, color) in commodity_flows[k]:
            flow_edges.append(edge)
            edge_widths.append(max(2, flow / 3))  # Scale width
            edge_colors.append(color)
    
    # Draw all flow edges
    nx.draw_networkx_edges(G, pos, edgelist=flow_edges, width=edge_widths,
                          edge_color=edge_colors, alpha=0.7, arrows=True,
                          arrowsize=15, arrowstyle='->', ax=ax)
    
    # Edge labels showing capacity (same as your original format)
    for (i, j) in G.edges():
        capacity = G[i][j]['capacity']
        edge_labels[(i,j)] = f"{capacity}"
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=8, font_color='darkblue',
                                 bbox=dict(boxstyle='round,pad=0.3',
                                          facecolor='white', alpha=0.7), ax=ax)
    
    # Enhanced legend
    commodity_legend = [plt.Line2D([0], [0], color=commodity_colors[k], linewidth=4, 
                                  label=f"K{k}: Node {mcf_commodities[k-1]['source']}→{mcf_commodities[k-1]['dest']} ({mcf_commodities[k-1]['demand']} Mbps)") 
                       for k in range(1, 6)]
    
    node_legend_elements = [
        Patch(facecolor='limegreen', edgecolor='black', label='Source Nodes'),
        Patch(facecolor='lightcoral', edgecolor='black', label='Destination Nodes'),
        Patch(facecolor='gold', edgecolor='black', label='Source & Destination'),
        Patch(facecolor='lightblue', edgecolor='black', label='Intermediate Nodes'),
        plt.Line2D([0], [0], color='lightgray', linewidth=2, label='Unused Links')
    ]
    
    # Create two legends
    legend1 = ax.legend(handles=commodity_legend, loc='upper left', 
                       fontsize=10, framealpha=0.95, title="Commodity Flows",
                       title_fontsize=11)
    
    ax.add_artist(legend1)
    
    ax.legend(handles=node_legend_elements, loc='upper right', 
              fontsize=10, framealpha=0.95, title="Node Types",
              title_fontsize=11)
    
    # Title with detailed information
    total_scaled_demand = sum(c['demand'] for c in scaled_comms)
    total_original_demand = sum(c['demand'] for c in mcf_commodities)
    
    plt.title(f"Multi-Commodity Flow (MCF) Solution - Color-Coded Commodities\n"
              f"Total Demand: {total_scaled_demand:.1f} Mbps (Original: {total_original_demand} Mbps) | "
              f"Scaling Factor: {mcf_scaling:.3f}\n"
              f"Objective Value: {pulp.value(prob_mcf.objective):.2f}",
              fontsize=13, fontweight='bold', pad=25)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('MCF_flow_diagram_color_coded.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: MCF_flow_diagram_color_coded.png")
    
    # Also create a simplified version showing only the main flow paths
    fig2, ax2 = plt.subplots(figsize=(16, 12))
    
    # Draw the same base network
    nx.draw_networkx_nodes(G, pos, node_size=900, node_color=node_colors,
                          edgecolors='black', linewidths=2, ax=ax2)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12,
                           font_weight='bold', ax=ax2)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=2,
                          edge_color='lightgray', alpha=0.3, ax=ax2)
    
    # Draw only significant flows (above 10 Mbps) for clarity
    significant_flow_edges = []
    significant_edge_widths = []
    significant_edge_colors = []
    
    for k in range(1, 6):
        color = commodity_colors[k]
        for (edge, flow, _) in commodity_flows[k]:
            if flow > 10:  # Only show flows > 10 Mbps
                significant_flow_edges.append(edge)
                significant_edge_widths.append(max(2, flow / 5))
                significant_edge_colors.append(color)
    
    nx.draw_networkx_edges(G, pos, edgelist=significant_flow_edges, 
                          width=significant_edge_widths, edge_color=significant_edge_colors, 
                          alpha=0.8, arrows=True, arrowsize=20, arrowstyle='->', ax=ax2)
    
    # Edge labels showing capacity (same as original)
    for (i, j) in G.edges():
        capacity = G[i][j]['capacity']
        edge_labels[(i,j)] = f"{capacity}"
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=8, font_color='darkblue',
                                 bbox=dict(boxstyle='round,pad=0.3',
                                          facecolor='white', alpha=0.7), ax=ax2)
    
    # Simplified legend
    ax2.legend(handles=commodity_legend, loc='upper left', 
               fontsize=10, framealpha=0.95, title="Commodity Flows (>10 Mbps)")
    
    plt.title(f"MCF Solution - Main Flow Paths (>10 Mbps)\n"
              f"Scaling Factor: {mcf_scaling:.3f} | Total Cost: {pulp.value(prob_mcf.objective):.2f}",
              fontsize=14, fontweight='bold', pad=20)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('MCF_main_flows.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: MCF_main_flows.png")
    plt.close('all')

print("\n" + "="*60)
print("ENHANCED MCF VISUALIZATIONS COMPLETE")
print("="*60)
print("Generated MCF files:")
print("  • MCF_result.csv")
print("  • LinkUtilisation.csv") 
print("  • MCF_flow_diagram_color_coded.png (detailed, color-coded)")
print("  • MCF_main_flows.png (simplified, main paths only)")