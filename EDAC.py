import numpy as np


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

# Hamming code (7,4)



# BCH code
