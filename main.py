
import matplotlib.pyplot as plt
from EDAC import *
from data_generator import DataGenerator
from testing import parity, fletcher, crc8, rs, hamming
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

        # Total errors injected (for detection rate calculation)
        self.total_errors_injected = 0

    def sim_rounds(self, error_rate):
        # runs simulation across nr of specified rounds at fixed error_rate

        results = {
            'parity': {'detection': [], 'correction': []},
            'fletcher16': {'detection': [], 'correction': []},
            'crc8': {'detection': [], 'correction': []},
            'hamming_32_26': {'detection': [], 'correction': []},
        }

        for rnd in tqdm(range(self.rounds), desc=f"Error rate {error_rate}"):
            seed_rnd = rnd  # use the same seed for error generation across all EDAC methods

            # parity
            self.det_parity = parity(self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd)
            results['parity']['detection'].append(self.det_parity)

            # checksum8

            # fletcher16
            self.det_fletcher = fletcher(self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd)
            results['fletcher16']['detection'].append(int(self.det_fletcher))

            # crc8
            self.det_crc8 = (
                crc8(0xA6, self.data_generator, self.clean, self.error_rate_type, error_rate, seed_rnd))
            results['crc8']['detection'].append(int(self.det_crc8))

            # crc16

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
error_rates = [10, 20, 30]

# Create test instance
tester = Test(nr_of_bytes, rounds, error_rate_type)
simulation_results = tester.run_simulation(error_rates)

methods = list(next(iter(simulation_results.values())).keys())
error_rates = list(simulation_results.keys())

x = np.arange(len(error_rates))
width = 0.18

plt.figure(figsize=(12,6))

for i, method in enumerate(methods):

    avg = [simulation_results[er][method][0] for er in error_rates]
    minv = [simulation_results[er][method][1] for er in error_rates]
    maxv = [simulation_results[er][method][2] for er in error_rates]

    pos = x + i * width

    plt.bar(pos, avg, width, label=method)
    plt.scatter(pos, minv, color="black", marker="_", s=200)
    plt.scatter(pos, maxv, color="black", marker="_", s=200)

plt.xticks(x + width*(len(methods)-1)/2, error_rates)
plt.xlabel("Error Rate")
plt.ylabel("Detected Errors (bits)")
plt.title("EDAC Detection Performance")

plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout()
plt.show()














