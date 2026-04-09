
import matplotlib.pyplot as plt
from EDAC import *
from data_generator import DataGenerator
from testing import parity, fletcher, crc8, crc16, rs, hamming, checksum
from tqdm import tqdm



class Test:
    def __init__(self, nr_of_bytes, rounds, error_rate_type):
        self.nr_of_bytes = nr_of_bytes
        self.rounds = rounds
        self.error_rate_type = error_rate_type

        # Initialize all counters to zero
        self.reset_counters()

        # initialize clean data
        self.data_generator = DataGenerator(self.nr_of_bytes)
        self.clean = self.data_generator.generate_clean()

    def reset_counters(self):
        """Reset all counters for a new simulation run"""
        # Detection counters
        self.det_parity = 0
        self.det_fletcher = 0
        self.det_checksum8 = 0
        self.det_crc8 = 0
        self.det_crc16 = 0
        self.det_hm_32_26 = 0
        self.det_hm_16_11 = 0
        self.det_hm_8_4 = 0
        self.det_rs = 0

        # Correction counters
        self.cor_hm_32_26 = 0
        self.cor_hm_16_11 = 0
        self.cor_hm_8_4 = 0
        self.cor_hm_4_3 = 0
        self.cor_rs = 0


    def sim_rounds(self, error_rate):
        # runs simulation across nr of specified rounds at fixed error_rate

        results = {
            'parity': {'detection': [], 'correction': []},
            'checksum8': {'detection': [], 'correction': []},
            'fletcher16': {'detection': [], 'correction': []},
            'crc8': {'detection': [], 'correction': []},
            'crc16': {'detection': [], 'correction': []},
            'hamming_8_4': {'detection': [], 'correction': []},
            'hamming_32_26': {'detection': [], 'correction': []}
        }

        for rnd in tqdm(range(self.rounds), desc=f"Error rate {error_rate}"):
            seed_rnd = rnd  # use the same seed for error generation across all EDAC methods

            # parity
            self.det_parity = parity(self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd)
            results['parity']['detection'].append(self.det_parity)

            # checksum8
            self.det_checksum8 = checksum(self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd)
            results['checksum8']['detection'].append(int(self.det_checksum8))

            # fletcher16
            self.det_fletcher = fletcher(self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd)
            results['fletcher16']['detection'].append(int(self.det_fletcher))

            # crc8
            self.det_crc8 = (
                crc8(0xA6, self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd))
            results['crc8']['detection'].append(int(self.det_crc8))

            # crc16
            self.det_crc16 = (
                crc16(0xAC9A, self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd))
            results['crc16']['detection'].append(int(self.det_crc16))

            # hamming (8, 4)
            self.det_hm_8_4, self.cor_hm_8_4 = (
                hamming(3, self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd))
            results['hamming_8_4']['detection'].append(self.det_hm_8_4)
            results['hamming_8_4']['correction'].append(self.cor_hm_8_4)

            # hamming (32,26)
            self.det_hm_32_26, self.cor_hm_32_26 = (
                hamming(5, self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd))
            results['hamming_32_26']['detection'].append(self.det_hm_32_26)
            results['hamming_32_26']['correction'].append(self.cor_hm_32_26)

            # rs(2)

        return results


    def run_simulation(self, error_rates):
        # Runs simulation across different error rates
        results = {}

        for error_rate in error_rates:
            results[error_rate] = {}

            # simulate rounds
            rounds_results = self.sim_rounds(error_rate)

            # compile results
            for key, value in rounds_results.items():
                det_avg = sum(value['detection']) / len(value['detection'])
                det_min = min(value['detection'])
                det_max = max(value['detection'])
                # std deviation, confidence interval, standard error

                #cor_avg = sum(value['correction']) / len(value['correction'])
                #cor_min = min(value['correction'])
                #cor_max = max(value['correction'])
                #results[error_rate][key] = [det_avg, det_min, det_max, cor_avg, cor_min, cor_max]
                results[error_rate][key] = [det_avg, det_min, det_max]

            # reset counters for round simulations
            self.reset_counters()

        return results




# Test parameters
nr_of_bytes = 18  # Bytes per round
rounds = 1000  # Number of rounds per error rate
error_rate_type = 'bits'  # Type of errors

# Error rates to test
error_rates = np.arange(1, 21, 1)

# Create test instance
tester = Test(nr_of_bytes, rounds, error_rate_type)
simulation_results = tester.run_simulation(error_rates)


def plot_ordered_simulation_results(simulation_results):
    # 1. Prepare base lists
    error_rates = sorted(list(simulation_results.keys()))
    # Access the first available error rate to get method keys
    all_methods = list(simulation_results[error_rates[0]].keys())

    # 2. Calculate the "Global Average" for sorting
    method_scores = {}
    for method in all_methods:
        avg_across_rates = np.mean([simulation_results[er][method][0] for er in error_rates])
        method_scores[method] = avg_across_rates

    # 3. Sort methods by their global average (ascending)
    sorted_methods = sorted(all_methods, key=lambda m: method_scores[m])

    # 4. Setup Plotting with a soft color palette
    fig, ax = plt.subplots(figsize=(12, 7))
    # Using 'Pastel1' or 'Set3' for professional, soft colors
    colors = plt.cm.viridis(np.linspace(0.3, 1, len(sorted_methods)))

    x = np.arange(len(error_rates))
    total_width = 0.8
    bar_width = total_width / len(sorted_methods)

    for i, method in enumerate(sorted_methods):
        avgs = [simulation_results[er][method][0] for er in error_rates]
        mins = [simulation_results[er][method][1] for er in error_rates]
        maxs = [simulation_results[er][method][2] for er in error_rates]

        # Calculate error bar heights
        yerr = [
            [a - m for a, m in zip(avgs, mins)],
            [M - a for a, M in zip(avgs, maxs)]
        ]

        offset = (i - (len(sorted_methods) - 1) / 2) * bar_width

        # Plot bars with softer edge colors and the chosen palette
        ax.bar(x + offset, avgs, bar_width, label=method,
               yerr=yerr, capsize=4, color=colors[i], edgecolor='gray', linewidth=0.5)


    # 5. Finalize Chart Labels
    ax.set_xlabel(f'Error Rate ({error_rate_type})')
    ax.set_ylabel('Detections \n (for checksums 1 indicates a detection across the entire message)')
    ax.set_title(f'EDAC Method Performance for Data Packet size of {nr_of_bytes} bytes')
    ax.set_xticks(x)
    ax.set_xticklabels(error_rates)

    # 6. Indication of error bar meaning
    # Placing a text box in the upper right
    explanation_text = "Error bars represent\nMinimum and Maximum\ndetections per round."
    ax.text(0.02, 0.6, explanation_text, transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.5, edgecolor='gray'))

    ax.legend(title="Methods (Sorted by Avg)", loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.show()


# Run the plot
plot_ordered_simulation_results(simulation_results)














