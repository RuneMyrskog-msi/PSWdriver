import socket
import time


#DEVELOPMENT
import pdb


class GWINSTEK_driver:
    
    def __init__(self, ip: str, port: int, output_on_delay: float=0.0, output_off_delay: float=0.0,
     output_mode=0, sense_avg_count: int=1, ocp: float=None, ovp: float=None):
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
        self.system_info= self._get_system_info()

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

    def _send(self, message: str, delay: float=0.0):
        # open socket and send 'message' over TCP to self.TCP_IP on port self.PORT, 
        # then close socket
        if not message.endswith('\n'):
            message += '\n'
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
            s.connect((self.TCP_IP, self.PORT))
            s.send(message.encode())
            time.sleep(delay)

    def _send_read(self, message: str, delay: float=0.0):
        # open TCP socket, send 'message' to 'self.TCP_IP' on port 'self.PORT', 
        # return response from the socket as a string
        if not message.endswith('\n'):
            message += '\n'
        
        response=None
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
            s.connect((self.TCP_IP, self.PORT))
            s.send(message.encode())
            time.sleep(delay)
            try:
                response = s.recv(256).decode().replace('\n','')
            except TimeoutError as err:
                print(f"[LAST MESSAGE]: {message}")
                raise err
        return response
    
    def _send_command(self, command, value=None, value_type=None, minimum=None, maximum=None):
        if value is not None:
            raise_for_type(value, value_type)
            raise_for_range(value, minimum=minimum, maximum=maximum)
            message = f"{command} {value}"
        else:
            message = command
        self._send(message)
        self.raise_for_system_error()
    
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

    def _set_output_on_delay(self, value: float):
        command = f"OUTP:DEL:ON"
        self._send_command(command, value=value, value_type=float)
        return True

    def _set_output_off_delay(self, value: float):
        command = f"OUTP:DEL:OFF"
        self._send_command(command, value=value, value_type=float)
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
        command = "OUTP:PROT:CLE"
        self._send_command(command)
    
    def output_recover(self):
        self.set_output_state(False)
        self.output_protection_clear()
        time.sleep(1)
        return False if self.output_tripped() else True

    def output_tripped(self):
        message = "OUTP:PROT:TRIP?\n"
        response = self._send_read(message) 
        return True if response == 1 else False
    
    def raise_for_system_error(self):
        error_msg = self.system_error()
        if not error_msg.startswith('+0'):
            raise RuntimeError(f"Error returned by power supply: {error_msg}")

    def reset(self):
        command = "*RST"
        self._send_command(command)
    
    def set_bleeder_resistor_state(self, value: bool):
        command = "SYST:CONF:BLE:STAT"
        value = "ON" if value else "OFF"
        self._send_command(command, value=value, value_type=str)
    
    def set_buzzer_state(self, value: bool):
        command = "SYST:CONF:BEEP:STAT"
        value = "ON" if value else "OFF"
        self._send_command(command, value=value, value_type=str)
        return True
    
    def set_current(self, value: float):
        command = f"SOUR:CURR:LEV:IMM:AMPL"
        self._send_command(command, value=value, value_type=float, minimum=self.CURR_MIN, maximum=self.CURR_MAX)
        return percent_error(self.get_current(), value) < 5
    
    def set_current_slew_fall(self, value: float):
        command = f"SOUR:CURR:SLEW:FALL"  
        self._send_command(command, value=value, value_type=float, minimum=self.CURR_FALL_MIN, maximum=self.CURR_FALL_MAX)
        return True
    
    def set_current_slew_rise(self, value: float):
        command = f"SOUR:CURR:SLEW:RIS"
        self._send_command(command, value=value, value_type=float, minimum=self.CURR_RISE_MIN, maximum=self.CURR_RISE_MAX)
        return True
    
    def set_ocp(self, value: float):
        command = f"SOUR:CURR:PROT:LEV"
        self._send_command(command, value=value, value_type=float, minimum=self.OCP_MIN, maximum=self.OCP_MAX)
        return True

    def set_ovp(self, value: float):
        command = f"SOUR:VOLT:PROT:LEV"
        self._send_command(command, value=value, value_type=float, minimum=self.OVP_MIN, maximum=self.OVP_MAX)  
        return True
    
    def set_output_mode(self, value):
        if value in self.OUTPUT_MODES:
            value = self.OUTPUT_MODES[value]
        if value in self.OUTPUT_MODES.values():
            command = f"OUTP:MODE"
            self._send_command(command, value=value, value_type=int)
            return int(self.get_output_mode()) == value
        else:
            raise ValueError("Value must be 0-3 or 'CVHS','CCHS','CVLS','CCLS'")
    
    def set_output_state(self, state: bool):
        command = "OUTP:STAT"  
        value = 1 if value else 0
        self._send_command(command, value=value, value_type=int)
    
    def set_series_resistance(self, value: float):
        command = f"SOUR:RES:LEV:IMM:AMPL"
        self._send_command(command, value=value, value_type=float, minimum=self.RES_MIN, maximum=self.RES_MAX)
        return percent_error(self.get_series_resistance(), value) < 5

    def set_sense_avg_count(self, value: int):
        command = f"SENS:AVER:COUNT"
        self._send_command(command, value=value, value_type=int)
        return int(self.get_sense_avg_count()) == value
    
    def set_voltage(self, value: float):
        command = f"SOUR:VOLT:LEV:IMM:AMPL"
        self._send_command(command, value=value, value_type=float, minimum=self.VOLT_MIN, maximum=self.VOLT_MAX)
        return percent_error(self.get_voltage(), value) < 5
    
    def set_voltage_current(self, voltage: float, current: float):
        command = "APPL"
        value = f"{voltage}"
        raise_for_type(voltage, float)
        raise_for_range(voltage, self.VOLT_MIN, self.VOLT_MAX)
        raise_for_type(current, float)
        raise_for_range(current, self.CURR_MIN, self.CURR_MAX)

        message = f"APPL {voltage},{current}"
        self._send(message)
        voltage_error = percent_error(self.get_voltage(), voltage)
        current_error = percent_error(self.get_current(), current)
        return voltage_error < 5 & current_error < 5
    
    def set_voltage_slew_fall(self, value: float):
        command = f"SOUR:VOLT:SLEW:FALL"
        self._send_command(command, value=value, value_type=float, minimum=self.VOLT_FALL_MIN, maximum=self.VOLT_FALL_MAX)
        return True
    
    def set_voltage_slew_rise(self, value: float):
        command = f"SOUR:VOLT:SLEW:RIS"
        self._send_command(command, value=value, value_type=float, minimum=self.VOLT_RISE_MIN, maximum=self.VOLT_RISE_MAX)
        return True

    def system_beep(self, value: int=1):
        command = f"SYST:BEEP:IMM"
        self._send_command(command, value=value, value_type=int, minimum=self.BEEP_DUR_MIN, maximum=self.BEEP_DUR_MAX)
        return True

    def system_preset(self):
        command = "SYST:PRES"
        self._send_command(command)

    def system_error(self):
        message = "SYST:ERR?" 
        return self._send_read(message)
    
    def test_device(self):
        message = "*TST?"
        error_code = int(self._send_read(message))
        return error_code

