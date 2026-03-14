from EDAC import *
from FletcherChecksumLib import FletcherChecksumBytes
import crc
from reedsolo import RSCodec

def parity(DG, clean, error_rate_type, error_rate, seed):

    # Instance of parity class
    UART_parity = Parity(clean)
    # calculate parities and modify message
    UART_parity.parity_calc()
    # generate errors within message, returns message with bit flips
    DG.generate_errors(UART_parity.message, error_rate_type, error_rate, seed)

    detected_errors = UART_parity.check_parity(UART_parity.message)

    # Returns nr of blocks with errors detected in it
    return detected_errors


def checksum(DG, clean, error_rate_type, error_rate, seed):
    # instance of checksum8 class
    checksum8 = Checksum(clean)

    # calculate checksum and assign to message
    checksum8.calc_checksum(checksum8.message)

    # modify message and insert errors
    DG.generate_errors(checksum8.message, error_rate_type, error_rate, seed)

    # returns True if mismatched (error detected)
    return checksum8.calc_checksum(checksum8.message)


def fletcher(DG, clean, error_rate_type, error_rate, seed):

    # Instance of fletcher class
    fletcher16 = FletcherChecksumBytes

    # Calculate fletcher 16 for clean data
    fl_clean = fletcher16.get_fletcher16(bytes(clean))
    fl_h = (fl_clean['Fletcher16_dec'] >> 8) & 0xff
    fl_l = fl_clean['Fletcher16_dec'] & 0xff

    # Combine fletcher16 codeword with bytes, then convert to bits
    message_bytes = np.append(np.array([fl_l, fl_h], dtype=np.uint8), clean)
    message_bits = np.unpackbits(message_bytes, bitorder="little")

    # Generate errors & convert back to bytes
    DG.generate_errors(message_bits, error_rate_type, error_rate, seed)
    message_bytes = np.packbits(message_bits, bitorder="little")
    # Possibly erroneous fletcher16 values
    fletcher_tx_l, fletcher_tx_h = message_bytes[:2]

    # Re-calculate fletcher16 value for received data
    fletcher_rx = fletcher16.get_fletcher16(bytes(message_bytes[2:]))
    fletcher_rx_h = (fletcher_rx['Fletcher16_dec'] >> 8) & 0xff
    fletcher_rx_l = fletcher_rx['Fletcher16_dec'] & 0xff

    # Returns true (1) based on a detected error
    return fletcher_rx_h != fletcher_tx_h or fletcher_tx_l != fletcher_rx_l


def crc8(polynomial, DG, clean, error_rate_type, error_rate, seed):

    # Setup instance with desired settings
    crc_config = crc.Configuration(
        width=8,
        polynomial=polynomial,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input=False,
        reverse_output=False
    )
    crc8_instance = crc.Calculator(crc_config)

    # Calculate crc8 word from bytes
    crc_word = crc8_instance.checksum(bytes(clean))

    # Combine crc word + bytes and convert to bits
    message_bytes = np.append(np.uint8(crc_word), clean)
    message_bits = np.unpackbits(message_bytes, bitorder="little")

    # Generate errors and convert back to bytes
    DG.generate_errors(message_bits, error_rate_type, error_rate, seed)
    message_bytes = np.packbits(message_bits, bitorder="little")

    # Returns true based on a detected error, crc.verify returns the inverse: false == error hence, the "not"
    return not crc8_instance.verify(bytes(message_bytes[1:]), message_bytes[0])

def crc16(polynomial, DG, clean, error_rate_type, error_rate, seed):

    # Setup instance with desired settings
    crc_config = crc.Configuration(
        width=16,
        polynomial=polynomial,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input=False,
        reverse_output=False
    )
    crc16_instance = crc.Calculator(crc_config)

    # Calculate crc8 word from bytes
    crc_word = crc16_instance.checksum(bytes(clean))

    # Combine crc word + bytes and convert to bits
    crc_bytes = np.frombuffer(np.uint16(crc_word).tobytes(), dtype=np.uint8)
    message_bytes = np.concatenate((crc_bytes, clean))
    message_bits = np.unpackbits(message_bytes, bitorder="little")

    # Generate errors and convert back to bytes
    DG.generate_errors(message_bits, error_rate_type, error_rate, seed)
    message_bytes = np.packbits(message_bits, bitorder="little")

    # Extract the first 2 bytes as the received checksum
    received_crc = np.frombuffer(message_bytes[:2].tobytes(), dtype=np.uint16)[0]

    # Returns true based on a detected error, crc.verify returns the inverse: false == error hence, the "not"
    return not crc16_instance.verify(bytes(message_bytes[2:]), received_crc)

def rs(DG, clean, error_rate_type, error_rate, seed):
    rsc = RSCodec(4)
    print(clean)
    clean_plus_rs = np.array(rsc.encode(clean))
    print(clean_plus_rs)
    DG.generate_errors(clean_plus_rs, error_rate_type, error_rate, seed)
    print(clean_plus_rs)
    print(np.array(rsc.decode(clean_plus_rs)[0]))
    return


def hamming(r, DG, clean, error_rate_type, error_rate, seed):

    # instance of hamming with specific nr of parity bits
    ham_r = Hamming(clean, r)

    # calculate hamming parities for entire block
    ham_r.encode()

    # generate errors in message
    DG.generate_errors(ham_r.message, error_rate_type, error_rate, seed)

    # return number of errors in message
    return ham_r.decode(ham_r.message)
