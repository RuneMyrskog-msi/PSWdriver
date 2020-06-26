import unittest
import socket
import threading

try:
    from GWINSTEK_driver import GWINSTEK_driver
except ModuleNotFoundError:
    from driver.GWINSTEK_driver import GWINSTEK_driver

class Test_GWINSTEK_driver(unittest.TestCase): 

    def setUp(self):
        self.driver = GWINSTEK_driver("192.168.1.101",2268)
        
    
    def test_send(self):
        HOST = socket.gethostname()
        PORT = 8080
        
        def driver_thread():
            self.driver.TCP_IP = HOST
            self.driver.PORT = PORT
            self.driver._send("TEST")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            driver_thread = threading.Thread(target=driver_thread)
            driver_thread.start()
            conn, addr = server_socket.accept()
            msg = conn.recv(256).decode()
            conn.close()
        self.assertTrue(msg.endswith('\n'))
        self.assertEqual(msg, "TEST\n")
    
    def test_send_read(self):
        HOST = socket.gethostname()
        PORT = 8080

        def driver_thread():
            self.driver.TCP_IP = HOST
            self.driver.PORT = PORT
            response = self.driver._send_read("TEST")
            self.assertEqual(response, "TEST")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            driver_thread = threading.Thread(target=driver_thread)
            driver_thread.start()
            conn, addr = server_socket.accept()
            msg = conn.recv(256).decode()
            conn.send(msg.encode())
            conn.close()
        
        self.assertTrue(msg.endswith('\n'))
        

    def test_get_system_info(self):
        sys_info = self.driver._get_system_info()
        self.assertTrue(type(sys_info) is dict)
        self.assertEqual(len(sys_info.keys()), 10)
        for key in sys_info:
            self.assertTrue(type(sys_info[key]) is str)

    def test_set_get_voltage(self):
        self.driver.set_voltage(1.5)
        self.assertRaises(ValueError, self.driver.set_voltage, self.driver.VOLT_MAX + 1)
        self.assertRaises(ValueError, self.driver.set_voltage, self.driver.VOLT_MIN - 1)

        return_value = self.driver.get_voltage()
        self.assertTrue(type(return_value) is float)
        self.assertEqual(return_value, 1.5)

    def test_set_get_current(self):
        self.driver.set_current(0.1)
        self.assertRaises(ValueError, self.driver.set_current, self.driver.CURR_MAX + 1)
        self.assertRaises(ValueError, self.driver.set_current, self.driver.CURR_MIN - 1)
        
        return_value = self.driver.get_current()
        self.assertTrue(type(return_value) is float)
        self.assertEqual(return_value, 0.1)

if __name__ == "__main__":
    unittest.main()