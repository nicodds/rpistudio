# coding: utf-8
import RPi.GPIO as io
from time import time

STOPPED = 0
HEATING = 1
COOLING = 2


class Peltier(object):

    def __init__(self, right_gpio, left_gpio):
        # we are currently developing this library, debug is on
        self._debug = True
        # definition of comunication endpoints
        self.r_gpio = right_gpio
        self.l_gpio = left_gpio
        # configuration of the endpoints
        io.setmode(io.BCM)
        io.setup(self.r_gpio, io.OUT)
        io.setup(self.l_gpio, io.OUT)
        # definition of the polarity controllers
        self.hot_ctrl  = io.PWM(self.l_gpio, 100)
        self.cold_ctrl = io.PWM(self.r_gpio, 100)
        self._status = STOPPED
        self._last_change = 0.0
        # available statuses
        # 0 stopped
        # 1 heating up
        # 2 cooling down

    def _set_status(self, status):
        if self._debug:
            print(" -------> Activity lasted: %.2f seconds" %(time()-self._last_change))
        self._last_change = time()
        self._status = status
        
        if self._debug:
            print("Set status %d on %f" %(status, self._last_change))

    def get_status(self):
        return self._status

    def time_in_status(self):
        return float(time()-self._last_change)

    def start_heatup(self):
        if self._debug:
            print("Heating up")
        self._set_status(HEATING)
        self.hot_ctrl.start(100)

    def start_cooldown(self):
        if self._debug:
            print("Cooling down")
        self._set_status(COOLING)
        self.cold_ctrl.start(100)

    def stop(self):
        if self._debug:
            print('Stopping')
            
        if self.get_status() == HEATING:
            self.hot_ctrl.stop()
        elif self.get_status() == COOLING:
            self.cold_ctrl.stop()        
                
        self._set_status(STOPPED)

    def cleanup(self):
        io.cleanup()
