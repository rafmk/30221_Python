import numpy as np

class DataGenerator:
    def __init__(self, data_size, seed=None):
        self.seed = seed
        self.data_size = data_size
        self.rng = np.random.default_rng(self.seed)

    def generate_bytes(self):
        self.bytes = self.rng.integers(0, 256, size=self.data_size, dtype=np.uint8)




class FixedErrorGenerator(DataGenerator):
    def __init__(self, byte_length, data_size, seed=None):
        DataGenerator.__init__(self, byte_length, data_size, seed)

    def

class RandomErrorGenerator(DataGenerator):
    def __init__(self, byte_length, data_size, seed=None):
        DataGenerator.__init__(self, byte_length, data_size, seed)