def raise_for_range(value, minimum, maximum):
    if (minimum and value < minimum) or (maximum and value > maximum):
        raise ValueError(f"Value outside acceptable range: {minimum} - {maximum}")

def raise_for_type(value, expected_type):
    if type(value) is int and expected_type is float:
        return
    if type(value) is not expected_type:
        raise TypeError(f'Expected type {expected_type}, got type {type(value)}')

def percent_error(expected_value, actual_value):
    percent_error = abs((expected_value - actual_value)/expected_value)*100
    return percent_error

def main():
    TCP_IP = "192.168.1.101"
    PORT = 2268
    driver = GWINSTEK_driver(TCP_IP, PORT)

    print("\n[DEVICE STATUS]")
    print(f"error status: {driver.test_device()}")

    print("\n[SYSTEM INFO]")
    for key in driver.system_info:
        print(f"{key}: {driver.system_info[key]}")

    driver.set_voltage(6)
    driver.set_current(0.02)
    print("\n[SETTINGS]")
    print(f"current: {driver.get_current()}")
    print(f"current_slew_fall: {driver.get_current_slew_fall()}")
    print(f"current slew rise: {driver.get_current_slew_rise()}")
    print(f"over current protection (OCP): {driver.get_ocp()}")
    print(f"voltage: {driver.get_voltage()}")
    print(f"voltage slew fall: {driver.get_voltage_slew_fall()}")
    print(f"voltage slew rise: {driver.get_voltage_slew_fall()}")
    print(f"over voltage protection (OVP): {driver.get_ovp()}")
    print(f"series resistance: {driver.get_series_resistance()}")
    print(f"output mode: {driver.get_output_mode()}")
    print(f"smoothing level: {driver.get_sense_avg_count()}")
    print("\n[MEASUREMENTS]")
    print(f"measured voltage: {driver.measure_voltage()}")
    print(f"measured current: {driver.measure_current()}")
    print(f"measured power: {driver.measure_power()}")

if __name__ == "__main__":

    main()

    


'''
    TERMINAL TESTING SET UP

TCP_IP = "192.168.1.101"
PORT = 2268
import socket
def _send_read(message: str):
    if not message.endswith('\n'):
        message += '\n'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
        s.connect((TCP_IP, PORT))
        s.send(message.encode())
        try:
            response = s.recv(256).decode().replace('\n','')
        except TimeoutError as err:
            print(f"[LAST MESSAGE]: {message}")
            raise err
        return response

def _send(message: str):
    if not message.endswith('\n'):
        message += '\n'
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:    
        s.connect((TCP_IP, PORT))
        s.send(message.encode())

import pdb
import GWINSTEK_driver
pdb.run('GWINSTEK_driver.main()')

'''
