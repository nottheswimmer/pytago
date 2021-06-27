import os
from unittest import TestCase

from pytago import python_to_go

# Change directories to the location of the test for consistency between testing environments
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class Test(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxDiff = None

    def assert_examples_match(self, example: str):
        with open(f"../../examples/{example}.py", encoding="utf_8") as a, \
                open(f"../../examples/{example}.go", encoding="utf_8") as b:
            self.assertEqual(b.read(), python_to_go(a.read()))

    def test_hello_world(self):
        self.assert_examples_match("helloworld")

    def test_input(self):
        self.assert_examples_match("input")

    def test_randomness(self):
        self.assert_examples_match("randomness")

    def test_string_methods(self):
        self.assert_examples_match("string_methods")

    def test_list_methods(self):
        self.assert_examples_match("list_methods")

    def test_set_methods(self):
        self.assert_examples_match("set_methods")

    def test_global_code(self):
        self.assert_examples_match("global_code")

    def test_boolnumcompare(self):
        self.assert_examples_match("boolnumcompare")

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
        self.assert_examples_match("classes")

    def test_globals(self):
        self.assert_examples_match("globals")

    def test_asyncawait(self):
        self.assert_examples_match("asyncawait")

    def test_yields(self):
        self.assert_examples_match("yields")

    def test_isvseql(self):
        self.assert_examples_match("isvseql")

    def test_matchcase(self):
        self.assert_examples_match("matchcase")

    def test_defaultargs(self):
        self.assert_examples_match("defaultargs")

    def test_walrus(self):
        self.assert_examples_match("walrus")

    def test_truthiness(self):
        self.assert_examples_match("truthiness")

    def test_minmax(self):
        self.assert_examples_match("minmax")

    def test_sum(self):
        self.assert_examples_match("sum")

    def test_reverse(self):
        self.assert_examples_match("reverse")

    def test_listcomp(self):
        self.assert_examples_match("listcomp")

    def test_dictcomp(self):
        self.assert_examples_match("dictcomp")

    def test_setcomp(self):
        self.assert_examples_match("setcomp")

    def test_generatorexp(self):
        self.assert_examples_match("generatorexp")

    def test_ternary(self):
        self.assert_examples_match("ternary")

    def test_abs(self):
        self.assert_examples_match("abs")

    def test_isinstance(self):
        self.assert_examples_match("isinstance")

    def test_zip(self):
        self.assert_examples_match("zip")

    def test_map(self):
        self.assert_examples_match("map")

    def test_repr(self):
        self.assert_examples_match("repr")

    def test_lambdafunc(self):
        self.assert_examples_match("lambdafunc")

    def test_timemodule(self):
        self.assert_examples_match("timemodule")

    def test_exit(self):
        self.assert_examples_match("exit")


    # Algorithms
    def test_algomajorityelement(self):
        self.assert_examples_match("algomajorityelement")

    # In development

    # def test_forelse(self):
    #     self.assert_examples_match("forelse")
    #
    # def test_iterunpacking(self):
    #     self.assert_examples_match("iterunpacking")

    # def test_ingenerator(self):
    #     self.assert_examples_match("ingenerator")

    #     def test_dunders(self):
    #         self.assert_examples_match("dunders")

    # def test_pop(self):
    #     self.assert_examples_match("pop")
    #
    # def test_index(self):
    #     self.assert_examples_match("index")
