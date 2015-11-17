# test_mymath.py
#
# Run tests with the command:
#   python3.5 -m unittest test_mymath.py

import unittest
import mymath

class TestFunctions(unittest.TestCase):

  def test_sum_positive(self):
      self.assertEqual(mymath.compute_sum(1, 2), 3)

  def test_sum_negative(self):
      self.assertEqual(mymath.compute_sum(-1, -2), -3)

  def test_error(self):
      with self.assertRaises(TypeError):
          mymath.compute_sum(None, None)

if __name__ == '__main__':
    unittest.main()