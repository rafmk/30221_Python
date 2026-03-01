from matplotlib import pyplot as plt
import numpy as np
from data_generator import DataGenerator
from EDAC import *
from FletcherChecksumLib import FletcherChecksumBytes
import crc
from reedsolo import RSCodec


class Test:
    def __init__(self, rounds):
        self.rounds = rounds

        # # of detections for simulation
        self.det_parity = 0
        self.det_fletcher = 0
        self.det_crc8 = 0
        self.det_rs = 0
        self.det_bhc = 0

        # # of corrections for simulation
        self.cor_hm = 0
        self.cor_rs = 0
        self.cor_bhc = 0


    def sim_inst(self, error_rate):

        for rnd in range(self.rounds):
            # Just set seed for error generation identical for all EDAC methods
            error_seed = rnd

            # Setup random data
            DG = DataGenerator(18)
            clean = DG.generate_clean()

            # count up positive detections for each method
            self.det_parity += parity(DG, clean, error_rate, error_seed)
            self.det_fletcher += fletcher(DG, clean, error_rate, error_seed)
            self.det_crc8 += crc8(DG, clean, error_rate, error_seed)













def parity(DG, clean, error_rate, seed):
    ###UART Parity clone###

    # Grab parity bytes
    parity_bytes = np.array(Parity(clean).parity_calc(), dtype=np.uint8)

    # Combine clean + parity bytes & feed to error generator
    clean_plus_p = np.append(clean, parity_bytes)
    # print(clean_plus_p)
    DG.generate_errors(clean_plus_p, error_rate, seed)
    # print(DG.dirty)

    # Grab dirty array and feed to Parity calc
    PD = Parity(clean_plus_p)
    PD.check_parity(len(parity_bytes))
    #print("Parity error detection: ", PD.error_detection, "errors detected")

    # Returns true based on a detected error
    return PD.error_detection !=0 #, PD.error_detection


def fletcher(DG, clean, error_rate, seed):
    ###Fletcher###

    # Setup instance
    FL = FletcherChecksumBytes

    # Calculate fletcher 16 for clean data
    fl_clean = FL.get_fletcher16(bytes(clean))
    fl_h = (fl_clean['Fletcher16_dec'] >> 8) & 0xff
    fl_l = fl_clean['Fletcher16_dec'] & 0xff

    # Combine clean + parity bytes & feed to error generator
    clean_plus_fl = np.append(clean, np.array([fl_h, fl_l], dtype=np.uint8))

    # Generate errors
    DG.generate_errors(clean_plus_fl, error_rate, seed)
    # Possibly erroneous fletcher16 values
    fl_h_tx, fl_l_tx = clean_plus_fl[-2:]

    # Calculate fletcher16 values for incoming data and check against sent values
    fl_dirty = FL.get_fletcher16(bytes(clean_plus_fl[:-2]))
    fl_h_rx = (fl_dirty['Fletcher16_dec'] >> 8) & 0xff
    fl_l_rx = fl_dirty['Fletcher16_dec'] & 0xff

    # Returns true based on a detected error
    return fl_h_tx != fl_h_rx or fl_l_tx != fl_l_rx


def crc8(DG, clean, error_rate, seed):
    ###CRC8###

    # Setup instance with desired settings
    crc_config = crc.Configuration(
        width=8,
        polynomial=0xA6,
        init_value=0x00,
        final_xor_value=0x00,
        reverse_input=False,
        reverse_output=False
    )
    CRC = crc.Calculator(crc_config)

    # Calculate crc value
    crc_word = CRC.checksum(bytes(clean))

    # Combine clean + crc word & feed to error generator
    clean_plus_crc = np.append(clean, np.uint8(crc_word))

    # Generate errors
    DG.generate_errors(clean_plus_crc, error_rate, seed)

    # Returns true based on a detected error, crc.verify returns the inverse: false == error hence, the "not"
    return not CRC.verify(bytes(clean_plus_crc[:-1]), clean_plus_crc[-1])


def rs(DG, clean, error_rate, seed):
    rsc = RSCodec(4)
    print(clean)
    clean_plus_rs = np.array(rsc.encode(clean))
    print(clean_plus_rs)
    DG.generate_errors(clean_plus_rs, error_rate, seed)
    print(clean_plus_rs)
    print(np.array(rsc.decode(clean_plus_rs)[0]))
    return


def hamming(DG, clean, error_rate, seed):
    pass
