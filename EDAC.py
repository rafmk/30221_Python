import numpy as np


# UART parity
class Parity:
    def __init__(self, data=b''):
        self.parity_key = 0
        self.data = data

    def parity_calc(self):
        for byte in self.data:
            self.parity_key <<= 1
            if byte.bit_count()%2 != 0:
                self.parity_key += 1
        nr_bytes = (len(self.data) + 7) // 8
        return list(self.parity_key.to_bytes(nr_bytes)), nr_bytes, bin(self.parity_key)

    def check_parity(self, dirty, nr_parity_bytes):
        for byte in dirty[:-nr_parity_bytes]:
            break







# Fletcher
class Fletcher:
    def __init__(self, data=b'', fl_size=8):
        self.data = data
        self.fl_size = fl_size

    def fl_calculate(self):
        # generate fletcher codeword and append to data
        return self.data

    def fl_check(self):
        # check fletcher codeword against data
        return "bingo"

# Hamming code (7,4)



# BCH code
