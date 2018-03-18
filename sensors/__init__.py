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


from .aadc import AbstractADC
from .abstract_sensor import AbstractSensor
from .analog_sensor import AnalogSensor
from .i2c_sensor import I2cSensor
from .SDL_Pi_HDC1000 import *
from time import sleep
import numpy as np

# setup the ADC using a 14 bit resolution
adc = AbstractADC(bit=14)
AnalogSensor.adc = adc


class TempControlSensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name=name, channel=channel, debug=debug)

    def convert(self, measure):
        intercept = 0.49374288952568435
        pendence  = 90.665619256659113

        value  = intercept + measure*pendence

        return value


class TempMeasureSensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name=name, channel=channel, debug=debug)

    def convert(self, measure):
        intercept = 0.49374288952568435
        pendence  = 90.665619256659113

        value  = intercept + measure*pendence

        return value



class RawPmtSensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name='pmt', channel=channel, debug=debug)

    def convert(self, measure):
        return measure



class Pmt1Sensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name='pmt1', channel=channel, debug=debug)

    def convert(self, measure):
        factor       = 12.735170
        true_measure_v = factor * measure
        true_measure_phot_sec = 508115364.5*true_measure_v
        
        return true_measure_phot_sec

    
class Pmt2Sensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name=name, channel=channel, debug=debug)

    def convert(self, measure):
        factor       = 12.694516
        true_measure_v = factor * measure
        true_measure_phot_sec = 508115364.5*true_measure_v
        
        
        return true_measure_phot_sec


class HumiditySensor(I2cSensor):
    def __init__(self, address, name, debug=False):
        """A class to interface to HDC1000/1080 digital humidity and temperature sensors"""
        self._address  = address
        self._name     = name
        self._debug    = debug
        self._instance = SDL_Pi_HDC1000(addr=self._address)

        self._instance.setTemperatureResolution(HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
        self._instance.setHumidityResolution(HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)

        

    def prepare_sensor(self, seconds=5):
        if self._debug:
            print('Heating %s surface to prepare for measures' %(self._name))
        self._instance.turnHeaterOn()
        sleep(seconds)
        self._instance.turnHeaterOff()

        

    def convert(self, measure):
        return measure


    def measure(self):
        return self._instance.readHumidity()

    def measure_temperature(self):
        return self._instance.readTemperature()
        

class RandomSensor(AbstractSensor):
    def __init__(self):
        self._name = 'random_sensor'

    def measure(self):
        return np.random.uniform()
