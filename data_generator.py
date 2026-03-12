import numpy as np

class DataGenerator:
    def __init__(self, data_size, base = 8):
        self.data_size = data_size # total number of characters
        self.base = base # character base (nr of bits per character)


    def generate_clean(self, seed=None):
        rng = np.random.default_rng(seed)  # seed for generating bytes
        return rng.integers(0, 2 ** self.base, size=self.data_size, dtype=np.uint8) # generate clean data


    def generate_errors(self, data, rate_type= 'bits', error_rate = 0, seed=None):

        match rate_type:
            case 'bits':
                # error rate is given in nr of bits
                error_rate = error_rate

            case 'percentage':
                # error rate is given in percentage
                error_rate = round(error_rate / 100 * self.data_size * self.base)


        rng = np.random.default_rng(seed)  # seed for generating error positions
        error_positions = rng.integers(0, self.data_size * self.base, size=error_rate) # generate bit positions of flips
        for error_position in error_positions:
            index, bit = divmod(error_position, self.base)  # find position within array of bytes
            data[index] ^= 1 << bit # flip bit in corresponding index and position





