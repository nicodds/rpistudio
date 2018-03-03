class AbstractSensor(object):
    
    def __init__(self, name='sensor', debug=False):
        self._name    = name
        self._debug   = debug


    def convert(self, measure):
        print("""%s --- This method currently only return the value
        passed. You should reimplement it in your specialized class.""" %(self._name))

        return measure

    def measure(self):
        print("""%s --- This method currently only return the 0.0. 
        You should reimplement it in your specialized class.""" %(self._name))

        return 0.0
    

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

