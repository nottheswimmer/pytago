import glob
from os.path import split

HEADER_PATH = 'README_HEADER.md'
EXAMPLES_PATH = "../examples"
README_DESTINATION = "../README.md"
TEST_FILE_PATH = "../pytago/tests/test_core.py"

DISABLED_EXAMPLES = {
    "forelse",
    "iterunpacking",
    "dunders",
    "pop",
    "ingenerator"
}

def get_usage_string():
    import subprocess
    out = subprocess.check_output(["pytago", "-h"])
    return '\n'.join(out.decode().splitlines())

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
    for i, example in enumerate(examples):
        example_name = split(example)[-1].removesuffix(".py").removesuffix(".go")
        if example_name in DISABLED_EXAMPLES:
            continue
        is_python = i % 2 == 0
        if is_python:
            parts.append(f'### {example_name}')
        with open(example) as f:
            if is_python:
                parts.append("""#### Python""")
            else:
                parts.append("""#### Go""")
            parts.append('```' + ("python" if is_python else "go"))
            for line in f.read().splitlines(keepends=False):
                if is_python and line.strip().startswith('#'):
                    continue
                parts.append(line)
            parts.append("```")
    example_code = '\n'.join(parts)
    with open(README_DESTINATION, "w") as f:
        t = TEMPLATE.replace('{% usage %}', get_usage_string())
        t = t.replace('{% examples %}', example_code)
        f.write(t)

if __name__ == '__main__':
    main()