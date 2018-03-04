from time import time


class PidController(object):
    def __init__(self, p, i, d):
        self._kp = p
        self._ki = i
        self._kd = d
        self._last_value = 0
        self._last_time  = time()


    def check(self, delta):
        dt = time() - self._last_time
        
        return_value = self._kp * delta
        return_value += self._ki * self._integrate(delta, dt)
        return_value += self._kd * self._derive(delta, dt)

        self._last_value = delta
        self._last_time  = time()

        return return_value
        

    def _integrate(self, new_value, dt):
        return 0.5*dt*(self._last_value+new_value)

    def _derive(self, new_value, dt):
        return (new_value-self._last_value)/dt
