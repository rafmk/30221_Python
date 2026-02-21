from data_generator import DataGenerator
from EDAC import *
import crc

dataset = DataGenerator(18, 8, 1)
clean = dataset.generate_clean()




crc_config = crc.Configuration(
    width=8,
    polynomial=0xA6,
    init_value=0x00,
    final_xor_value=0x00,
    reverse_input=False,
    reverse_output=False
)

crc_instance = crc.Calculator(crc_config)
codeword_clean = crc_instance.checksum(bytes(clean))
print(clean)
print(codeword_clean)
np.append(clean, codeword_clean)
print(clean)
#print(crc_instance.verify(bytes(dataset.dirty), ))
