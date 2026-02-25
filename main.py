from testing import *
# just keeping thios for later print(format(byte, '08b'))

rounds = 100
parity = np.zeros(100)
crc8 = np.zeros(100)
fletcher16 = np.zeros(100)
error_rates = np.arange(0, 100, 1)
for error_rate in error_rates:
    sim = Test(rounds)
    sim.sim_inst(error_rate)
    parity[error_rate] = sim.det_parity
    crc8[error_rate] = sim.det_crc8
    fletcher16[error_rate] = sim.det_fletcher

plt.plot(error_rates, parity, 'o-', linewidth=2, markersize=8, label='parity')
plt.plot(error_rates, crc8, 's-', linewidth=2, markersize=8, label='crc8')
plt.plot(error_rates, fletcher16, '^-', linewidth=2, markersize=8, label='fletcher16')

plt.xlabel('Error Rate (%)')
plt.ylabel(f'Number of Errors Detected after {rounds} rounds')
plt.title('EDAC Method Performance Across Error Rates')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim(-5, 105)
plt.ylim(0, 110)
plt.show()



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



