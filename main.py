from data_generator import DataGenerator

dataset = DataGenerator(100, 100, 12345)
dataset.generate_clean()
print(dataset.clean)
dataset.generate_errors()
print(dataset.dirty)