import numpy as np


def flip_bit(value, pos):
    return value ^ (1 << pos)


class DataGenerator:
    def __init__(self, data_size, error_rate, seed1=None, seed2=None):
        self.bytes = None
        self.data_size = data_size
        self.rng = np.random.default_rng(seed1)
        self.error_positions = None
        self.error_rate = error_rate
        self.rng2 = np.random.default_rng(seed2)

    def generate_clean(self):
        self.clean = self.rng.integers(0, 256, size=self.data_size, dtype=np.uint8)

    def generate_errors(self):
        self.dirty = self.clean
        #error_rate in %
        self.error_positions = self.rng2.integers(0, self.data_size * 8, size=int(self.error_rate / 100 * self.data_size * 8))

        for error_position in self.error_positions:
            index, bit = divmod(error_position, 8)
            if bit == 0:
                #flip bit 8 of indexed integer
                flip_bit(self.dirty[index], 7)
                break

            else:
                #flip bit of (index + 1) at position (bit - 1)
                flip_bit(self.dirty[index + 1], bit - 1)
                break


