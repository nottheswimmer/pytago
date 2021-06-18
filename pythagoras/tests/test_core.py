import os
from unittest import TestCase

from pythagoras import python_to_go

# Change directories to the location of the test for consistency between testing environments
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class Test(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def assert_examples_match(self, example: str):
        with open(f"../../examples/{example}.py") as a, \
                open(f"../../examples/{example}.go") as b:
            self.assertEqual(b.read(), python_to_go(a.read()))

    def test_hello_world(self):
        self.assert_examples_match("helloworld")

    def test_add(self):
        self.assert_examples_match("add")

    def test_exponents(self):
        self.assert_examples_match("exponents")

    def test_variables(self):
        self.assert_examples_match("variables")

    def test_floats(self):
        self.assert_examples_match("floats")

    def test_numlist(self):
        self.assert_examples_match("numlist")

    def test_loops(self):
        self.assert_examples_match("loops")

    def test_strings(self):
        self.assert_examples_match("strings")

    def test_logical(self):
        self.assert_examples_match("logical")

    def test_maths(self):
        self.assert_examples_match("maths")

    def test_requestslib(self):
        self.assert_examples_match("requestslib")

    def test_conditionals(self):
        self.assert_examples_match("conditionals")

    def test_fstrings(self):
        self.assert_examples_match("fstrings")

    def test_nestedfstrings(self):
        self.assert_examples_match("nestedfstrings")

    def test_dictionary(self):
        self.assert_examples_match("dictionary")

    def test_writefile(self):
        self.assert_examples_match("writefile")

    def test_pass(self):
        self.assert_examples_match("pass")

    def test_ellipsis(self):
        self.assert_examples_match("ellipsis")

    def test_missingreturntype(self):
        self.assert_examples_match("missingreturntype")

    # def test_lambdafunc(self):
    #     self.assert_examples_match("lambdafunc")

    def test_continuestmt(self):
        self.assert_examples_match("continuestmt")

    def test_breakstmt(self):
        self.assert_examples_match("breakstmt")

    def test_whileloop(self):
        self.assert_examples_match("whileloop")

    def test_sets(self):
        self.assert_examples_match("sets")

    def test_contains(self):
        self.assert_examples_match("contains")

    def test_tryexcept(self):
        self.assert_examples_match("tryexcept")

    def test_tryfinally(self):
        self.assert_examples_match("tryfinally")

    def test_asserts(self):
        self.assert_examples_match("asserts")

    def test_classes(self):
        return self.assert_examples_match("classes")

    def test_globals(self):
        return self.assert_examples_match("globals")

    def test_asyncawait(self):
        return self.assert_examples_match("asyncawait")

    def test_yields(self):
        return self.assert_examples_match("yields")

    def test_isvseql(self):
        return self.assert_examples_match("isvseql")

    def test_matchcase(self):
        return self.assert_examples_match("matchcase")

    def test_defaultargs(self):
        return self.assert_examples_match("defaultargs")

    # List methods
    def test_listappend(self):
        return self.assert_examples_match("listappend")

    # Algorithms
    def test_algomajorityelement(self):
        return self.assert_examples_match("algomajorityelement")
