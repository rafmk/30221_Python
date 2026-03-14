import numpy as np

class DataGenerator:
    def __init__(self, data_size):
        self.data_size = data_size # total number of characters

    def generate_clean(self, seed=None):
        rng = np.random.default_rng(seed)  # seed for generating bytes
        return rng.integers(0, 256, size=self.data_size, dtype=np.uint8) # generate clean data


    def generate_errors(self, input_data, rate_type= 'bits', error_rate = 0, seed=None):
        match rate_type:
            case 'bits':
                # error rate is given in nr of bits
                error_rate = error_rate

            case 'percentage':
                # error rate is given in percentage
                error_rate = round(error_rate / 100 * self.data_size * self.base)


        rng = np.random.default_rng(seed)  # seed for generating error positions
        error_positions = rng.integers(0, len(input_data), size=error_rate, dtype=np.uint8)  # generate positions of bit flips
        input_data[error_positions] ^= True  # flip bits







