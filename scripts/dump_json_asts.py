import glob
import os
from pathlib import Path

from pytago import dump_python_to_go_ast_as_json

EXAMPLES_PATH = "../examples"
OUTPUT_PATH = "../scratchwork/json_asts"


def main():
    examples = glob.glob(EXAMPLES_PATH + "/*")
    for example in examples:
        if not example.endswith(".py"):
            continue

        with open(example) as f:
            py_code = f.read()

        py_json = dump_python_to_go_ast_as_json(py_code)
        filename = os.path.split(example)[-1].removesuffix(".py") + ".json"
        output_location = Path(OUTPUT_PATH) / filename
        print(output_location)
        with open(output_location, "w") as f:
            f.write(py_json)


if __name__ == '__main__':
    main()

