from abstract_sensor import AbstractSensor

class I2cSensor(AbstractSensor):
    def __init__(self, address='0x00', name='i2c_sensor', debug=False):
        self._address  = address
        self._name     = name
        self._debug    = debug
        # this private property is here to store the object
        # implementing the details of the specific sensor
        self._instance = None


    def get_address(self):
        return self._address

    # there is no set_address method since changing the i2c address
    # once the specific sensor object is istantiated makes no sense.
