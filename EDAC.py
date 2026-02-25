### Library for EDAC protocols that I couldn't find already available ###

# UART parity sim
class Parity:
    def __init__(self, data=b''):
        self.data = data
        self.error_detection = 0

    def parity_calc(self):
        # Calculate number of parity bytes needed (one parity byte per 8 data bytes, rounding up)
        num_parity_bytes = (len(self.data) + 7) // 8

        # Initialize parity bytes
        parity_bytes = bytearray(num_parity_bytes)

        for byte_idx, byte_val in enumerate(self.data):

            # Determine which parity byte this data byte belongs to
            parity_byte_index, parity_bit_position = divmod(byte_idx, 8)

            # Count number of 1 bits in the byte
            bit_count = bin(byte_val).count('1')

            # Add 1 if bit_count odd
            if bit_count % 2:
                # start parity bits with MSB
                parity_bytes[parity_byte_index] |= (1 << (7 - parity_bit_position))

        return parity_bytes

    def check_parity(self, nr_parity_bytes):

        for byte_idx, byte_val in enumerate(self.data[:(len(self.data) - nr_parity_bytes)]):

            # Determine which parity byte this data byte belongs to
            parity_byte_index, parity_bit_position = divmod(byte_idx, 8)
            parity_byte = self.data[(len(self.data) - nr_parity_bytes) + parity_byte_index]

            # data has odd number of 1s and parity is given as 0: bad
            if bin(byte_val).count('1') % 2 and not (parity_byte >> (7 - parity_bit_position)) & 1:
                self.error_detection +=1
            # data has even number of 1s and parity is given as 1: bad
            elif not bin(byte_val).count('1') % 2 and (parity_byte >> (7 - parity_bit_position)) & 1:
                self.error_detection += 1


# Hamming code (7,4)



# BCH code
