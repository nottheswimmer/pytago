from unittest import TestCase

from pythagoras import python_to_go


def assert_examples_match(test_case: TestCase, example: str):
    with open(f"./pythagoras/tests/examples/{example}.py") as a, \
            open(f"./pythagoras/tests/examples/{example}.go") as b:
        test_case.assertEqual(python_to_go(a.read()), b.read())


class Test(TestCase):
    def test_hello_world(self):
        assert_examples_match(self, "helloworld")
