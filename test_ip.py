import unittest
from Project_one import *

class Testip(unittest.TestCase):

    re="(^(10).((25[0-5]|2[0-4][0-9])\.)((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$)"

    def test_correct_ip(self):
        self.assertRegexpMatches('10.205.1.5', self.re)

    def test_incorrect_ip(self):
        self.assertNotRegexpMatches('10.199.1.5', self.re)

    def test_bogus_ip(self):
        self.assertNotRegexpMatches('10.a.e.5', self.re)

if __name__== "__main__":
    unittest.main()