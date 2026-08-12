import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# --- 1. Load NSFNET Topology from CSV ---
print("Loading NSFNET topology from CSV...")
nsfnet_df = pd.read_csv("NSFNET_Links.csv")
print(f"Loaded {len(nsfnet_df)} edges from NSFNET_Links.csv")
print(nsfnet_df.head())
print()

# --- 2. Build Graph from CSV ---
G = nx.Graph()
for _, row in nsfnet_df.iterrows():
    source_node = int(row['Source'])
    dest_node = int(row['Destination'])
    weight = int(row['Weight'])
    capacity = int(row['Capacity_Mbps'])
    G.add_edge(source_node, dest_node, Weight=weight, Capacity=capacity)

print(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print()

# --- 3. Load SCF CSV (Source & Destination Nodes) ---
scf = pd.read_csv("scf_222170972.csv")
source = int(scf.loc[0, "source"])
target = int(scf.loc[0, "destination"])
print(f"Source node: {source} (Los Angeles)")
print(f"Destination node: {target} (Ann Arbor)")
print()

# --- 4. Compute Shortest Path (Dijkstra) ---
path = nx.shortest_path(G, source=source, target=target, weight="Weight")
cost = nx.shortest_path_length(G, source=source, target=target, weight="Weight")
print("Shortest path sequence:", " → ".join(map(str, path)))
print(f"Total path cost (sum of weights): {cost}")
print()

# --- 5. City Labels (Optional: use numbers or city names) ---
city_labels = {
    1: "1 (SF)", 2: "2 (PA)", 3: "3 (LA)", 4: "4 (DEN)",
    5: "5 (HOU)", 6: "6 (CHI)", 7: "7 (AA)", 8: "8 (PIT)",
    9: "9 (ITH)", 10: "10 (NY)", 11: "11 (PRI)", 12: "12 (CP)",
    13: "13 (ATL)", 14: "14 (SD)"
}

# Use simple numbers if preferred
# city_labels = {i: str(i) for i in range(1, 15)}

# --- 6. Layout (Spring layout with fixed seed for consistency) ---
pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)

# --- 7. Visualization with Color-Coded Nodes ---
plt.figure(figsize=(14, 10))

# Prepare node colors
node_colors = []
for node in G.nodes():
    if node == source:
        node_colors.append('green')  # Source node
    elif node == target:
        node_colors.append('red')    # Destination node
    elif node in path:
        node_colors.append('orange') # Intermediate nodes in path
    else:
        node_colors.append('lightblue')  # Other nodes

# Draw nodes with different colors
nx.draw_networkx_nodes(G, pos, node_size=900, node_color=node_colors, 
                       edgecolors='black', linewidths=2)

# Draw node labels
nx.draw_networkx_labels(G, pos, labels=city_labels, font_size=8, font_weight='bold')

# Draw all edges in light gray
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=5, edge_color="lightgray", alpha=0.6)

# Highlight edges in the shortest path in red
path_edges = list(zip(path, path[1:]))
nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=5, edge_color="red", alpha=0.9)

# Draw edge labels (weights)
edge_labels = {(u, v): d["Weight"] for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="darkgreen", 
                             font_size=13, font_weight='bold')

# --- 8. Add Legend/Key ---
legend_elements = [
    Patch(facecolor='green', edgecolor='black', label=f'Source Node ({source})'),
    Patch(facecolor='red', edgecolor='black', label=f'Destination Node ({target})'),
    Patch(facecolor='orange', edgecolor='black', label='Intermediate Path Nodes'),
    Patch(facecolor='lightblue', edgecolor='black', label='Other Nodes'),
    plt.Line2D([0], [0], color='red', linewidth=5, label='Shortest Path'),
    plt.Line2D([0], [0], color='lightgray', linewidth=2, label='Other Links')
]

plt.legend(handles=legend_elements, loc='upper left', fontsize=10, framealpha=0.9)

# --- 9. Title and Formatting ---
plt.title(
    f"NSFNET Shortest Path: Node {source} (Los Angeles) → Node {target} (Ann Arbor)\n"
    f"Path: {' → '.join(map(str, path))} | Total Cost: {cost}",
    fontsize=14, fontweight='bold', pad=20
)

plt.tight_layout()
plt.axis("off")

# --- 10. Save and Display ---
plt.savefig("shortest_path_nsfnet.png", dpi=300, bbox_inches='tight')
print("✓ Graph saved as 'shortest_path_nsfnet.png'")
plt.show()

# --- 11. Optional: Print Path Details ---
print("\n" + "="*60)
print("SHORTEST PATH DETAILS")
print("="*60)
for i in range(len(path) - 1):
    u, v = path[i], path[i+1]
    weight = G[u][v]['Weight']
    capacity = G[u][v]['Capacity']
    print(f"Step {i+1}: Node {u} → Node {v} | Weight: {weight} | Capacity: {capacity} Mbps")
print("="*60)