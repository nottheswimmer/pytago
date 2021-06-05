from unittest import TestCase

from pythagoras import python_to_go


def test_example(test_case: TestCase, example: str):
    with open(f"examples/{example}.py") as a, open(f"examples/{example}.go") as b:
        test_case.assertEqual(python_to_go(a.read()), b.read())


class Test(TestCase):
    def test_hello_world(self):
        test_example(self, "helloworld")
