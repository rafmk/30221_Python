from testing import *
# just keeping this for later print(format(byte, '08b'))

'''rounds = 100
error_rates = np.arange(0, 100, 1)
parity = np.zeros(len(error_rates))
crc8 = np.zeros(len(error_rates))
fletcher16 = np.zeros(len(error_rates))
for error_rate in error_rates:
    sim = Test(rounds)
    sim.sim_inst(error_rate)
    parity[error_rate] = sim.det_parity / rounds
    crc8[error_rate] = sim.det_crc8 / rounds
    fletcher16[error_rate] = sim.det_fletcher / rounds

plt.plot(error_rates, parity, 'o-', linewidth=2, markersize=8, label='parity')
plt.plot(error_rates, crc8, 's-', linewidth=2, markersize=8, label='crc8')
plt.plot(error_rates, fletcher16, '^-', linewidth=2, markersize=8, label='fletcher16')

plt.xlabel('Error Rate (%)')
plt.ylabel(f'Number of Errors Detected after {rounds} rounds')
plt.title('EDAC Method Performance Across Error Rates')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()'''

#hm = Hamming(list(range(15)), 7)
hm = Hamming([15], 3)
hm.encode()
print([format(i, '08b') for i in list(hm.total_packet)])
print([format(i, '08b') for i in [0b00111111]])
print([format(i, '08b') for i in list(hm.decode([0b00111111]))])

hm = Hamming([15], 3)
hm.encode()
encoded_packet = list(hm.total_packet)
print("Encoded:", [format(i, '08b') for i in encoded_packet])

# Introduce a single-bit error at bit index 2 (0-based)
error_packet = encoded_packet.copy()
error_packet[0] ^= 0b00000100  # flip bit 2
print("With Error:", [format(i, '08b') for i in error_packet])

# Decode
decoded_packet = hm.decode(error_packet)
print("Decoded:", [format(i, '08b') for i in decoded_packet])



'''### Generate data ###

# Setup data generator, set error rate
DG = DataGenerator(18)
error_rate = 50  # %
print("@ 50% error rate 50% of bits in the complete message will experience a flip")

# Grab clean data
clean = DG.generate_clean()

###UART Parity clone###

# Grab parity bytes
parity_bytes = np.array(Parity(clean).parity_calc(), dtype=np.uint8)

# Combine clean + parity bytes & feed to error generator
clean_plus_p = np.append(clean, parity_bytes)
#print(clean_plus_p)
DG.generate_errors(clean_plus_p, error_rate)
#print(DG.dirty)

# Grab dirty array and feed to Parity calc
PD = Parity(clean_plus_p)
PD.check_parity(len(parity_bytes))
print("Parity error detection: ", PD.error_detection, "errors detected")


###Fletcher###

# Setup instance
FL = FletcherChecksumBytes

# Calculate fletcher 16 for clean data
fl_clean = FL.get_fletcher16(bytes(clean))
fl_h = (fl_clean['Fletcher16_dec'] >> 8) & 0xff
fl_l = fl_clean['Fletcher16_dec'] & 0xff

# Combine clean + parity bytes & feed to error generator
clean_plus_fl = np.append(clean, np.array([fl_h, fl_l], dtype=np.uint8))


# Generate errors
DG.generate_errors(clean_plus_fl, error_rate)
# Possibly erroneous fletcher16 values
fl_h_tx, fl_l_tx = clean_plus_fl[-2:]

# Calculate fletcher16 values for incoming data and check against sent values
fl_dirty = FL.get_fletcher16(bytes(clean_plus_fl[:-2]))
fl_h_rx = (fl_dirty['Fletcher16_dec'] >> 8) & 0xff
fl_l_rx = fl_dirty['Fletcher16_dec'] & 0xff

if fl_h_tx != fl_h_rx or fl_l_tx != fl_l_rx:
    print("Fletcher error detection: ", "error detected")


#CRC

# Setup instance with desired settings
crc_config = crc.Configuration(
    width=8,
    polynomial=0xA6,
    init_value=0x00,
    final_xor_value=0x00,
    reverse_input=False,
    reverse_output=False
)
CRC = crc.Calculator(crc_config)

# Calculate crc value
crc_word = CRC.checksum(bytes(clean))

# Combine clean + crc word & feed to error generator
clean_plus_crc = np.append(clean, np.uint8(crc_word))

# Generate errors
DG.generate_errors(clean_plus_crc, error_rate)

# Check for errors
if not CRC.verify(bytes(clean_plus_crc[:-1]), clean_plus_crc[-1]):
    print("CRC8 error detection: ", "error detected")'''



