from EDAC import *

rx_data = np.arange(1, 7, dtype=np.uint8)
print(rx_data)
hm = Hamming(rx_data, 5)
hm.encode()
print(np.packbits(hm.message, bitorder="little"))

