import serial
import numpy as np

class ActonSp300i(object):
    def __init__(self, port='/dev/tty', sensor=None):
        """
        A class to interface to Princeton Instruments SpectraPro 300i
        Monocrhomator via serial interface, using the protocol specified
        in ftp://ftp.princetoninstruments.com/public/manuals/Acton/Sp-300i.pdf
        """
        self._port   = port
        self._sensor = sensor
        try:
            self._connection = serial.Serial(self._port,
                                             baudrate=9600,
                                             bytesize=serial.EIGHTBITS,
                                             parity=serial.PARITY_NONE,
                                             stopbits=serial.STOPBITS_ONE,
                                             timeout=5)
            self._connection.open()
        except serial.SerialException:
            print('Unable to find or configure a serial connection to device %s' %(self._port))
            return None

        
    def set_sensor(self, sensor):
        self._sensor = sensor

        
    def get_current_position(self):
        """
        This method returns the current position of the grating, i.e. the currently 
        selected wavelength. The value is a float representing the wavelength in
        nanometers. On error, the method raises a serial.SerialException.
        """
        self._connection.write(b"?NM\r")
        ret_str      = self._connection.read_until()
        ret_elements = ret_str.decode().strip().split()

        if (len(ret_elements) == 4) and (ret_elements[-1] == 'ok'):
            return float(ret_elements[1])
        else:
            raise serial.SerialException

        
    def init_scan(self, wavelength):
        self._connection.write(b"%f GOTO\n" %(float(wavelength)))
        line = self._connection.read_until()

        
    def move_to(self, wavelength):
        """ 
        Move the grating to the given wavelength
        """
        self._connection.write(b"%f NM\n" %(float(wavelength)))
        line = self._connection.read_until()

        print(line.decode())

        if line.decode().strip() != 'ok':
            raise serial.SerialException
            

        
    def scan(self, wavelength_range=(400, 800), n_repetitions=30, n_integrations=1):
        """
        Performs a wavelength scan in 'wavelength_range' (defaults from 400 to 
        800 nm with 1 nm step), repeating the measure n_repetitions times (defaults
        to 30) and summing up n_integrations times (defaults to 1, i.e. no sum) the
        values.

        The method returns a numpy array of length equal to the wavelength range
        and whose structure is [wavelenght, mean measure, standard deviation].
        """
        measures = []
        self.init_scan(wavelength_range[0]-0.1)
        
        for l in range(wavelength_range[0], wavelength_range[1]+1):
            current_measure = []
            
            self.move_to(l)
            
            for _ in range(n_integrations):
                tmp_measure = []
                for _ in range(n_repetitions):
                    tmp_measure.append(self._sensor.measure())
                if n_integrations == 1:
                    current_measure = tmp_measure
                else:
                    current_measure.append(np.array(tmp_measure).sum())

            current_measure = np.array(current_measure)
            measures.append([l, current_measure.mean(), current_measure.std()])

        return np.array(measures)
                
            
        
