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

from .abstract_sensor import AbstractSensor

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
