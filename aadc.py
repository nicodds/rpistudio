from ABE_helpers import ABEHelpers
from ABE_ADCDifferentialPi import ADCDifferentialPi

class AbstractADC(object):
    def __init__(self, bit=16):
        self._adc = ADCDifferentialPi(ABEHelpers().get_smbus(), 0x68, 0x69, 16)

    def read(self, channel):
        return self._adc.read_voltage(channel)
