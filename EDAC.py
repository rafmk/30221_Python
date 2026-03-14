### Library for EDAC protocols that I couldn't find already available ###
import copy
from data_generator import np
from math import ceil
from functools import reduce
import operator as op

# UART parity sim
class Parity:
    def __init__(self, input_data):
        self.blocks = len(input_data)
        self.input_data = np.unpackbits(input_data, bitorder="little")
        self.block_size = 9 # byte + one parity bit
        # block-wise data bit positions
        self.data_idx = np.arange(1, self.block_size)
        self.message = np.zeros(self.block_size * self.blocks, dtype=bool)
        # global position of data bits
        self.global_data_idx = np.concatenate([block * self.block_size + self.data_idx for block in range(self.blocks)])
        self.errors = 0


    def parity_calc(self):
        # position input data bits within message
        for i, position in enumerate(self.global_data_idx):
            self.message[position] = self.input_data[i]

        for block in range(self.blocks):
            block_start = block * self.block_size
            block_end = block_start + self.block_size

            # block is odd
            if self.message[block_start: block_end].sum() % 2:
                # now block is even
                self.message[block_start] = True


    def check_parity(self, message):
        for block in range(self.blocks):
            block_start = block * self.block_size
            block_end = block_start + self.block_size

            # block is odd meaning error has been detected
            if message[block_start: block_end].sum() % 2:
                self.errors += 1

        return self.errors



# Hamming code

class Hamming:
    def __init__(self, input_data, r):
        # input_data must be np array of dtype uint8
        self.input_data = np.unpackbits(input_data, bitorder="little")  # array of bits
        self.input_len_bits = len(self.input_data)
        self.r = r  # int >= 3
        self.len_available_bits = 2 ** self.r - 1 - self.r
        self.blocks = ceil(self.input_len_bits / self.len_available_bits)

        # block-wise position of parity bits
        self.parity_idx = np.array([2 ** i for i in range(self.r)])
        self.block_size = 2 ** self.r

        # add index for extended parity bit at the start of the block
        self.parity_idx = np.append(self.parity_idx, 0)

        # block-wise position of data bits
        self.data_idx = np.delete(np.arange(self.block_size), self.parity_idx)

        # global position of data bits
        self.global_data_idx = np.concatenate([block * self.block_size + self.data_idx for block in range(self.blocks)])

        # initialize message
        self.message = np.zeros(self.block_size * self.blocks, dtype=bool)

        #self.check_pp()



    def encode(self):

        # position input data bits within message
        for i, position in enumerate(self.global_data_idx):
            # break out of loop if we reach end of input data
            if i == self.input_len_bits:
                break
            self.message[position] = self.input_data[i]

        # calculate Hamming parity bits
        self.calc_parity(self.message)

    def decode(self, message):
        error_count = 0
        correction_count = 0

        for block in range(self.blocks):
            block_start = block * self.block_size
            block_end = block_start + self.block_size
            error_position = reduce(op.xor, [i for i, bit in enumerate(message[block_start:block_end]) if bit], 0)

            # if extended parity returns odd (sum % 2 == true) an odd number of errors have occurred
            if message[block_start: block_end].sum() % 2:
                # if error_position != 0 than single bit flip has occurred
                if error_position != 0:
                    # fix error
                    message[block_start + error_position] = not message[block_start + error_position]
                    error_count += 1
                    correction_count += 1

                # error in parity bit
                else:
                    message[block_start] = not message[block_start]
                    error_count += 1
                    correction_count += 1

            # if extended parity check ok, even number of errors detected
            else:
                # double bit error
                if error_position != 0:
                    # cannot fix error
                    error_count += 2

                # no error
                else:
                    pass

        return error_count, correction_count

    def calc_parity(self, message):
        # calculate Hamming parity bits
        for block in range(self.blocks):
            block_start = block * self.block_size
            block_end = block_start + self.block_size

            error_position = reduce(op.xor, [i for i, bit in enumerate(message[block_start:block_end]) if bit], 0)
            for i in range(error_position.bit_length()):
                if error_position >> i & 1:
                    # flip parity bit in message
                    message[block_start + (2 ** i)] = not message[block_start + (2 ** i)]

            # calculated extended parity
            message[block_start] = message[block_start: block_end].sum() % 2


    def check_pp(self):

        sanity_check = ''
        for i, val in enumerate(self.message):
            if i not in self.global_data_idx:
                sanity_check += 'P'

            elif i in self.global_data_idx:
                sanity_check += 'D'

            else:
                sanity_check += 'X'

        print(sanity_check)

    def convert(self, message):
        data_bits = message[self.global_data_idx]
        return np.packbits(data_bits, bitorder="little")










# bad V1 version, a few oversights, now I'm redoing it i guess
'''class Hamming_bad:
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
        self.input_data_length = len(input_data) * 8

        # Run through data positions in total packet but stop once length has reached data_length
        input_data_idx = 0
        for total_data_idx in sorted(self.data_idx):

            # Finds bit value within original data array, if 1 set self.bits position to 1
            if self.get_bit(input_data, input_data_idx):
                self.set_bit(self.total_packet, total_data_idx, 1)

            # Count up through the original data using the input_data_idx, done at input_data_length - 1
            input_data_idx += 1
            if input_data_idx >= self.input_data_length:
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

    def extract(self, input_data):
        lst = [0] * (self.input_data_length // 8)
        lst_bit_idx = 0
        for total_data_idx in sorted(self.data_idx):
            bit = self.get_bit(input_data, total_data_idx)
            self.set_bit(lst, lst_bit_idx, bit)
            lst_bit_idx += 1
        return lst'''








































