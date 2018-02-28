# coding: utf-8
import RPi.GPIO as io
from time import time
from pid_control import PidController
import numpy as np

# available statuses
# 0 stopped
# 1 heating up
# 2 cooling down

STOPPED = 0
HEATING = 1
COOLING = 2


class Peltier(object):

    def __init__(self, cold_gpio, hot_gpio, kp=0, ki=0, kd=0, pwm=100):
        # we are currently developing this library, debug is on
        self._debug = True
        # definition of comunication endpoints
        self.c_gpio = cold_gpio
        self.h_gpio = hot_gpio
        # configuration of the endpoints
        io.setmode(io.BCM)
        io.setup(self.c_gpio, io.OUT, initial=io.LOW)
        io.setup(self.h_gpio, io.OUT, initial=io.LOW)

        # definition of the polarity controllers
        self._pwm = pwm
        self.hot_ctrl  = io.PWM(self.h_gpio, self._pwm)
        self.cold_ctrl = io.PWM(self.c_gpio, self._pwm)
        self._status = STOPPED
        self._last_pwm_value = None
        self._last_change = 0.0

        # pid controller
        self._pid = PidController(kp, ki, kd)

        
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

    
    def heatup(self, value=100):
        if self._debug:
            print("Heating up")

        if self.get_status() != HEATING:
            self._set_status(HEATING)
            if self.get_status() == COOLING:
                self.cold_ctrl.stop()
                
            self.hot_ctrl.start(value)
        else:
            self.hot_ctrl.ChangeDutyCycle(value)

        
    def cooldown(self, value=100):
        if self._debug:
            print("Cooling down %i" % value)

        if self.get_status() != COOLING:
            self._set_status(COOLING)
            
            if self.get_status() == HEATING:
                self.hot_ctrl.stop()
                
            self.cold_ctrl.start(value)
        else:
            self.cold_ctrl.ChangeDutyCycle(value)

        
    def stop(self):
        if self._debug:
            print('Stopping')
            
        if self.get_status() == HEATING:
            self.hot_ctrl.stop()
        elif self.get_status() == COOLING:
            self.cold_ctrl.stop()        
                
        self._set_status(STOPPED)


    def adjust(self, delta):
        pwm_value = int(100*self._pid.check(delta))
        pwm_sign = np.sign(pwm_value)
        pwm_value = np.abs(pwm_value)

        if pwm_value > self._pwm:
            pwm_value = self._pwm

        if pwm_sign > 0:
            if self._debug:
                print("Heating with pwm %f" %(pwm_value))
            self.heatup(pwm_value)
        elif pwm_sign < 0:
            if self._debug:
                print("Cooling with pwm %f" %(pwm_value))
            self.cooldown(pwm_value)
        else:
            self.stop()

        return pwm_sign*pwm_value

        
    def cleanup(self):
        io.cleanup()
