import glob
from os.path import split
import os

rel = "" if os.getcwd().endswith("scripts") else "./scripts/"

HEADER_PATH = rel + 'README_HEADER.md'
EXAMPLES_PATH = rel + "../examples"
README_DESTINATION = rel + "../README.md"
TEST_FILE_PATH = rel + "../pytago/tests/test_core.py"

DISABLED_EXAMPLES = {
    "iterunpacking",
    "dunders",
    "pop",
    "ingenerator"
}

def get_usage_string():
    import subprocess
    out = subprocess.check_output(["pytago", "-h"])
    return '\n'.join(out.decode().splitlines()).replace("Pytago", "pytago", 1)

def main():
    parts = []
    with open(HEADER_PATH) as f:
        TEMPLATE = f.read()

    with open(TEST_FILE_PATH) as f:
        TEST_CODE = f.read()

    def example_sort_key(a):
        ext = a.split('.')[-1]
        example_name = split(a)[-1].removesuffix(".py").removesuffix(".go")
        try:
            return TEST_CODE.index(example_name), 0 if ext == "py" else 1
        except ValueError:
            return -1, 0 if ext == "py" else 1


    examples = glob.glob(EXAMPLES_PATH + "/*")
    examples.sort(key=example_sort_key)

    # It's assumed that Python examples appear then Go examples
    for i, example in enumerate(examples):
        example_name = split(example)[-1].removesuffix(".py").removesuffix(".go")
        if example_name in DISABLED_EXAMPLES:
            continue
        is_python = i % 2 == 0
        if is_python:
            assert example.endswith(".py")
            parts.append(f'### {example_name}')
        else:
            assert example.endswith(".go")
        with open(example) as f:
            if is_python:
                parts.append("\n<table><tr><th>Python</th><th>Go</th></tr><tr><td>\n")
            else:
                parts.append("</td><td>\n")
            parts.append('```' + ("python" if is_python else "go"))
            for line in f.read().splitlines(keepends=False):
                if is_python and line.strip().startswith('#'):
                    continue
                parts.append(line)
            parts.append("```")
            if not is_python:
                parts.append('</td></tr></table>\n')
    example_code = '\n'.join(parts)
    with open(README_DESTINATION, "w") as f:
        t = TEMPLATE.replace('{% usage %}', get_usage_string())
        t = t.replace('{% examples %}', example_code)
        f.write(t)

if __name__ == '__main__':
    main()