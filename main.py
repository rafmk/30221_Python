from data_generator import DataGenerator
from EDAC import *
import crc
from FletcherChecksumLib import FletcherChecksumBytes
from reedsolo import *

dataset = DataGenerator(18, 8, 10)
clean = dataset.generate_clean()

#Parity
data = [246, 111, 119,  81, 205, 212,  67,  28,  75, 106, 168,  16, 180, 185, 117, 209, 128,  78]
print(clean)
print(Parity(clean).parity_calc())

#Fletcher
fl_instance = FletcherChecksumBytes
fl_codeword = fl_instance.get_fletcher16(bytes(clean))
print(fl_codeword)

#CRC
crc_config = crc.Configuration(
    width=8,
    polynomial=0xA6,
    init_value=0x00,
    final_xor_value=0x00,
    reverse_input=False,
    reverse_output=False
)
crc_instance = crc.Calculator(crc_config)
crc_codeword = crc_instance.checksum(bytes(clean))


#Reedsolo


