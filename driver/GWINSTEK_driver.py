import socket
import time


#TODO test commands for time to sleep before theyre confirmed to have completed
    #
    # SYST:ERR, what exactly does it mean pulled when any command was not successfully executed
    #

class GWINSTEK_driver:
    
    def __init__(self, ip: str, port: int, output_on_delay: float=0.0, output_off_delay: float=0.0, output_mode=0, sense_avg_count: int=1, ocp: float=None, ovp: float=None):
        self.TCP_IP = ip 
        self.PORT = port
        
        # establish system constants once  
        self.OCP_MIN = float(self._send_read("SOUR:CURR:PROT:LEV? MIN"))
        self.OCP_MAX  = float(self._send_read("SOUR:CURR:PROT:LEV? MAX"))
        self.CURR_MIN = float(self._send_read("SOUR:CURR:LEV:IMM:AMPL? MIN"))
        self.CURR_MAX = float(self._send_read("SOUR:CURR:LEV:IMM:AMPL? MAX"))
        self.CURR_RISE_MIN = float(self._send_read("SOUR:CURR:SLEW:RIS? MIN"))
        self.CURR_RISE_MAX = float(self._send_read("SOUR:CURR:SLEW:RIS? MAX"))
        self.CURR_FALL_MIN = float(self._send_read("SOUR:CURR:SLEW:FALL? MIN"))
        self.CURR_FALL_MAX = float(self._send_read("SOUR:CURR:SLEW:FALL? MAX"))

        self.OVP_MIN = float(self._send_read("SOUR:VOLT:PROT:LEV? MIN"))
        self.OVP_MAX = float(self._send_read("SOUR:VOLT:PROT:LEV? MAX"))
        self.VOLT_MIN = float(self._send_read("SOUR:VOLT:LEV:IMM:AMPL? MIN"))
        self.VOLT_MAX = float(self._send_read("SOUR:VOLT:LEV:IMM:AMPL? MAX"))
        self.VOLT_RISE_MIN = float(self._send_read("SOUR:VOLT:SLEW:RIS? MIN"))
        self.VOLT_RISE_MAX = float(self._send_read("SOUR:VOLT:SLEW:RIS? MAX"))
        self.VOLT_FALL_MIN = float(self._send_read("SOUR:VOLT:SLEW:FALL? MIN"))
        self.VOLT_FALL_MAX = float(self._send_read("SOUR:VOLT:SLEW:FALL? MAX"))

        self.RES_MIN = float(self._send_read("SOUR:RES:LEV:IMM:AMPL? MIN"))
        self.RES_MAX = float(self._send_read("SOUR:RES:LEV:IMM:AMPL? MAX"))

        self.BEEP_DUR_MIN = int(self._send_read("SYST:BEEP? MIN"))
        self.BEEP_DUR_MAX = int(self._send_read("SYST:BEEP? MAX"))

        self.OUTPUT_MODES = {'CVHS': 0,'CCHS': 1,'CVLS': 2,'CCLS': 3}
        self.SYSTEM_INFO = self._get_system_info()
        print('oooooooggaaaaa')

        # configurations
        if not ocp:
            ocp = self.OCP_MAX
        if not ovp:
            ovp = self.OVP_MAX

        self._set_output_on_delay(output_on_delay)
        self._set_output_off_delay(output_off_delay)
        self.set_output_mode(output_mode)
        self.set_sense_avg_count(sense_avg_count)
        self.set_ocp(ocp)
        self.set_ovp(ovp)
        self.abort_commands()


    def _send(self, message: str):
        # open socket and send 'message' over TCP to self.TCP_IP on port self.PORT, 
        # then close socket
        if not message.endswith('\n'):
            message += '\n'
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
            s.connect((self.TCP_IP, self.PORT))
            s.send(message.encode())
            #time.sleep(0.1)

    def _send_read(self, message: str):
        # open TCP socket, send 'message' to 'self.TCP_IP' on port 'self.PORT', 
        # return response from the socket as a string
        if not message.endswith('\n'):
            message += '\n'

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
            s.connect((self.TCP_IP, self.PORT))
            s.send(message.encode())
            #time.sleep(0.1)
            try:
                response = s.recv(256).decode().replace('\n','')
            except TimeoutError as err:
                print(f"[LAST MESSAGE]: {message}")
                raise err
            return response
    
    def _get_system_info(self):
        sys_info_string = self._send_read('SYST:INF?')
        sys_info_list = [value.split(' ')[1] for value in sys_info_string.split(',')]
        system_info = {
            'manufacturer': sys_info_list[0],
            'model': sys_info_list[1],
            'serial-number': sys_info_list[2],
            'firmware-version': sys_info_list[3],
            'keyboard-cpld': sys_info_list[4],
            'analog-cpld': sys_info_list[5],
            'kernal-build-date': sys_info_list[6],
            'test-version': sys_info_list[7],
            'test-build-date': sys_info_list[8],
            'mac-address': sys_info_list[9],
        }
        return system_info

    def _set_output_on_delay(self, delay: float):
        message = f"OUTP:DEL:ON {delay}"
        self._send(message)
        return True

    def _set_output_off_delay(self, delay: float):
        message = f"OUTP:DEL:OFF {delay}"
        self._send(message)
        return True
    
    def _measure(self, which: str):
        message = f"MEAS:SCAL:{which}:DC?"
        return float(self._send_read(message))

    def abort_commands(self):
        self._send("ABOR")

    def apply_ocp(self, value: bool):
        message = f"SOUR:CURR:PROT:STAT ON" if value else "SOUR:CURR:PROT:STAT OFF"
        self._send(message)
        
    def apply_ovp(self, value: bool):
        message = "SOUR:VOLT:PROT:STAT ON" if value else "SOUR:VOLT:PROT:STAT OFF"
        self._send(message)
    
    def get_bleeder_resistor_state(self):
        message = "SYST:CONF:BLE:STAT?"
        response = self._send_read(message)
        return True if response == "true" else False
    
    def get_buzzer_state(self):
        message = "SYST:CONF:BEEP:STAT?"
        response = self._send_read(message)
        return True if response == "true" else False
    
    def get_current(self):
        message = "SOUR:CURR:LEV:IMM:AMPL?"
        return float(self._send_read(message))
    
    def get_current_slew_fall(self):
        message = "SOUR:CURR:SLEW:FALL?"
        return self._send_read(message)
    
    def get_current_slew_rise(self):
        message = "SOUR:CURR:SLEW:RIS?"
        return self._send_read(message)

    def get_last_error(self):
        message = "SYST:ERR?"
        error = self._send_read(message)
        return error

    def get_model(self):
        return self.SYSTEM_INFO['model']
    
    def get_ocp(self):
        message = "SOUR:CURR:PROT:LEV?"
        return float(self._send_read(message))

    def get_output_mode(self):
        message = "OUTP:MODE?"
        return int(self._send_read(message))
    
    def get_ovp(self):
        message = "SOUR:VOLT:PROT:LEV?"
        return float(self._send_read(message))
    
    def get_sense_avg_count(self):
        message = "SENS:AVER:COUNT?"
        return float(self._send_read(message))

    def get_serial_number(self):
        return self.SYSTEM_INFO["serial-number"]

    def get_series_resistance(self):
        message = "SOUR:RES:LEV:IMM:AMPL?"
        return float(self._send_read(message))
    
    def get_voltage(self):
        message = "SOUR:VOLT:LEV:IMM:AMPL?"
        return float(self._send_read(message))
    
    def get_voltage_slew_fall(self):
        message = "SOUR:VOLT:SLEW:FALL?"
        return float(self._send_read(message))
    
    def get_voltage_slew_rise(self):
        message = "SOUR:VOLT:SLEW:RIS?"
        return float(self._send_read(message))
    
    def measure_current(self):
        return self._measure("CURR")
    
    def measure_power(self):
        return self._measure("POW")

    def measure_voltage(self):
        return self._measure("VOLT")
    
    def output_protection_clear(self):
        message = "OUTP:PROT:CLE"
        self._send(message) 
    
    def output_recover(self):
        self.set_output_state(False)
        self.output_protection_clear()
        time.sleep(1)
        return False if self.output_tripped() else True

    def output_tripped(self):
        message = "OUTP:PROT:TRIP?\n"
        response = self._send_read(message) 
        return True if response == 1 else False
    
    def reset(self):
        self._send(f"*RST\n")
    
    def set_bleeder_resistor_state(self, value: bool):
        message = "SYST:CONF:BLE:STAT ON" if value else "SYST:CONF:BLE:STAT OFF"
        self._send(message)
    
    def set_buzzer_state(self, value: bool):
        message = "SYST:CONF:BEEP:STAT ON" if value else "SYST:CONF:BEEP:STAT OFF"
        self._send(message)
    
    def set_current(self, current: float):
        raise_for_range(current, self.CURR_MIN, self.CURR_MAX)
        message = f"SOUR:CURR:LEV:IMM:AMPL {current}"
        self._send(message)

        return percent_error(self.get_current(), current) < 5
    
    def set_current_slew_fall(self, rate: float):
        raise_for_range(rate, self.CURR_FALL_MIN, self.CURR_FALL_MAX) 
        message = f"SOUR:CURR:SLEW:FALL {rate}"  
        self._send(message)
    
    def set_current_slew_rise(self, rate: float):
        raise_for_range(rate, self.CURR_RISE_MIN, self.CURR_RISE_MAX)
        message = f"SOUR:CURR:SLEW:RIS {rate}"
        self._send(message)
    
    def set_ocp(self, level: float):
        raise_for_range(level, self.OCP_MIN, self.OCP_MAX)
        message = f"SOUR:CURR:PROT:LEV {level}"
        self._send(message)

    def set_ovp(self, level: float):
        raise_for_range(level, self.OVP_MIN, self.OVP_MAX)
        message = f"SOUR:VOLT:PROT:LEV {level}"
        self._send(message)  
    
    def set_output_mode(self, mode):
        if mode in self.OUTPUT_MODES:
            mode = self.OUTPUT_MODES[mode]
        if mode in self.OUTPUT_MODES.values():
            message = f"OUTP:MODE {mode}"
            self._send(message)
            return int(self.get_output_mode()) == mode
        else:
            raise ValueError("Value must be 0-3 or 'CVHS','CCHS','CVLS','CCLS'")
    
    def set_output_state(self, value: bool):
        message = "OUTP:STAT 1" if value else "OUTP:STAT 0"  
        self._send(message)
    
    def set_series_resistance(self, level: float):
        raise_for_range(level, self.RES_MIN, self.RES_MAX)
        message = f"SOUR:RES:LEV:IMM:AMPL {level}"
        self._send(message)
        return percent_error(self.get_series_resistance(), level) < 5

    def set_sense_avg_count(self, level: int):
        raise_for_range(level,0,2)
        message = f"SENS:AVER:COUN {level}"
        self._send(message)
        return self.get_sense_avg_count() == level
    
    def set_voltage(self, voltage: float):
        raise_for_range(voltage, self.VOLT_MIN, self.VOLT_MAX)
        message = f"SOUR:VOLT:LEV:IMM:AMPL {voltage}"
        self._send(message)

        return percent_error(self.get_voltage(), voltage) < 5
    
    def set_voltage_current(self, voltage: float, current: float):
        raise_for_range(voltage, self.VOLT_MIN, self.VOLT_MAX)
        raise_for_range(current, self.CURR_MIN, self.CURR_MAX)
        message = f"APPL {voltage},{current}"
        self._send(message)
        voltage_error = percent_error(self.get_voltage(), voltage)
        current_error = percent_error(self.get_current(), current)

        return voltage_error < 5 & current_error < 5
    
    def set_voltage_slew_fall(self, rate: float):
        raise_for_range(rate, self.VOLT_FALL_MIN, self.VOLT_FALL_MAX)
        message = f"SOUR:VOLT:SLEW:FALL {rate}"
        self._send(message)
    
    def set_voltage_slew_rise(self, rate: float):
        raise_for_range(rate, self.VOLT_RISE_MIN, self.VOLT_RISE_MAX)
        message = f"SOUR:VOLT:SLEW:RIS {rate}"
        self._send(message)
    
    def system_beep(self, duration: int=1):
        raise_for_range(duration, self.BEEP_DUR_MIN, self.BEEP_DUR_MAX)
        message = f"SYST:BEEP:IMM {duration}"
        self._send(message)
        return True

    def system_preset(self):
        self._send("SYST:PRES")  
    
    def test_device(self):
        message = "*TST?"
        error_code = int(self._send_read(message))
        return error_code

