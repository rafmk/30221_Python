import numpy as np
import crc8

# UART parity


# Fletcher



# Adler-32



# CRC 3 bit (X0, X1, X2)
def crc8_test(data):
    print("crc8_test")
    print(type(bytearray(data)))
    test = crc8.crc8(initial_string=bytearray(data))
    return type(test.digest())



# Hamming code (7,4)



# BCH code
