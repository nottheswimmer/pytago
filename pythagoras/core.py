import ast
from subprocess import Popen, PIPE

# from pythagoras import go_ast


def python_to_go(python: str) -> str:
    tree = ast.parse(python)
    # go_code = go_ast.unparse(tree)
    return _gofmt("""\
package main
import "fmt"
func main() {
	fmt.Println("hello world")
}
""")


def _gofmt(code: str) -> str:
    p = Popen(["gofmt", "-s"], stdout=PIPE, stdin=PIPE)
    out, err = p.communicate(code.encode())
    return out.decode()


# Debugging
if __name__ == '__main__':
    print(python_to_go("""\
print("Hello world")
"""))
