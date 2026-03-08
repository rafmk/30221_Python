import numpy as np
import matplotlib.pyplot as plt

def extended_hamming_params(r):
    n = 2 ** r  # Codeword size
    k = n - r - 1  # Data bits
    return n, k, r


def find_best_code_for_data(data_size=144, r_min=3, r_max=8):
    results = []

    for r in range(r_min, r_max + 1):
        n, k, r_parity = extended_hamming_params(r)

        # Calculate how many code blocks needed
        num_blocks = (data_size + k - 1) // k

        # Total capacity with this many blocks
        total_data_capacity = num_blocks * k

        # Empty data bits (wasted capacity in the data portion)
        empty_bits = total_data_capacity - data_size

        # Total bits transmitted
        total_bits_transmitted = num_blocks * n

        # Total overhead (everything beyond the original 144 data bits)
        total_overhead_bits = total_bits_transmitted - data_size

        # Overhead percentage relative to original data
        overhead_pct = (total_overhead_bits / data_size) * 100

        results.append({
            'r': r,
            'k': k,
            'n': n,
            'num_blocks': num_blocks,
            'empty_bits': empty_bits,
            'total_parity': num_blocks * r_parity,
            'total_overhead_bits': total_overhead_bits,
            'overhead_pct': overhead_pct,
            'total_bits': total_bits_transmitted
        })

    return results


# Calculate results for 144-bit data
data_size = 144
results = find_best_code_for_data(data_size)

# Color map for different r values
colors = plt.cm.viridis(np.linspace(0, 1, len(results)))

# Plot 1: Overhead vs Empty Bits (main plot)
for i, result in enumerate(results):
    scatter = plt.scatter(result['empty_bits'],
                          result['overhead_pct'],
                          color=colors[i],
                          s=200,
                          label=f'r={result["r"]} (n={result["n"]}, k={result["k"]})',
                          alpha=0.7,
                          edgecolors='black',
                          linewidth=2)

# Customize the first plot
plt.xlabel('Empty Data Bits', fontsize=12, fontweight='bold')
plt.ylabel('Overhead (%)', fontsize=12, fontweight='bold')
#plt.title(f'Extended Hamming Code Efficiency for {data_size}-bit Data', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(loc='upper right', fontsize=9, framealpha=0.9)

plt.show()