def raise_for_range(value, minimum, maximum):
    if value < minimum or value > maximum:
        raise ValueError(f"Value outside acceptable range: {minimum} - {maximum}")

def percent_error(expected_value, actual_value):
    percent_error = abs((expected_value - actual_value)/expected_value)*100
    return percent_error

if __name__ == "__main__":

    TCP_IP = "192.168.1.101"
    PORT = 2268
    driver = GWINSTEK_driver(TCP_IP, PORT)

    error_code =  driver.test_device()
    print("\n[DEVICE STATUS]")
    print(f"error status: {error_code}")

    print("\n[SYSTEM INFO]")
    for key in driver.system_info:
        print(f"{key}: {driver.system_info[key]}")

    driver.set_voltage(6)
    driver.set_current(0.02)
    print("\n[SETTINGS]")
    print(f"voltage: {driver.get_voltage()}")
    print(f"current: {driver.get_current()}")
    print(f"output mode: {driver.get_output_mode()}")
    

    v_measured = driver.measure_voltage()
    I_measured = driver.measure_current()
    p_measured = driver.measure_power()
    print("\n[MEASUREMENTS]")
    print(f"measured voltage: {v_measured}")
    print(f"measured current: {I_measured}")
    print(f"measured power: {p_measured}")
'''
from GWINSTEK_driver import GWINSTEK_driver
driver = GWINSTEK_driver("192.168.1.101",2268)

driver.set_output_state(False)
'''
