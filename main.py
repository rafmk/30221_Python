from data_generator import DataGenerator
from EDAC import *
import crc
from FletcherChecksumLib import FletcherChecksumBytes
from reedsolo import *

#Parity
#data = [246, 111, 119,  81, 205, 212,  67,  28,  75, 106, 168,  16, 180, 185, 117, 209, 128,  78]
#for int in clean: print(format(int, '08b'))

# Setup data generator, set error rate
DG = DataGenerator(18, 8, 50)
DG.generate_clean()

# Grab clean data
clean = DG.clean


# Grab parity bytes
parity_bytes = np.array(Parity(clean).parity_calc())


# Combine clean + parity bytes & feed to error generator
clean_plus_p = np.append(clean, parity_bytes)
print(clean_plus_p)
DG.generate_errors(clean_plus_p)
print(DG.dirty)

# Grab dirty array and feed to Parity calc
PD = Parity(DG.dirty)
PD.check_parity(len(parity_bytes))
print(PD.error_detection)


#Fletcher
fl_instance = FletcherChecksumBytes
fl_codeword = fl_instance.get_fletcher16(bytes(clean))
#print(fl_codeword)

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


