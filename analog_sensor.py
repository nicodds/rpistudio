from abstract_sensor import AbstractSensor

class AnalogSensor(AbstractSensor):
    adc = None
    
    def __init__(self, channel, name='analog_sensor', debug=False):
        self._channel = channel
        self._name    = name
        self._debug   = debug


    def measure(self):
        raw_measure = AnalogSensor.adc.read(self._channel)
        converted   = self.convert(raw_measure)
        
        if self._debug:
            print('%s: %f (raw: %f)' %(self._name, converted, raw_measure))
            
        return converted

    
    def get_channel(self):
        return self._channel

    def set_channel(self, channel):
        self._channel = channel
