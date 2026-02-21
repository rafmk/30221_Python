import numpy as np

class DataGenerator:
    def __init__(self, data_size, base, error_rate, seed1=None, seed2=None):
        self.data_size = data_size # total number of characters
        self.base = base # character base (nr of bits per character)
        self.rng1 = np.random.default_rng(seed1) # seed for generating bytes
        self.error_rate = error_rate # error rate in %
        self.rng2 = np.random.default_rng(seed2) # seed for generating error positions

        # init variables
        self.clean = None
        self.dirty = None
        self.error_positions = None

    def generate_clean(self):
        self.clean = self.rng1.integers(0, 2 ** self.base, size=self.data_size, dtype=np.uint16) # generate clean data
        return self.clean

    def generate_errors(self, clean_data):
        self.dirty = clean_data.copy() # copy clean data
        self.error_positions = self.rng2.integers(0, self.data_size * self.base, size=round(self.error_rate / 100 * self.data_size * self.base)) # generate bit positions of flips
        for error_position in self.error_positions:
            index, bit = divmod(error_position, self.base)  # find position within array of bytes
            self.dirty[index] ^= 1 << bit # flip bit in corresponding index and position





