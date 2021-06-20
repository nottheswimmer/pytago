import glob
from os.path import split

HEADER_PATH = 'README_HEADER.md'
EXAMPLES_PATH = "../examples"
README_DESTINATION = "../README.md"

DISABLED_EXAMPLES = {
    "forelse",
    "lambdafunc"
}

def main():
    parts = []
    with open(HEADER_PATH) as f:
        TEMPLATE = f.read()
    examples = glob.glob(EXAMPLES_PATH + "/*")
    examples.sort(reverse=True)
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
            parts.append(f.read())
            parts.append("```")
    example_code = '\n'.join(parts)
    with open(README_DESTINATION, "w") as f:
        f.write(TEMPLATE.replace('{% examples %}', example_code))

if __name__ == '__main__':
    main()