import os
from pathlib import Path

rel = "" if os.getcwd().endswith("scripts") else "./scripts/"
TESt_PATH = rel + "../pytago/tests/test_core.py"

name = input("test name: ")

Path(rel + f"../examples/{name}.py").touch()
Path(rel + f"../examples/{name}.go").touch()

with open(rel + "../pytago/tests/test_core.py", "r") as f:
    if f"def test_{name}(self)" in f.read():
        print(f"test_{name} already exists, but I touched the files")
        exit(0)

with open(rel + "../pytago/tests/test_core.py", "a") as f:
    f.write(f"""
    def test_{name}(self):
        self.assert_examples_match("{name}")
""")
