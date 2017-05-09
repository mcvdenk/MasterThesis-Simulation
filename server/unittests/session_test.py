from bson import objectid
import unittest
from datetime import datetime
import time

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from session import *

class TestSession(unittest.TestCase):
    
    def setUp(self):
        self.start = datetime.now()
        self.session = Session(browser = "Win32")

    def tearDown(self):
        del self.session

    def test_start(self):
        self.assertAlmostEqual(self.session.start.timestamp(), self.start.timestamp(), delta = 1)

    def test_browser(self):
        self.assertEqual(self.session.browser, "Win32")

    def test_end_session(self):
        end = datetime.now()
        self.session.end_session()
        self.assertAlmostEqual(self.session.end.timestamp(), end.timestamp(), delta = 1)


if __name__ == '__main__':
    f = open("test_output.txt", "w")
    runner = unittest.TextTestRunner(f)
    unittest.main(testRunner = runner, warnings = "ignore")
    f.close()
