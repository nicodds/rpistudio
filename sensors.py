from aadc import AbstractADC
from analog_sensor import AnalogSensor
from i2c_sensor import I2cSensor
from SDL_Pi_HDC1000 import *
from time import sleep

# setup the ADC
adc = AbstractADC()
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

    

class Pmt1Sensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name='pmt1', channel=channel, debug=debug)

    def convert(self, measure):
        factor       = 12.735170
        true_measure = factor * measure
        
        return true_measure

    
class Pmt2Sensor(AnalogSensor):
    def __init__(self, channel, name, debug=False):
        AnalogSensor.__init__(self, name=name, channel=channel, debug=debug)

    def convert(self, measure):
        factor       = 12.694516
        true_measure = factor * measure
        
        return true_measure


class HumiditySensor(I2cSensor):
    def __init__(self, address, name, debug=False):
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
        
