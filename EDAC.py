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




class Hamming:


    def __init__(self, input_data, r):
        # Determine size of total packet in bits
        self.total_packet_length = 2 ** r - 1

        # Determine ceiling size of total packet in bytes and create corresponding byte array of zero
        nr_of_bytes = (self.total_packet_length + 7) // 8
        self.total_packet = bytearray(nr_of_bytes)


        # Locate bit position of all parity bits and data bits
        self.parity_idx = {2 ** i - 1 for i in range(r)}
        self.data_idx = set(range(self.total_packet_length)) - self.parity_idx
        self.check_pp()

        # Length of data in bits
        input_data_length = len(input_data) * 8

        # Run through data positions in total packet but stop once length has reached data_length
        input_data_idx = 0
        for total_data_idx in sorted(self.data_idx):

            # Finds bit value within original data array, if 1 set self.bits position to 1
            if self.get_bit(input_data, input_data_idx):
                self.set_bit(self.total_packet, total_data_idx, 1)

            # Count up through the original data using the input_data_idx, done at input_data_length - 1
            input_data_idx += 1
            if input_data_idx >= input_data_length:
                break

    def check_pp(self):

        sanity_check = ''
        for idx in range(self.total_packet_length):
            if idx in self.parity_idx:
                sanity_check += 'P'

            elif idx in self.data_idx:
                sanity_check += 'D'

            else:
                sanity_check += 'X'

        print(sanity_check)



    def set_bit(self, data, position, value):
        byte_idx, bit_idx = divmod(position, 8)
        if value:
            data[byte_idx] |= (1 << bit_idx)
        else:
            data[byte_idx] &= ~(1 << bit_idx)


    def get_bit(self, data, position):
        byte_idx, bit_idx = divmod(position, 8)
        return (data[byte_idx] >> bit_idx) & 1


    def calc_parity(self, input_data):

        # Run through all parity bits and calculate parity
        for parity_position in sorted(self.parity_idx):
            parity_sum = 0

            # Run through all data positions
            for data_bit_idx in sorted(self.data_idx):

                # Find positions where binary index match parity_position

                if (data_bit_idx + 1) & (parity_position + 1):
                    parity_sum += self.get_bit(input_data, data_bit_idx)

            # Set parity bit
            self.set_bit(input_data, parity_position, parity_sum % 2)

    def calc_extnd_parity(self, input_data):
        # Pass over entire packet
        parity_sum = 0
        for idx in range(self.total_packet_length):
            parity_sum += self.get_bit(input_data, idx)

        # Returns 1 for odd nr of ones and 0 for even.
        return parity_sum % 2


    def encode(self, hamming_type= "trad"):
        self.calc_parity(self.total_packet)
        match hamming_type:

            # Normal Hamming
            case "trad":
                return

            # Extended Hamming
            case "extnd":
                # Set last bit as parity bit
                self.set_bit(self.total_packet, self.total_packet_length, self.calc_extnd_parity(self.total_packet))



    def decode(self, input_data, hamming_type= "trad"):

        # Copy input and recalculate parity
        input_data_recalc = input_data[:]
        self.calc_parity(input_data_recalc)

        error_position = 0
        for parity_position in sorted(self.parity_idx):

            # Parity position of rx and recalced differ
            if self.get_bit(input_data_recalc, parity_position) != self.get_bit(input_data, parity_position):
                # Sum syndrome to find position
                error_position += parity_position + 1

        match hamming_type:

            # Normal Hamming
            case "trad":
                # Flip bit
                if error_position != 0:
                    print("bit flip detected & corrected")
                    error_bit_value = self.get_bit(input_data, error_position - 1)
                    self.set_bit(input_data, error_position - 1, error_bit_value ^ 1)

            # Extended Hamming
            case "extnd":
                # Calculates parity bit of received data
                parity_calc = self.calc_extnd_parity(input_data)
                parity_rx = self.get_bit(input_data, self.total_packet_length)

                if parity_calc != parity_rx:
                    if error_position != 0:
                        print("bit flip detected & corrected")
                        error_bit_value = self.get_bit(input_data, error_position - 1)
                        self.set_bit(input_data, error_position - 1, error_bit_value ^ 1)
                    else:
                        # Flip extended parity bit...
                        print("Extended Parity bit error")
                else:
                    if error_position != 0:
                        print("double bit flip detected, cannot correct")
                    else:
                        print("no errors")


        return input_data
















































