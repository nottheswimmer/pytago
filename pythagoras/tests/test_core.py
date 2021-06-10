import os
from unittest import TestCase

from pythagoras import python_to_go

# Change directories to the location of the test for consistency between testing environments
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def assert_examples_match(test_case: TestCase, example: str):
    with open(f"../../examples/{example}.py") as a, \
            open(f"../../examples/{example}.go") as b:
        test_case.assertEqual(python_to_go(a.read()), b.read())


class Test(TestCase):
    def test_hello_world(self):
        assert_examples_match(self, "helloworld")

    def test_add(self):
        assert_examples_match(self, "add")

    def test_exponents(self):
        assert_examples_match(self, "exponents")

    def test_variables(self):
        assert_examples_match(self, "variables")

    def test_floats(self):
        assert_examples_match(self, "floats")

    def test_numlist(self):
        assert_examples_match(self, "numlist")

    def test_loops(self):
        assert_examples_match(self, "loops")

    def test_strings(self):
        assert_examples_match(self, "strings")

    def test_logical(self):
        assert_examples_match(self, "logical")

    def test_maths(self):
        assert_examples_match(self, "maths")

    def test_requestslib(self):
        assert_examples_match(self, "requestslib")

    def test_conditionals(self):
        assert_examples_match(self, "conditionals")

    def test_fstrings(self):
        assert_examples_match(self, "fstrings")

    def test_nestedfstrings(self):
        assert_examples_match(self, "nestedfstrings")

    def test_dictionary(self):
        assert_examples_match(self, "dictionary")

    def test_writefile(self):
        assert_examples_match(self, "writefile")
