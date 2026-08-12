import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# DATA FROM YOUR RESULTS
# ============================================================

# SCF Data
scf_utilization = [75.50, 75.50, 75.50, 100.00, 100.00, 75.50, 100.00, 100.00, 100.00, 100.00]
scf_total_cost = 1217.69
scf_avg_utilization = 90.20

# MCF Data  
mcf_utilization = [100.00, 57.89, 85.65, 100.00, 100.00, 90.43, 100.00, 100.00, 
                   100.00, 100.00, 100.00, 100.00, 90.43, 100.00, 20.57, 57.89, 
                   20.57, 79.43, 57.89, 100.00]
mcf_total_cost = 2845.77
mcf_avg_utilization = 83.04

# ============================================================
# FIGURE 7: Histogram of Link Utilisation Values
# ============================================================

plt.figure(figsize=(12, 8))

# Combine both SCF and MCF utilization for overall histogram
all_utilization = scf_utilization + mcf_utilization

# Create histogram
n, bins, patches = plt.hist(all_utilization, bins=12, alpha=0.7, color='purple', 
                           edgecolor='black', density=False, rwidth=0.85)

plt.xlabel('Link Utilization (%)', fontsize=12, fontweight='bold')
plt.ylabel('Number of Links', fontsize=12, fontweight='bold')
plt.title(' Histogram of Link Utilisation Values\n(Combined SCF and MCF Results)', 
          fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

# Add count labels on histogram bars
for i, (count, patch) in enumerate(zip(n, patches)):
    if count > 0:
        plt.text(patch.get_x() + patch.get_width()/2, count + 0.2, 
                 f'{int(count)}', ha='center', va='bottom', fontweight='bold', fontsize=10)

# Add vertical lines for averages
plt.axvline(np.mean(scf_utilization), color='red', linestyle='--', linewidth=2, 
            label=f'SCF Average: {np.mean(scf_utilization):.1f}%')
plt.axvline(np.mean(mcf_utilization), color='blue', linestyle='--', linewidth=2, 
            label=f'MCF Average: {np.mean(mcf_utilization):.1f}%')
plt.axvline(np.mean(all_utilization), color='green', linestyle='-', linewidth=2, 
            label=f'Overall Average: {np.mean(all_utilization):.1f}%')

plt.legend(loc='upper left', framealpha=0.9)
plt.tight_layout()
plt.savefig('Figure7_Histogram_Link_Utilisation.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================
# FIGURE 8: Bar Chart Comparing SCF and MCF Total Costs
# ============================================================

plt.figure(figsize=(10, 8))

# Data for the bar chart
models = ['Single-Commodity Flow (SCF)', 'Multi-Commodity Flow (MCF)']
costs = [scf_total_cost, mcf_total_cost]
colors = ['#FF6B6B', '#4ECDC4']  # Red and teal colors

# Create bar chart
bars = plt.bar(models, costs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

plt.ylabel('Total Cost', fontsize=12, fontweight='bold')
plt.title('Comparison of SCF and MCF Total Costs', 
          fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar, cost in zip(bars, costs):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
             f'{cost:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=12)

# Add percentage difference annotation
cost_difference = ((mcf_total_cost - scf_total_cost) / scf_total_cost) * 100
plt.annotate(f'MCF cost is {cost_difference:+.1f}% higher than SCF', 
             xy=(0.5, 0.85), xycoords='axes fraction',
             ha='center', va='center', fontsize=11, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))

# Add some additional statistics below the bars
plt.text(0.5, -0.15, f'SCF: Node 3 → 7 | Scaled Demand: 124.0 Mbps\nMCF: 5 Commodities | Total Scaled Demand: 292.8 Mbps', 
         ha='center', va='center', transform=plt.gca().transAxes, fontsize=10,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7))

plt.tight_layout()
plt.savefig('Figure8_BarChart_Cost_Comparison.png', dpi=300, bbox_inches='tight')
plt.show()

print("=" * 60)
print("FIGURES 7 AND 8 GENERATED SUCCESSFULLY")
print("=" * 60)
print("Generated files:")
print("• Figure7_Histogram_Link_Utilisation.png")
print("• Figure8_BarChart_Cost_Comparison.png")
print("=" * 60)
print(f"SCF Statistics:")
print(f"  • Average Utilization: {scf_avg_utilization}%")
print(f"  • Total Cost: {scf_total_cost}")
print(f"  • Number of Links: {len(scf_utilization)}")
print(f"MCF Statistics:")
print(f"  • Average Utilization: {mcf_avg_utilization}%")
print(f"  • Total Cost: {mcf_total_cost}")
print(f"  • Number of Links: {len(mcf_utilization)}")
print(f"Combined Statistics:")
print(f"  • Overall Average Utilization: {np.mean(all_utilization):.2f}%")
print(f"  • Cost Difference: {cost_difference:+.1f}%")
print("=" * 60)