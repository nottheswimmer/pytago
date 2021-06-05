from unittest import TestCase

from pythagoras import add


class Test(TestCase):
    def test_add(self):
        self.assertEqual(add(2, 2), 4)
