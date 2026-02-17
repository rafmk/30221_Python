import numpy as np
import crc8

# UART parity


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

# CRC

class CRC:
    def __init__(self, data=b'', crc_size=1, poly='0x00'):
        self.data = data
        self.crc_size = crc_size
        self.poly = poly

    def crc_calculate(self):
        # generate crc codeword and append to data
        return self.data

    def crc_check(self):
        # check crc codeword against data
        return "bingo"



# Hamming code (7,4)



# BCH code
