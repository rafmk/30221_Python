from data_generator import DataGenerator
from EDAC import *

dataset = DataGenerator(18, 8, 10, 12345)
dataset.generate_clean()
dataset.generate_errors(dataset.clean)
print(dataset.clean)
print(dataset.dirty)
print(dataset.dirty.hex())
