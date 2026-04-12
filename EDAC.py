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

# Basic checksum (max data size 255 bits)
class Checksum:
    def __init__(self, input_data):
        self.blocks = len(input_data)
        self.message = np.unpackbits(input_data, bitorder="little")
        self.message = np.append(np.zeros(8, dtype=np.uint8), self.message)


    def calc_checksum(self, message):
        # save old checksum
        old_chksm = np.packbits(message[:8], bitorder="little")[0]
        # calc checksum while avoiding checksum bits themselves
        chksm = np.sum(message[8:])
        # assign new checksum to message start
        message[:8] = np.unpackbits(np.array([chksm], dtype=np.uint8), bitorder="little")

        # returns True if mismatched (error detected)
        return old_chksm != chksm




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
            for i in range(self.r):
                message[block_start + (1 << i)] = (error_position >> i) & 1

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










































