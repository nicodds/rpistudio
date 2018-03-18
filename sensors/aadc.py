# Copyright 2018 Domenico Delle Side <nico@delleside.org>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing,
#    software distributed under the License is distributed on an "AS
#    IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#    express or implied.  See the License for the specific language
#    governing permissions and limitations under the License.


from .ABE_helpers import ABEHelpers
from .ABE_ADCDifferentialPi import ADCDifferentialPi

class AbstractADC(object):
    def __init__(self, bit=16):
        """
        This class is just an abstraction layer to wrap the different ADCs
        available for Raspberry PI. You should implement here ADC initialization
        and provide a "read" method that, given a channel, returns the
        corresponding voltage measure.
        """
        
        self._adc = ADCDifferentialPi(ABEHelpers().get_smbus(), 0x68, 0x69, bit)

    def read(self, channel):
        return self._adc.read_voltage(channel)
