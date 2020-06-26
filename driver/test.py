import unittest
from unittest.mock import Mock
from GWINSTEK_driver import GWINSTEK_driver


class Test_GWINSTEK_driver(unittest.TestCase):
    @unittest.mock.patch('GWINSTEK_driver.GWINSTEK_driver', autospec=True)
    def setUp(self, mock_driver):
        
        self.driver = mock_driver("192.168.1.101",2268)
        
        
    
    def test_send(self):
        print(self.driver)

if __name__ == "__main__":
    unittest.main()



