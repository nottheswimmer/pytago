# pytago

Transpiles some Python into human-readable Golang.

- [Try out the web demo](https://pytago.dev/)

## Installation and usage

There are two "officially" supported ways to use Pytago:
1. A web application you can run via docker
2. A locally-installed command-line tool

### Web application

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

#### Installation

```
git clone https://github.com/nottheswimmer/pytago/
cd pytago
docker build -t pytago .
```

#### Usage
```
docker run -p 8080:8080 -e PORT=8080 -it pytago

# User interface
open http://127.0.0.1:8080/

# API
curl --request POST 'http://127.0.0.1:8080/' \
  --header 'Content-Type: application/json'  \
  --data-raw '{"py": "print(\"Hello World\")"}'
```

### Local command-line application

#### Prerequisites

- [Go 1.16.x](https://golang.org/dl/)
- [Python 3.10.x](https://www.python.org/downloads/release/python-3100b3/)
  - No, it will not work on 3.9. Search the code for "match."
- `go get golang.org/x/tools/cmd/goimports`
- `go get mvdan.cc/gofumpt`

#### Installation

##### via pip
```
pip install pytago
```

##### via setup.py (dev)

```
git clone https://github.com/nottheswimmer/pytago/
cd pytago
pip install -e .
```

##### via setup.py

```
git clone https://github.com/nottheswimmer/pytago/
cd pytago
pip install .
```

#### Usage

```
usage: pytago [-h] [-o OUTFILE] INFILE

positional arguments:
  INFILE                read python code from INFILE

options:
  -h, --help            show this help message and exit
  -o OUTFILE, --out OUTFILE
                        write go code to OUTFILE
```

## Examples

All examples presented here are used as tests for the program.

### listappend
#### Python
```python
def main():
    a = [1, 2, 3]
    a.append(4)
    print(a)

if __name__ == '__main__':
    main()
```
#### Go
```go
int: 1
int: 5
str: hello
int: 5
int: 12
int: 19
unknown: 12.5
unknown: [1, 2, 3]
```
### listappend
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	a = append(a, 4)
	fmt.Println(a)
}
```
#### Go
```go
def main():
    print(abs(-6))
    print(abs(3))

if __name__ == '__main__':
    main()
```
### abs
#### Python
```python
package main

import (
	"fmt"
	"math"
)

func main() {
	fmt.Println(math.Abs(-6))
	fmt.Println(math.Abs(3))
}
```
#### Go
```go
def main():
    print("hello world")


if __name__ == '__main__':
    main()
```
### helloworld
#### Python
```python
package main

import "fmt"

func main() {
	fmt.Println("hello world")
}
```
#### Go
```go
def main():
    print("Hi, what's your name?")
    name = input("Name: ")
    print("Hi", name, "how old are you?")
    age = int(input("Age: "))
    print("Describe yourself in one sentence:")
    description = input()
    print("So your name is", name, "and you are", age, "years old, and your description is", '"' + description + '"')


if __name__ == '__main__':
    main()
```
### input
#### Python
```python
package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	fmt.Println("Hi, what's your name?")
	name := func(msg string) string {
		fmt.Print(msg)
		text, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		return strings.ReplaceAll(text, "\n", "")
	}("Name: ")
	fmt.Println("Hi", name, "how old are you?")
	age := func() int {
		i, err := strconv.ParseInt(func(msg string) string {
			fmt.Print(msg)
			text, _ := bufio.NewReader(os.Stdin).ReadString('\n')
			return strings.ReplaceAll(text, "\n", "")
		}("Age: "), 10, 64)
		if err != nil {
			panic(err)
		}
		return int(i)
	}()
	fmt.Println("Describe yourself in one sentence:")
	description := func() string {
		text, _ := bufio.NewReader(os.Stdin).ReadString('\n')
		return strings.ReplaceAll(text, "\n", "")
	}()
	fmt.Println("So your name is", name, "and you are", age, "years old, and your description is", "\""+description+"\"")
}
```
#### Go
```go
import random


def main():
    print(random.random())
    print(random.randrange(9000, 10000))
    print(random.randint(9000, 10000))
    items = ["Hello", 3, "Potato", "Cake"]
    print(random.choice(items))
    random.shuffle(items)
    print(items)
    u = random.uniform(200, 500)
    print(u)
    if random.random() > 0.5:
        print("50/50")


if __name__ == '__main__':
    main()
```
### randomness
#### Python
```python
package main

import (
	"fmt"
	"math/rand"
	"time"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

func main() {
	fmt.Println(rand.Float64())
	fmt.Println(func(start int, stop int) int {
		n := stop - start
		return rand.Intn(n) + start
	}(9000, 10000))
	fmt.Println(func(start int, stop int) int {
		n := stop - start
		return rand.Intn(n) + start
	}(9000, 10000+1))
	items := []interface{}{"Hello", 3, "Potato", "Cake"}
	fmt.Println(items[rand.Intn(len(items))])
	rand.Shuffle(len(items), func(i int, j int) {
		items[i], items[j] = items[j], items[i]
	})
	fmt.Println(items)
	u := func(a float64, b float64) float64 {
		return rand.Float64()*(b-a) + b
	}(200, 500)
	fmt.Println(u)
	if rand.Float64() > 0.5 {
		fmt.Println("50/50")
	}
}
```
#### Go
```go
def main():
    lower = "hello world"
    crazy = "HeLLo WoRlD"
    upper = "HELLO WORLD"
    lol = "---LOL---"
    hearts = "🧡💛💚💙💜"
    arabic_indic_digit = "٠"
    whitespace = " \v\f\t\r\n"
    s_hello_s = whitespace + lower + whitespace
    multiline = lower + "\n" + crazy + "\r\n" + upper + "\n"

    print(crazy.capitalize())
    print(lower.endswith("world"))
    print(lower.find(" "))
    print(lower.find(" ", 2))
    print(upper.find(" ", 7, 8))
    print(lower.index(" "))
    print(lower.index(" ", 2))
    print(upper.index(" ", 2, 8))
    print(lower.isalnum())
    print(hearts.isascii())
    print(arabic_indic_digit.isdecimal())
    print(arabic_indic_digit.isdigit())
    print(lower.islower())
    print(arabic_indic_digit.isnumeric())
    print(hearts.isprintable())
    print(whitespace.isspace())
    print(upper.isupper())
    print(hearts.join([lower, crazy, upper]))
    print(crazy.lower())
    print(s_hello_s.lstrip() + "|")
    print(lower.lstrip("h"))
    print(lower.removeprefix("hello "))
    print(lower.removesuffix(" world"))
    print(lower.replace("world", "gophers"))
    print(upper.replace("O", "OOOOO", 1))
    print(upper.rfind("O"))
    print(upper.rfind("O", 1))
    print(upper.rfind("O", 1, 6))
    print(upper.rindex("O"))
    print(upper.rindex("O", 1))
    print(upper.rindex("O", 1, 6))
    print(s_hello_s.rstrip() + "|")
    print(lower.rstrip("d"))
    print(lower.split())
    print(upper.split("L"))
    print(upper.split("L", 1))
    print(multiline.splitlines())
    print(upper.startswith("HELLO"))
    print(s_hello_s.strip() + "|")
    print(lol.strip("-"))
    print(crazy.title())
    print(crazy.upper())


if __name__ == '__main__':
    main()
```
### string_methods
#### Python
```python
package main

import (
	"bufio"
	"errors"
	"fmt"
	"strings"
	"unicode"
)

func main() {
	lower := "hello world"
	crazy := "HeLLo WoRlD"
	upper := "HELLO WORLD"
	lol := "---LOL---"
	hearts := "🧡💛💚💙💜"
	arabic_indic_digit := "٠"
	whitespace := " \u000b\f\t\r\n"
	s_hello_s := whitespace + lower + whitespace
	multiline := lower + "\n" + crazy + "\r\n" + upper + "\n"
	fmt.Println(strings.ToUpper(crazy[0:1]) + strings.ToLower(crazy[1:]))
	fmt.Println(strings.HasSuffix(lower, "world"))
	fmt.Println(strings.Index(lower, " "))
	fmt.Println(func() int {
		if r := strings.Index(lower[2:], " "); r != -1 {
			return r + 2
		}
		return -1
	}())
	fmt.Println(func() int {
		if r := strings.Index(upper[7:8], " "); r != -1 {
			return r + 7
		}
		return -1
	}())
	fmt.Println(func(X string, sub string) int {
		if i := strings.Index(X, sub); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(lower, " "))
	fmt.Println(func(X string, sub string, start int) int {
		if i := func() int {
			if r := strings.Index(X[start:], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(lower, " ", 2))
	fmt.Println(func(X string, sub string, start int, end int) int {
		if i := func() int {
			if r := strings.Index(X[start:end], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, " ", 2, 8))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !((unicode.IsLetter(r) || unicode.IsDigit(r)) && (unicode.IsDigit(r) || unicode.IsNumber(r))) {
				return false
			}
		}
		return true
	}(lower))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if r > unicode.MaxASCII {
				return false
			}
		}
		return true
	}(hearts))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.Is(unicode.Nd, r) {
				return false
			}
		}
		return len(X) != 0
	}(arabic_indic_digit))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.IsDigit(r) {
				return false
			}
		}
		return len(X) != 0
	}(arabic_indic_digit))
	fmt.Println(func(X string) bool {
		lower_found := false
		for _, r := range X {
			if !unicode.IsLower(r) {
				if !unicode.IsSpace(r) {
					return false
				}
			} else {
				lower_found = true
			}
		}
		return lower_found && len(X) != 0
	}(lower))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !(unicode.IsDigit(r) || unicode.IsNumber(r)) {
				return false
			}
		}
		return len(X) != 0
	}(arabic_indic_digit))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.IsPrint(r) {
				return false
			}
		}
		return true
	}(hearts))
	fmt.Println(func(X string) bool {
		for _, r := range X {
			if !unicode.IsSpace(r) {
				return false
			}
		}
		return len(X) != 0
	}(whitespace))
	fmt.Println(func(X string) bool {
		upper_found := false
		for _, r := range X {
			if !unicode.IsUpper(r) {
				if !unicode.IsSpace(r) {
					return false
				}
			} else {
				upper_found = true
			}
		}
		return upper_found && len(X) != 0
	}(upper))
	fmt.Println(strings.Join([]string{lower, crazy, upper}, hearts))
	fmt.Println(strings.ToLower(crazy))
	fmt.Println(strings.TrimLeftFunc(s_hello_s, unicode.IsSpace) + "|")
	fmt.Println(strings.TrimLeft(lower, "h"))
	fmt.Println(strings.TrimPrefix(lower, "hello "))
	fmt.Println(strings.TrimSuffix(lower, " world"))
	fmt.Println(strings.ReplaceAll(lower, "world", "gophers"))
	fmt.Println(strings.Replace(upper, "O", "OOOOO", 1))
	fmt.Println(strings.LastIndex(upper, "O"))
	fmt.Println(func() int {
		if r := strings.LastIndex(upper[1:], "O"); r != -1 {
			return r + 1
		}
		return -1
	}())
	fmt.Println(func() int {
		if r := strings.LastIndex(upper[1:6], "O"); r != -1 {
			return r + 1
		}
		return -1
	}())
	fmt.Println(func(X string, sub string) int {
		if i := strings.LastIndex(X, sub); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, "O"))
	fmt.Println(func(X string, sub string, start int) int {
		if i := func() int {
			if r := strings.LastIndex(X[start:], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, "O", 1))
	fmt.Println(func(X string, sub string, start int, end int) int {
		if i := func() int {
			if r := strings.LastIndex(X[start:end], sub); r != -1 {
				return r + start
			}
			return -1
		}(); i != -1 {
			return i
		}
		panic(errors.New("ValueError: substring not found"))
	}(upper, "O", 1, 6))
	fmt.Println(strings.TrimRightFunc(s_hello_s, unicode.IsSpace) + "|")
	fmt.Println(strings.TrimRight(lower, "d"))
	fmt.Println(strings.Fields(lower))
	fmt.Println(strings.Split(upper, "L"))
	fmt.Println(strings.SplitN(upper, "L", 1))
	fmt.Println(func(s string) (lines []string) {
		sc := bufio.NewScanner(strings.NewReader(s))
		for sc.Scan() {
			lines = append(lines, sc.Text())
		}
		return
	}(multiline))
	fmt.Println(strings.HasPrefix(upper, "HELLO"))
	fmt.Println(strings.TrimSpace(s_hello_s) + "|")
	fmt.Println(strings.Trim(lol, "-"))
	fmt.Println(func(s string) string {
		ws := true
		var sb strings.Builder
		for _, r := range s {
			if unicode.IsSpace(r) {
				ws = true
				sb.WriteRune(r)
			} else if ws {
				ws = false
				sb.WriteRune(unicode.ToUpper(r))
			} else {
				sb.WriteRune(unicode.ToLower(r))
			}
		}
		return sb.String()
	}(crazy))
	fmt.Println(strings.ToUpper(crazy))
}
```
#### Go
```go
def main():
    l1 = [1]
    l2 = ["hello", "how", "are", "you?"]
    l3 = [6.2, 1.6, 1.2, 20.1]

    l1.append(2)
    print(l1)

    l1.extend([4, 5])
    print(l1)

    l1.insert(3, 3)
    print(l1)

    print(l1.index(2))

    print(l1.count(3))

    l1.remove(3)
    print(l1)

    while l1:
        print(l1.pop())

    l3.clear()
    print(l3)

    l1.sort()
    print(l1)
    l2.sort()
    print(l2)
    l3.sort()
    print(l3)
    l3.sort(reverse=True)
    print(l3)

    l2.reverse()
    print(l2)

    l4 = l2.copy()
    l4.pop()
    print(l4)
    print(l2)

if __name__ == '__main__':
    main()
```
### list_methods
#### Python
```python
package main

import (
	"errors"
	"fmt"
	"reflect"
	"sort"
)

func main() {
	l1 := []int{1}
	l2 := []string{"hello", "how", "are", "you?"}
	l3 := []float64{6.2, 1.6, 1.2, 20.1}
	l1 = append(l1, 2)
	fmt.Println(l1)
	l1 = append(l1, []int{4, 5}...)
	fmt.Println(l1)
	l1 = append(l1, 3)
	copy(l1[3+1:], l1[3:])
	l1[3] = 3
	fmt.Println(l1)
	fmt.Println(func() int {
		for i, val := range l1 {
			if val == 2 {
				return i
			}
		}
		panic(errors.New("ValueError: element not found"))
	}())
	fmt.Println(func() int {
		n := 0
		for _, v := range l1 {
			if v == 3 {
				n += 1
			}
		}
		return n
	}())
	func(s *[]int, x int) {
		for i, val := range *s {
			if reflect.DeepEqual(val, x) {
				*s = append((*s)[:i], (*s)[i+1:]...)
				return
			}
		}
		panic(errors.New("ValueError: element not found"))
	}(&l1, 3)
	fmt.Println(l1)
	for len(l1) != 0 {
		fmt.Println(func(s *[]int) int {
			i := len(*s) - 1
			popped := (*s)[i]
			*s = (*s)[:i]
			return popped
		}(&l1))
	}
	l3 = nil
	fmt.Println(l3)
	sort.Ints(l1)
	fmt.Println(l1)
	sort.Strings(l2)
	fmt.Println(l2)
	sort.Float64s(l3)
	fmt.Println(l3)
	sort.Sort(sort.Reverse(sort.Float64Slice(l3)))
	fmt.Println(l3)
	func(arr []string) {
		for i, j := 0, len(arr)-1; i < j; i, j = i+1, j-1 {
			arr[i], arr[j] = arr[j], arr[i]
		}
	}(l2)
	fmt.Println(l2)
	l4 := func(s *[]string) (tmp []string) {
		tmp = append(tmp, *s...)
		return
	}(&l2)
	func(s *[]string) string {
		i := len(*s) - 1
		popped := (*s)[i]
		*s = (*s)[:i]
		return popped
	}(&l4)
	fmt.Println(l4)
	fmt.Println(l2)
}
```
#### Go
```go
def main():
    a = {1, 2, 3, 4}
    b = {4, 5, 6}
    b.add(7)
    print(a.union(b))
    print(a.intersection(b))
    print(a.difference(b))
    print(a.symmetric_difference(b))

    print(a.issubset(b))
    print(a.issuperset(b))


if __name__ == '__main__':
    main()
```
### set_methods
#### Python
```python
package main

import "fmt"

func main() {
	a := map[int]struct{}{1: {}, 2: {}, 3: {}, 4: {}}
	b := map[int]struct{}{4: {}, 5: {}, 6: {}}
	b[7] = struct{}{}
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		union := map[interface{}]struct{}{}
		for elt := range s1 {
			union[elt] = struct{}{}
		}
		for elt := range s2 {
			union[elt] = struct{}{}
		}
		return union
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		intersection := map[interface{}]struct{}{}
		for elt := range s1 {
			if func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				intersection[elt] = struct{}{}
			}
		}
		return intersection
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		difference := map[interface{}]struct{}{}
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				difference[elt] = struct{}{}
			}
		}
		return difference
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) map[interface{}]struct{} {
		symmetric_difference := map[interface{}]struct{}{}
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				symmetric_difference[elt] = struct{}{}
			}
		}
		for elt := range s2 {
			if !func() bool {
				_, ok := s1[elt]
				return ok
			}() {
				symmetric_difference[elt] = struct{}{}
			}
		}
		return symmetric_difference
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) bool {
		for elt := range s1 {
			if !func() bool {
				_, ok := s2[elt]
				return ok
			}() {
				return false
			}
		}
		return true
	}(a, b))
	fmt.Println(func(s1 map[int]struct{}, s2 map[int]struct{}) bool {
		for elt := range s2 {
			if !func() bool {
				_, ok := s1[elt]
				return ok
			}() {
				return false
			}
		}
		return true
	}(a, b))
}
```
#### Go
```go
A = [1, 2, 3]

for i, x in enumerate(A):
    A[i] += x

B = A[0]
C = A[0]
D: int = 3

while C < A[2]:
    C += 1

if C == A[2]:
    print('True')


def main():
    print("Main started")
    print(A)
    print(B)
    print(C)
    print(D)


if __name__ == '__main__':
    main()
```
### global_code
#### Python
```python
package main

import "fmt"

var (
	A = []int{1, 2, 3}
	B int
	C int
	D int
)

func init() {
	for i, x := range A {
		A[i] += x
	}
	B = A[0]
	C = A[0]
	D = 3
	for C < A[2] {
		C += 1
	}
	if C == A[2] {
		fmt.Println("True")
	}
}

func main() {
	fmt.Println("Main started")
	fmt.Println(A)
	fmt.Println(B)
	fmt.Println(C)
	fmt.Println(D)
}
```
#### Go
```go
def main():
    print(1 == True)
    print(1 == False)
    print(0 == True)
    print(0 == False)
    print()
    print(1. == True)
    print(1. == False)
    print(0. == True)
    print(0. == False)
    print()
    print(1+0j == True)
    print(1+0j == False)
    print(0+0j == True)
    print(0+0j == False)
    print()
    print(2 == True)

if __name__ == '__main__':
    main()
```
### boolnumcompare
#### Python
```python
package main

import "fmt"

func main() {
	fmt.Println(1 == 1)
	fmt.Println(1 == 0)
	fmt.Println(0 == 1)
	fmt.Println(0 == 0)
	fmt.Println()
	fmt.Println(1.0 == 1)
	fmt.Println(1.0 == 0)
	fmt.Println(0.0 == 1)
	fmt.Println(0.0 == 0)
	fmt.Println()
	fmt.Println(1+0.0i == 1)
	fmt.Println(1+0.0i == 0)
	fmt.Println(0+0.0i == 1)
	fmt.Println(0+0.0i == 0)
	fmt.Println()
	fmt.Println(2 == 1)
}
```
#### Go
```go
def main():
    print(add(2, 2))


def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    main()
```
### add
#### Python
```python
package main

import "fmt"

func main() {
	fmt.Println(add(2, 2))
}

func add(a int, b int) int {
	return a + b
}
```
#### Go
```go
def main():
    print(2 ** 8)


if __name__ == '__main__':
    main()
```
### exponents
#### Python
```python
package main

import (
	"fmt"
	"math"
)

func main() {
	fmt.Println(int(math.Pow(2, 8)))
}
```
#### Go
```go
def main():
    a = 3
    b = 7
    a = a + b
    print(a + b)
    another_scope()


def another_scope():
    a = 1
    b = 12
    a = a + b
    print(a + b)


if __name__ == '__main__':
    main()
```
### variables
#### Python
```python
package main

import "fmt"

func main() {
	a := 3
	b := 7
	a = a + b
	fmt.Println(a + b)
	another_scope()
}

func another_scope() {
	a := 1
	b := 12
	a = a + b
	fmt.Println(a + b)
}
```
#### Go
```go
def main():
    a = 7
    b = 3
    c = 4.5
    print(a / b)
    print(a // b)
    print(a / c)
    print(a // c)
    print(a + b)
    print(a + c)


if __name__ == '__main__':
    main()
```
### floats
#### Python
```python
package main

import (
	"fmt"
	"math"
)

func main() {
	a := 7
	b := 3
	c := 4.5
	fmt.Println(float64(a) / float64(b))
	fmt.Println(a / b)
	fmt.Println(float64(a) / c)
	fmt.Println(math.Floor(float64(a) / c))
	fmt.Println(a + b)
	fmt.Println(float64(a) + c)
}
```
#### Go
```go
def main():
    a = [1, 2, 3]
    print(a[0])
    print(a[1])
    print(a[2])
    a.append(4)
    print(a[3])
    a += [5, 6, 7]
    a = a + [8, 9, 10]
    print(a[4])
    print(a[-1])

if __name__ == '__main__':
    main()
```
### numlist
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	fmt.Println(a[0])
	fmt.Println(a[1])
	fmt.Println(a[2])
	a = append(a, 4)
	fmt.Println(a[3])
	a = append(a, []int{5, 6, 7}...)
	a = append(a, []int{8, 9, 10}...)
	fmt.Println(a[4])
	fmt.Println(a[len(a)-1])
}
```
#### Go
```go
def main():
    a = [1, 2, 3]
    for v in a:
        print(v)

    for i, v in enumerate(a):
        print(i + v)

    for i in range(5):
        print(i)

    for i in range(10, 15):
        print(i)

    for i in range(10, 15, 2):
        print(i)

    for j in range(15, 10, -1):
        print(j)

    for j in range(15, 10, -2):
        print(j)

if __name__ == '__main__':
    main()
```
### loops
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	for _, v := range a {
		fmt.Println(v)
	}
	for i, v := range a {
		fmt.Println(i + v)
	}
	for i := 0; i < 5; i++ {
		fmt.Println(i)
	}
	for i := 10; i < 15; i++ {
		fmt.Println(i)
	}
	for i := 10; i < 15; i += 2 {
		fmt.Println(i)
	}
	for j := 15; j > 10; j-- {
		fmt.Println(j)
	}
	for j := 15; j > 10; j -= 2 {
		fmt.Println(j)
	}
}
```
#### Go
```go
def main():
    a = "hello"
    b = "world"
    c = a + " " + b
    print(c)
    print(double_it(c))
    print(c[1])
    print(c[1:6])


def double_it(c: str) -> str:
    return c + c


if __name__ == '__main__':
    main()
```
### strings
#### Python
```python
package main

import "fmt"

func main() {
	a := "hello"
	b := "world"
	c := a + " " + b
	fmt.Println(c)
	fmt.Println(double_it(c))
	fmt.Println(string(c[1]))
	fmt.Println(c[1:6])
}

func double_it(c string) string {
	return c + c
}
```
#### Go
```go
def main():
    a = True
    b = False
    print(a)
    print(b)
    print(a and b)
    print(a or b)
    print(not a)
    print(not b)
    print(a and not b)
    print(a or not b)


if __name__ == '__main__':
    main()
```
### logical
#### Python
```python
package main

import "fmt"

func main() {
	a := true
	b := false
	fmt.Println(a)
	fmt.Println(b)
	fmt.Println(a && b)
	fmt.Println(a || b)
	fmt.Println(!a)
	fmt.Println(!b)
	fmt.Println(a && !b)
	fmt.Println(a || !b)
}
```
#### Go
```go
import math

def main():
    print(math.sin(3))
    print(math.cosh(3))
    print(math.pi)
    print(math.acosh(6))
    print(math.atan2(4, 7))

if __name__ == '__main__':
    main()
```
### maths
#### Python
```python
package main

import (
	"fmt"
	"math"
)

func main() {
	fmt.Println(math.Sin(3))
	fmt.Println(math.Cosh(3))
	fmt.Println(math.Pi)
	fmt.Println(math.Acosh(6))
	fmt.Println(math.Atan2(4, 7))
}
```
#### Go
```go
import requests


def main():
    resp = requests.get("http://tour.golang.org/welcome/1")
    print(resp.text)

if __name__ == '__main__':
    main()
```
### requestslib
#### Python
```python
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	resp, err := http.Get("http://tour.golang.org/welcome/1")
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	fmt.Println(func() string {
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			panic(err)
		}
		return string(body)
	}())
}
```
#### Go
```go
def main():
    a = 7
    b = add(a, -2)
    if a > b:
        print("It's bigger")
    elif a == b:
        print("They're equal")
    else:
        print("It's smaller")


def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    main()
```
### conditionals
#### Python
```python
package main

import "fmt"

func main() {
	a := 7
	b := add(a, -2)
	if a > b {
		fmt.Println("It's bigger")
	} else if a == b {
		fmt.Println("They're equal")
	} else {
		fmt.Println("It's smaller")
	}
}

func add(a int, b int) int {
	return a + b
}
```
#### Go
```go
def main():
    name = "Michael"
    age = 24
    print(f"My name is {name} and I am {age} years old. Later this year I'll be {age + 1}!")

if __name__ == '__main__':
    main()
```
### fstrings
#### Python
```python
package main

import (
	"bytes"
	"fmt"
	"text/template"
)

func main() {
	name := "Michael"
	age := 24
	fmt.Println(func() string {
		var buf bytes.Buffer
		err := template.Must(template.New("f").Parse("My name is {{.name}} and I am {{.age}} years old. Later this year I'll be {{.expr1}}!")).Execute(&buf, map[string]interface{}{"name": name, "age": age, "expr1": age + 1})
		if err != nil {
			panic(err)
		}
		return buf.String()
	}())
}
```
#### Go
```go
def main():
    name = "Michael"
    age = 24
    print(f"My name is {name} and I am {age} years old. Later this year I'll be {f'{age + 1}'}!")

if __name__ == '__main__':
    main()
```
### nestedfstrings
#### Python
```python
package main

import (
	"bytes"
	"fmt"
	"text/template"
)

func main() {
	name := "Michael"
	age := 24
	fmt.Println(func() string {
		var buf bytes.Buffer
		err := template.Must(template.New("f").Parse("My name is {{.name}} and I am {{.age}} years old. Later this year I'll be {{.expr1}}!")).Execute(&buf, map[string]interface{}{"name": name, "age": age, "expr1": func() string {
			var buf bytes.Buffer
			err := template.Must(template.New("f").Parse("{{.expr1}}")).Execute(&buf, map[string]interface{}{"expr1": age + 1})
			if err != nil {
				panic(err)
			}
			return buf.String()
		}()})
		if err != nil {
			panic(err)
		}
		return buf.String()
	}())
}
```
#### Go
```go
def main():
    a = {"name": "Michael", "age": 24, 1337: True}
    print(a)
    a["sleepiness"] = 1.0
    del a[1337]

    for k, v in a.items():
        print(k)
        print(v)

```
### dictionary
#### Python
```python
package main

import "fmt"

func main() {
	a := map[interface{}]interface{}{"name": "Michael", "age": 24, 1337: true}
	fmt.Println(a)
	a["sleepiness"] = 1.0
	delete(a, 1337)
	for k, v := range a {
		fmt.Println(k)
		fmt.Println(v)
	}
}
```
#### Go
```go
def main():
    with open("file_1.tmp", "w+") as f:
        f.write("This file was created in w+ mode\n")

    with open("file_2.tmp", "x") as f:
        f.write("This file was created by x mode\n")

    with open("file_2.tmp", "w") as f:
        f.write("This file was created by x mode and then overwritten in w mode\n")

    with open("file_2.tmp", "a") as f:
        f.write("... And then appended to in a mode\n")

    with open("file_2.tmp", "r") as f:
        print(f.read())

    with open("file_3.tmp", "a+") as f:
        f.write("This file was created in a+ mode\n")

    with open("file_4.tmp", "x+") as f:
        f.write("This file was created by x+ mode\n")

    with open("file_5.tmp", "wb+") as f:
        f.write(b"This file was created in wb+ mode\n")

    with open("file_6.tmp", "xb") as f:
        f.write(b"This file was created by xb mode\n")

    with open("file_6.tmp", "wb") as f:
        f.write(b"This file was created by xb mode and then overwritten in wb mode\n")

    with open("file_6.tmp", "ab") as f:
        f.write(b"... And then appended to in ab mode\n")

    with open("file_6.tmp", "rb") as f:
        print(f.read().decode())

    with open("file_7.tmp", "ab+") as f:
        f.write(b"This file was created in ab+ mode\n")

    with open("file_8.tmp", "xb+") as f:
        f.write(b"This file was created by xb+ mode\n")

    # with open("file_4.tmp", "x+") as f:
    #     pass

if __name__ == '__main__':
    main()
```
### writefile
#### Python
```python
package main

import (
	"fmt"
	"io/ioutil"
	"os"
)

func main() {
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_1.tmp", os.O_RDWR|os.O_TRUNC|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created in w+ mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_WRONLY|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created by x mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_WRONLY|os.O_TRUNC, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created by x mode and then overwritten in w mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("... And then appended to in a mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_2.tmp", os.O_RDONLY, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		fmt.Println(func() string {
			content, err := ioutil.ReadAll(f)
			if err != nil {
				panic(err)
			}
			return string(content)
		}())
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_3.tmp", os.O_RDWR|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created in a+ mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_4.tmp", os.O_RDWR|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.WriteString("This file was created by x+ mode\n")
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_5.tmp", os.O_RDWR|os.O_TRUNC|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created in wb+ mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_WRONLY|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created by xb mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_WRONLY|os.O_TRUNC, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created by xb mode and then overwritten in wb mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("... And then appended to in ab mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_6.tmp", os.O_RDONLY, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		fmt.Println(string(func() []byte {
			content, err := ioutil.ReadAll(f)
			if err != nil {
				panic(err)
			}
			return content
		}()))
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_7.tmp", os.O_RDWR|os.O_APPEND|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created in ab+ mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
	func() {
		f := func() *os.File {
			f, err := os.OpenFile("file_8.tmp", os.O_RDWR|os.O_EXCL|os.O_CREATE, 0o777)
			if err != nil {
				panic(err)
			}
			return f
		}()
		defer func() {
			if err := f.Close(); err != nil {
				panic(err)
			}
		}()
		func() int {
			n, err := f.Write([]byte("This file was created by xb+ mode\n"))
			if err != nil {
				panic(err)
			}
			return n
		}()
	}()
}
```
#### Go
```go
def main():
    pass

if __name__ == '__main__':
    main()
```
### pass
#### Python
```python
package main

func main() {
}
```
#### Go
```go
def main():
    ...

if __name__ == '__main__':
    main()
```
### ellipsis
#### Python
```python
package main

func main() {
}
```
#### Go
```go
def main():
    print(add(1, 3))


def add(a: int, b: int):
    return a + b
```
### missingreturntype
#### Python
```python
package main

import "fmt"

func main() {
	fmt.Println(add(1, 3))
}

func add(a int, b int) int {
	return a + b
}
```
#### Go
```go
def main():
    for i in range(10):
        if i < 3 or i > 7:
            continue
        print(i)

if __name__ == '__main__':
    main()
```
### continuestmt
#### Python
```python
package main

import "fmt"

func main() {
	for i := 0; i < 10; i++ {
		if i < 3 || i > 7 {
			continue
		}
		fmt.Println(i)
	}
}
```
#### Go
```go
def main():
    for i in range(10):
        if i > 7:
            break
        print(i)

if __name__ == '__main__':
    main()
```
### breakstmt
#### Python
```python
package main

import "fmt"

func main() {
	for i := 0; i < 10; i++ {
		if i > 7 {
			break
		}
		fmt.Println(i)
	}
}
```
#### Go
```go
def main():
    i = 0
    while True:
        print(i)
        i += 1
        if i > 5:
            break

    j = 10
    while j < 100:
        print(j)
        j += 10

    while 1:
        print(j + i)
        break

    while 0.1:
        print(j + i)
        break

    while 0:
        print("This never executes")

    while 0.0:
        print("This never executes")

    while None:
        print("This never executes")

    while False:
        print("This never executes")

    while "":
        print("This never executes")

    while "hi":
        print("This executes")
        break

if __name__ == '__main__':
    main()
```
### whileloop
#### Python
```python
package main

import "fmt"

func main() {
	i := 0
	for {
		fmt.Println(i)
		i += 1
		if i > 5 {
			break
		}
	}
	j := 10
	for j < 100 {
		fmt.Println(j)
		j += 10
	}
	for {
		fmt.Println(j + i)
		break
	}
	for {
		fmt.Println(j + i)
		break
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for false {
		fmt.Println("This never executes")
	}
	for {
		fmt.Println("This executes")
		break
	}
}
```
#### Go
```go
def main():
    s = {1, 2, 3}
    # other = {3, 4}
    # another = {5, 6, 7}
    x = 1

    # len(s)
    print(len(s))

    # x in s
    print(x in s)

    # x not in s
    print(x not in s)

    # TODO:
    # # isdisjoint(other)
    # print(s.isdisjoint(other))
    #
    # # issubset(other)
    # # set <= other
    # # Test whether every element in the set is in other.
    # print(s.issubset(other))
    # print(s <= other)
    #
    # # set < other
    # # Test whether the set is a proper subset of other, that is, set <= other and set != other.
    # print(s < other)
    #
    # # issuperset(other)
    # # Test whether every element in other is in the set.
    # print(s >= other)
    #
    # # set > other
    # # Test whether the set is a proper superset of other, that is, set >= other and set != other.
    # print(s > other)
    #
    # # union(*others)
    # # set | other | ...
    # print(s.union(other))
    # print(s.union(other, another))
    # print(s | other)
    # print(s | other | another)
    #
    # # intersection(*others)
    # # set & other & ...
    # print(s.intersection(other))
    # print(s.intersection(other, another))
    # print(s & other)
    # print(s & other & another)
    #
    # # difference(*others)
    # # set - other - ...
    # # Return a new set with elements in the set that are not in the others.
    # print(s.difference(other))
    # print(s.difference(other, another))
    # print(s - other)
    # print(s - other - another)
    #
    # # symmetric_difference(other)
    # # set ^ other
    # # Return a new set with elements in either the set or other but not both.
    # print(s.symmetric_difference(other))
    # print(s ^ other)
    #
    # # copy()
    # # Return a shallow copy of the set.
    # print(s.copy())
    #
    # # The following table lists operations available for set that do not apply to
    # # immutable instances of frozenset:
    #
    # # update(*others)
    # # set |= other | ...
    # # Update the set, adding elements from all others.
    # s.update(other)
    # print(s)
    # s.update(other, another)
    # print(s)
    # another |= other
    # print(another)
    # another |= other | s
    # print(another)
    #
    #
    # # intersection_update(*others)
    # # set &= other & ...
    # # Update the set, keeping only elements found in it and all others.
    # s.intersection_update(other)
    # print(s)
    # s.intersection_update(other, another)
    # print(s)
    # another &= other
    # print(another)
    # another &= other & s
    # print(another)
    #
    # # difference_update(*others)
    # # set -= other | ...
    # # Update the set, removing elements found in others.
    # s.difference_update(other)
    # print(s)
    # s.difference_update(other, another)
    # print(s)
    # another -= other
    # print(another)
    # another -= other | s
    # print(another)
    #
    # # symmetric_difference_update(other)
    # # set ^= other
    # # Update the set, keeping only elements found in either set, but not in both.
    # s.symmetric_difference_update(other)
    # print(s)
    # another ^= other
    # print(another)
    #
    # # add(elem)
    # # Add element elem to the set.
    # s.add(x)
    # print(s)
    #
    # # remove(elem)
    # # Remove element elem from the set. Raises KeyError if elem is not contained in the set.
    # s.remove(x)
    # print(s)
    #
    # # discard(elem)
    # # Remove element elem from the set if it is present.
    # s.discard(x)
    # print(s)
    #
    # # pop()
    # # Remove and return an arbitrary element from the set. Raises KeyError if the set is empty.
    # print(s.pop())
    #
    # # clear()
    # # Remove all elements from the set.
    # s.clear()
    # print(s)


if __name__ == '__main__':
    main()
```
### sets
#### Python
```python
package main

import "fmt"

func main() {
	s := map[int]struct{}{1: {}, 2: {}, 3: {}}
	x := 1
	fmt.Println(len(s))
	fmt.Println(func() bool {
		_, ok := s[x]
		return ok
	}())
	fmt.Println(!func() bool {
		_, ok := s[x]
		return ok
	}())
}
```
#### Go
```go
def main():
    # Iterables should compare the index of the element to -1
    a = [1, 2, 3]
    print(1 in a)
    print(4 in a)
    print(5 not in a)

    # Strings should either use strings.Compare or use strings.Index with a comparison to -1
    # While the former is more straight forward, I think the latter will be nicer for consistency
    b = "hello world"
    print("hello" in b)
    print("Hello" not in b)

    # Checking for membership in a dictionary means we need to check if the key is in it
    # ... Eventually this should behave well with mixed types
    c = {"hello": 1, "world": 2}
    print("hello" in c)
    print("Hello" not in c)

    # Bytes
    d = b'hello world'
    print(b'hello' in d)
    print(b'Hello' not in d)

    # Sets
    e = {1, 2, 3, "hello"}
    print("hello" in e)
    print(4 not in e)

if __name__ == '__main__':
    main()
```
### contains
#### Python
```python
package main

import (
	"bytes"
	"fmt"
	"strings"
)

func main() {
	a := []int{1, 2, 3}
	fmt.Println(func() int {
		for i, v := range a {
			if v == 1 {
				return i
			}
		}
		return -1
	}() != -1)
	fmt.Println(func() int {
		for i, v := range a {
			if v == 4 {
				return i
			}
		}
		return -1
	}() != -1)
	fmt.Println(func() int {
		for i, v := range a {
			if v == 5 {
				return i
			}
		}
		return -1
	}() == -1)
	b := "hello world"
	fmt.Println(strings.Contains(b, "hello"))
	fmt.Println(!strings.Contains(b, "Hello"))
	c := map[string]int{"hello": 1, "world": 2}
	fmt.Println(func() bool {
		_, ok := c["hello"]
		return ok
	}())
	fmt.Println(!func() bool {
		_, ok := c["Hello"]
		return ok
	}())
	d := []byte("hello world")
	fmt.Println(bytes.Contains(d, []byte("hello")))
	fmt.Println(!bytes.Contains(d, []byte("Hello")))
	e := map[interface{}]struct{}{1: {}, 2: {}, 3: {}, "hello": {}}
	fmt.Println(func() bool {
		_, ok := e["hello"]
		return ok
	}())
	fmt.Println(!func() bool {
		_, ok := e[4]
		return ok
	}())
}
```
#### Go
```go
def main():
    a = [1, 2, 3]
    for index in range(4):
        try:
            print(a[index])
            if index == 1:
                raise ValueError(index)
        except IndexError:
            print("That index was out of bounds")
        except (NotImplementedError, RuntimeError):
            print("This won't actually happen...")
        except Exception as e:
            print("Some other exception occurred")
            print(e)


if __name__ == '__main__':
    main()

```
### tryexcept
#### Python
```python
package main

import (
	"fmt"
	"strings"
)

func main() {
	a := []int{1, 2, 3}
	for index := 0; index < 4; index++ {
		func() {
			defer func() {
				if r := recover(); r != nil {
					if err, ok := r.(error); ok {
						if strings.HasPrefix(err.Error(), "IndexError") || strings.HasPrefix(err.Error(), "runtime error: index out of range") {
							fmt.Println("That index was out of bounds")
							return
						} else if strings.HasPrefix(err.Error(), "NotImplementedError") || (strings.HasPrefix(err.Error(), "RuntimeError") || strings.HasPrefix(err.Error(), "runtime error")) {
							fmt.Println("This won't actually happen...")
							return
						} else {
							e := err
							fmt.Println("Some other exception occurred")
							fmt.Println(e)
							return
						}
					}
					panic(r)
				}
			}()
			fmt.Println(a[index])
			if index == 1 {
				panic(fmt.Errorf("ValueError: %v", index))
			}
		}()
	}
}
```
#### Go
```go
def main():
    a = [1, 2, 3]

    for index in range(4):
        try:
            print(a[index])
        except Exception:
            pass
        finally:
            print("Finished an iteration")

    for index in range(4):
        try:
            print(a[index])
        finally:
            print("Finished an iteration")


if __name__ == '__main__':
    main()
```
### tryfinally
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	for index := 0; index < 4; index++ {
		func() {
			defer func() {
				fmt.Println("Finished an iteration")
			}()
			defer func() {
				if r := recover(); r != nil {
					if _, ok := r.(error); ok {
						return
					}
					panic(r)
				}
			}()
			fmt.Println(a[index])
		}()
	}
	for index := 0; index < 4; index++ {
		func() {
			defer func() {
				fmt.Println("Finished an iteration")
			}()
			fmt.Println(a[index])
		}()
	}
}
```
#### Go
```go
def main():
    assert 1 + 1 == 2
    assert True
    assert 1 + 3 == 5, "Math must be broken"


if __name__ == '__main__':
    main()
```
### asserts
#### Python
```python
package main

import (
	"errors"
	"fmt"
)

func main() {
	if !(1+1 == 2) {
		panic(errors.New("AssertionError"))
	}
	if !true {
		panic(errors.New("AssertionError"))
	}
	if !(1+3 == 5) {
		panic(fmt.Errorf("AssertionError: %v", "Math must be broken"))
	}
}
```
#### Go
```go
class Welcome:
    greeting: str
    instructions: list[str]

    def __init__(self, greeting: str, instructions: list[str]) -> None:
        self.greeting = greeting
        self.instructions = instructions

    def greet(self):
        print(self.greeting)
        for instruction in self.instructions:
            print(instruction)


def main():
    welcome = Welcome("Hello World", [
        "This is a class!",
        "Support will be limited at first.",
        "Still, I hope you'll find them useful."
    ])
    welcome.greet()


if __name__ == '__main__':
    main()
```
### classes
#### Python
```python
package main

import "fmt"

type Welcome struct {
	greeting     string
	instructions []string
}

func NewWelcome(greeting string, instructions []string) (self *Welcome) {
	self = new(Welcome)
	self.greeting = greeting
	self.instructions = instructions
	return
}

func (self *Welcome) greet() {
	fmt.Println(self.greeting)
	for _, instruction := range self.instructions {
		fmt.Println(instruction)
	}
}

func main() {
	welcome := NewWelcome("Hello World", []string{"This is a class!", "Support will be limited at first.", "Still, I hope you'll find them useful."})
	welcome.greet()
}
```
#### Go
```go
SITE = "https://www.google.com/"
NAME = ["Michael", "Wayne", "Phelps"]
KEYS = {1: 2, 3: 4}
AGE = 1000
BIRTH_YEAR = 2050


def main():
    global AGE
    print(SITE)
    print(NAME)
    print(BIRTH_YEAR)
    print(KEYS)
    print(AGE)
    AGE = 20  # This should use the variable from the global scope
    other_1()
    print(AGE)
    other_2()


def other_1():
    AGE = 200  # This should declare a new variable age
    print(AGE)

def other_2():
    print(AGE)  # This should still be able to access the global


if __name__ == '__main__':
    main()
```
### globals
#### Python
```python
package main

import "fmt"

var (
	SITE       = "https://www.google.com/"
	NAME       = []string{"Michael", "Wayne", "Phelps"}
	KEYS       = map[int]int{1: 2, 3: 4}
	AGE        = 1000
	BIRTH_YEAR = 2050
)

func main() {
	fmt.Println(SITE)
	fmt.Println(NAME)
	fmt.Println(BIRTH_YEAR)
	fmt.Println(KEYS)
	fmt.Println(AGE)
	AGE = 20
	other_1()
	fmt.Println(AGE)
	other_2()
}

func other_1() {
	AGE := 200
	fmt.Println(AGE)
}

func other_2() {
	fmt.Println(AGE)
}
```
#### Go
```go
import asyncio


async def myAsyncFunction() -> int:
    await asyncio.sleep(2)
    return 2


async def main():
    r = await myAsyncFunction()
    print(r)


if __name__ == '__main__':
    asyncio.run(main())
```
### asyncawait
#### Python
```python
package main

import (
	"fmt"
	"time"
)

func myAsyncFunction() <-chan int {
	r := make(chan int)
	go func() {
		defer close(r)
		time.Sleep(time.Second * 2)
		r <- 2
	}()
	return r
}

func main() {
	r := <-myAsyncFunction()
	fmt.Println(r)
}
```
#### Go
```go
def main():
    my_gen = gen()
    for x in my_gen:
        print("Received next number!")
        print(x)


def gen():
    print("Yielding next number...")
    yield 1
    print("Yielding next number...")
    yield 2
    print("Yielding next number...")
    yield 3


if __name__ == '__main__':
    main()
```
### yields
#### Python
```python
package main

import "fmt"

func main() {
	my_gen := gen()
	for x, ok := <-my_gen(); ok; x, ok = <-my_gen() {
		fmt.Println("Received next number!")
		fmt.Println(x)
	}
}

func gen() func() <-chan int {
	wait := make(chan struct{})
	yield := make(chan int)
	go func() {
		defer close(yield)
		<-wait
		fmt.Println("Yielding next number...")
		yield <- 1
		<-wait
		fmt.Println("Yielding next number...")
		yield <- 2
		<-wait
		fmt.Println("Yielding next number...")
		yield <- 3
		<-wait
	}()
	return func() <-chan int {
		wait <- struct{}{}
		return yield
	}
}
```
#### Go
```go
def main():
    a = [1, 2, 3]
    b = [1, 2, 3]
    print(a == b)  # True
    print(a != b)  # False
    print(a is a)  # True
    print(a is b)  # False
    print(a is not a)  # False
    print(a is not b)  # True

if __name__ == '__main__':
    main()
```
### isvseql
#### Python
```python
package main

import (
	"fmt"
	"reflect"
)

func main() {
	a := []int{1, 2, 3}
	b := []int{1, 2, 3}
	fmt.Println(reflect.DeepEqual(a, b))
	fmt.Println(!reflect.DeepEqual(a, b))
	fmt.Println(&a == &a)
	fmt.Println(&a == &b)
	fmt.Println(&a != &a)
	fmt.Println(&a != &b)
}
```
#### Go
```go
def main():
    a = 1
    match a:
        case 1:
            print(1)
        case 2:
            print(2)
        case 3:
            print(3)

    match a:
        case 4:
            print("Never gonna happen")
        case _:
            print("Nice, defaults!")


if __name__ == '__main__':
    main()
```
### matchcase
#### Python
```python
package main

import "fmt"

func main() {
	a := 1
	switch a {
	case 1:
		fmt.Println(1)
	case 2:
		fmt.Println(2)
	case 3:
		fmt.Println(3)
	}
	switch a {
	case 4:
		fmt.Println("Never gonna happen")
	default:
		fmt.Println("Nice, defaults!")
	}
}
```
#### Go
```go
def main():
    a = increment(1)
    print(a)
    b = increment(a, 2)
    print(b)
    c = increment(a, decrement=True, amount=3)
    print(c)


def increment(n: int, amount: int = 1, decrement: bool = False) -> int:
    if decrement:
        return n - amount
    return n + amount


if __name__ == '__main__':
    main()
```
### defaultargs
#### Python
```python
package main

import "fmt"

func main() {
	a := increment(1, 1, false)
	fmt.Println(a)
	b := increment(a, 2, false)
	fmt.Println(b)
	c := increment(a, 3, true)
	fmt.Println(c)
}

func increment(n int, amount int, decrement bool) int {
	if decrement {
		return n - amount
	}
	return n + amount
}
```
#### Go
```go
def main():
    if (a := some_func()) == 7:
        print(a)

    for x in (y := [1, 2, 3]):
        print(y)
        print(x)

    match j := 5:
        case 5:
            print(j)

    while (t1 := thing_1()) < 5 and (t2 := thing_2()) == 3:
        print(t1)
        print(t2)


def some_func():
    return 7


call_count = 0


def thing_1():
    global call_count
    call_count += 1
    return call_count


def thing_2():
    return 3


if __name__ == '__main__':
    main()
```
### walrus
#### Python
```python
package main

import "fmt"

func main() {
	if a := some_func(); a == 7 {
		fmt.Println(a)
	}
	y := []int{1, 2, 3}
	for _, x := range y {
		fmt.Println(y)
		fmt.Println(x)
	}
	switch j := 5; j {
	case 5:
		fmt.Println(j)
	}
	for t1, t2 := thing_1(), thing_2(); t1 < 5 && t2 == 3; t1, t2 = thing_1(), thing_2() {
		fmt.Println(t1)
		fmt.Println(t2)
	}
}

func some_func() int {
	return 7
}

var call_count = 0

func thing_1() int {
	call_count += 1
	return call_count
}

func thing_2() int {
	return 3
}
```
#### Go
```go
def main():
    if a := 1:
        print(a)

    if c := "":
        print(c)

    if d := b"":
        print(d)

    if e := "Hello":
        print(e)

    if f := b"Goodbye":
        print(f)

    if g := 1.0:
        print(g)

    if h := 1j:
        print(h)

    if i := 0.0:
        print(i)

    if j := 0j:
        print(j)

    if k := []:
        print(k)

    if l := [1, 2, 3]:
        print(l)

    if m := True:
        print(m)

    if n := False:
        print(n)

    if o := ():
        print(o)

    if p := (1, 2, 3):
        print(p)

    if q := set():
        print(q)

    if r := {1, 2, 3}:
        print(r)

    if s := {}:
        print(s)

    if t := {1: 2}:
        print(t)



if __name__ == '__main__':
    main()
```
### truthiness
#### Python
```python
package main

import "fmt"

func main() {
	if a := 1; a != 0 {
		fmt.Println(a)
	}
	if c := ""; len(c) != 0 {
		fmt.Println(c)
	}
	if d := []byte(""); len(d) != 0 {
		fmt.Println(d)
	}
	if e := "Hello"; len(e) != 0 {
		fmt.Println(e)
	}
	if f := []byte("Goodbye"); len(f) != 0 {
		fmt.Println(f)
	}
	if g := 1.0; g != 0 {
		fmt.Println(g)
	}
	if h := 1.0i; h != 0 {
		fmt.Println(h)
	}
	if i := 0.0; i != 0 {
		fmt.Println(i)
	}
	if j := 0.0i; j != 0 {
		fmt.Println(j)
	}
	if k := []interface{}{}; len(k) != 0 {
		fmt.Println(k)
	}
	if l := []int{1, 2, 3}; len(l) != 0 {
		fmt.Println(l)
	}
	if m := true; m {
		fmt.Println(m)
	}
	if n := false; n {
		fmt.Println(n)
	}
	if o := [0]interface{}{}; len(o) != 0 {
		fmt.Println(o)
	}
	if p := [3]int{1, 2, 3}; len(p) != 0 {
		fmt.Println(p)
	}
	if q := map[interface{}]struct{}{}; len(q) != 0 {
		fmt.Println(q)
	}
	if r := map[int]struct{}{1: {}, 2: {}, 3: {}}; len(r) != 0 {
		fmt.Println(r)
	}
	if s := map[interface{}]interface{}{}; len(s) != 0 {
		fmt.Println(s)
	}
	if t := map[int]int{1: 2}; len(t) != 0 {
		fmt.Println(t)
	}
}
```
#### Go
```go
def main():
    print(max([1, 2, 3]))
    print(min([1, 2, 3]))
    print(max("a", "b", "c"))
    print(min("a", "b", "c"))

if __name__ == '__main__':
    main()
```
### minmax
#### Python
```python
package main

import "fmt"

func main() {
	fmt.Println(func() (m int) {
		for i, e := range []int{1, 2, 3} {
			if i == 0 || e > m {
				m = e
			}
		}
		return
	}())
	fmt.Println(func() (m int) {
		for i, e := range []int{1, 2, 3} {
			if i == 0 || e < m {
				m = e
			}
		}
		return
	}())
	fmt.Println(func() (m string) {
		for i, e := range []string{"a", "b", "c"} {
			if i == 0 || e > m {
				m = e
			}
		}
		return
	}())
	fmt.Println(func() (m string) {
		for i, e := range []string{"a", "b", "c"} {
			if i == 0 || e < m {
				m = e
			}
		}
		return
	}())
}
```
#### Go
```go
def main():
    print(sum([1, 2, 3]))
    print(sum([1.5, 2.6, 3.7]))
    print(sum([1j, 2j, 3j]))

if __name__ == '__main__':
    main()
```
### sum
#### Python
```python
package main

import "fmt"

func main() {
	fmt.Println(func() (s int) {
		for _, e := range []int{1, 2, 3} {
			s += e
		}
		return
	}())
	fmt.Println(func() (s float64) {
		for _, e := range []float64{1.5, 2.6, 3.7} {
			s += e
		}
		return
	}())
	fmt.Println(func() (s complex128) {
		for _, e := range []complex128{1.0i, 2.0i, 3.0i} {
			s += e
		}
		return
	}())
}
```
#### Go
```go
def main():
    a = [1, 2, 3, 4, 5]

    # Even though this is technically an iterator I'm going to let
    # go just copy it for the initial implementation since that's
    # probably what you'd do in go (or just reverse in-place -- .reverse() for that)
    for x in reversed(a):
        print(x)

    for x in a:
        print(x)

    a.reverse()

    for x in a:
        print(x)


if __name__ == '__main__':
    main()
```
### reverse
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{1, 2, 3, 4, 5}
	for _, x := range func(arr []int) []int {
		arr2 := make([]int, len(arr))
		for i, e := range arr {
			arr2[len(arr)-i-1] = e
		}
		return arr2
	}(a) {
		fmt.Println(x)
	}
	for _, x := range a {
		fmt.Println(x)
	}
	func(arr []int) {
		for i, j := 0, len(arr)-1; i < j; i, j = i+1, j-1 {
			arr[i], arr[j] = arr[j], arr[i]
		}
	}(a)
	for _, x := range a {
		fmt.Println(x)
	}
}
```
#### Go
```go
def main():
    a = [x for x in range(10)]
    b = [x for x in range(10) if x % 2 == 0]
    c = [x if x % 2 == 0 else 777 for x in range(10)]
    d = [x for i, x in enumerate(c) if i % 2 == 0 if i % 3 == 1]
    e = [(x, y) for x in c for y in d]
    f = [(x, y) for x in c for y in next_five_numbers_times_two(x)]
    g = [(i, j) for i in range(10) for j in range(i)]

    print(a)
    print(b)
    print(c)
    print(d)
    print(e)
    print(f)
    print(g)


def next_five_numbers_times_two(a: int) -> list[int]:
    return [(a + i) * 2 for i in range(1, 6)]


if __name__ == '__main__':
    main()
```
### listcomp
#### Python
```python
package main

import "fmt"

func main() {
	a := func() (elts []int) {
		for x := 0; x < 10; x++ {
			elts = append(elts, x)
		}
		return
	}()
	b := func() (elts []int) {
		for x := 0; x < 10; x++ {
			if x%2 == 0 {
				elts = append(elts, x)
			}
		}
		return
	}()
	c := func() (elts []int) {
		for x := 0; x < 10; x++ {
			elts = append(elts, func() int {
				if x%2 == 0 {
					return x
				}
				return 777
			}())
		}
		return
	}()
	d := func() (elts []int) {
		for i, x := range c {
			if i%2 == 0 {
				if i%3 == 1 {
					elts = append(elts, x)
				}
			}
		}
		return
	}()
	e := func() (elts [][2]int) {
		for _, x := range c {
			for _, y := range d {
				elts = append(elts, [2]int{x, y})
			}
		}
		return
	}()
	f := func() (elts [][2]int) {
		for _, x := range c {
			for _, y := range next_five_numbers_times_two(x) {
				elts = append(elts, [2]int{x, y})
			}
		}
		return
	}()
	g := func() (elts [][2]int) {
		for i := 0; i < 10; i++ {
			for j := 0; j < i; j++ {
				elts = append(elts, [2]int{i, j})
			}
		}
		return
	}()
	fmt.Println(a)
	fmt.Println(b)
	fmt.Println(c)
	fmt.Println(d)
	fmt.Println(e)
	fmt.Println(f)
	fmt.Println(g)
}

func next_five_numbers_times_two(a int) []int {
	return func() (elts []int) {
		for i := 1; i < 6; i++ {
			elts = append(elts, (a+i)*2)
		}
		return
	}()
}
```
#### Go
```go
def main():
    a = {(x, y): x*y for x in range(20) for y in range(5) if x*y != 0}
    for k, v in a.items():
        print(k, v)


if __name__ == '__main__':
    main()
```
### dictcomp
#### Python
```python
package main

import "fmt"

func main() {
	a := func() (d map[[2]int]int) {
		d = make(map[[2]int]int)
		for x := 0; x < 20; x++ {
			for y := 0; y < 5; y++ {
				if x*y != 0 {
					d[[2]int{x, y}] = x * y
				}
			}
		}
		return
	}()
	for k, v := range a {
		fmt.Println(k, v)
	}
}
```
#### Go
```go
def main():
    a = {x for x in range(20, 39)}
    b = {(x, y) for x in range(100) for y in range(x, x + 5) if x % 39 in a}
    print(a)
    print(b)


if __name__ == '__main__':
    main()
```
### setcomp
#### Python
```python
package main

import "fmt"

func main() {
	a := func() (s map[int]struct{}) {
		s = make(map[int]struct{})
		for x := 20; x < 39; x++ {
			s[x] = struct{}{}
		}
		return
	}()
	b := func() (s map[[2]int]struct{}) {
		s = make(map[[2]int]struct{})
		for x := 0; x < 100; x++ {
			for y := x; y < x+5; y++ {
				if func() bool {
					_, ok := a[x%39]
					return ok
				}() {
					s[[2]int{x, y}] = struct{}{}
				}
			}
		}
		return
	}()
	fmt.Println(a)
	fmt.Println(b)
}
```
#### Go
```go
def main():
    a = ((x, y) for x in range(5) for y in range(x))
    b = (w for w in ("Where", "Are", "You?", "And", "I'm", "So", "Sorry"))
    for l in b:
        print(l, next(a))
    for rest in a:
        print(rest)


if __name__ == '__main__':
    main()
```
### generatorexp
#### Python
```python
package main

import "fmt"

func main() {
	a := func() func() <-chan [2]int {
		wait := make(chan struct{})
		yield := make(chan [2]int)
		go func() {
			defer close(yield)
			<-wait
			for x := 0; x < 5; x++ {
				for y := 0; y < x; y++ {
					yield <- [2]int{x, y}
					<-wait
				}
			}
		}()
		return func() <-chan [2]int {
			wait <- struct{}{}
			return yield
		}
	}()
	b := func() func() <-chan string {
		wait := make(chan struct{})
		yield := make(chan string)
		go func() {
			defer close(yield)
			<-wait
			for _, w := range [7]string{"Where", "Are", "You?", "And", "I'm", "So", "Sorry"} {
				yield <- w
				<-wait
			}
		}()
		return func() <-chan string {
			wait <- struct{}{}
			return yield
		}
	}()
	for l, ok := <-b(); ok; l, ok = <-b() {
		fmt.Println(l, <-a())
	}
	for rest, ok := <-a(); ok; rest, ok = <-a() {
		fmt.Println(rest)
	}
}
```
#### Go
```go
def main():
    a = 1 if True else 2
    print(a)


if __name__ == '__main__':
    main()
```
### ternary
#### Python
```python
package main

import "fmt"

func main() {
	a := func() int {
		if true {
			return 1
		}
		return 2
	}()
	fmt.Println(a)
}
```
#### Go
```go
def main():
    a = ["a", 1, "5", 2.3, 1.2j]
    some_condition = True
    for x in a:
        # If it's all isinstance, we can use a type switch
        if isinstance(x, (str, float)):
            print("String or float!")
        elif isinstance(x, int):
            print("Integer!")
        else:
            print("Dunno!")
            print(":)")

        # If it's got mixed expressions, we will inline a switch for the isinstance expression
        if isinstance(x, str) and some_condition:
            print("String")
        elif isinstance(x, int):
            print("Integer!")
        else:
            print("Dunno!!")
            print(":O")


if __name__ == '__main__':
    main()
```
### isinstance
#### Python
```python
package main

import "fmt"

func main() {
	a := []interface{}{"a", 1, "5", 2.3, 1.2i}
	some_condition := true
	for _, x := range a {
		switch x.(type) {
		case string, float64:
			fmt.Println("String or float!")
		case int:
			fmt.Println("Integer!")
		default:
			fmt.Println("Dunno!")
			fmt.Println(":)")
		}
		if func() bool {
			switch x.(type) {
			case string:
				return true
			}
			return false
		}() && some_condition {
			fmt.Println("String")
		} else {
			switch x.(type) {
			case int:
				fmt.Println("Integer!")
			default:
				fmt.Println("Dunno!!")
				fmt.Println(":O")
			}
		}
	}
}
```
#### Go
```go
def main():
    x = [1, 2, 3]
    y = [4, 5, 6]
    zipped = zip(x, y)
    for pair in zipped:
        print(pair)

if __name__ == '__main__':
    main()
```
### zip
#### Python
```python
package main

import "fmt"

func main() {
	x := []int{1, 2, 3}
	y := []int{4, 5, 6}
	zipped := func() func() <-chan [2]int {
		wait := make(chan struct{})
		yield := make(chan [2]int)
		go func() {
			defer close(yield)
			<-wait
			for i, e := range x {
				if i >= len(y) {
					break
				}
				yield <- [2]int{e, y[i]}
				<-wait
			}
		}()
		return func() <-chan [2]int {
			wait <- struct{}{}
			return yield
		}
	}()
	for pair, ok := <-zipped(); ok; pair, ok = <-zipped() {
		fmt.Println(pair)
	}
}
```
#### Go
```go
def main():
    a = [1, 2, 3]
    b = map(increment, a)
    for value in b:
        print(value)


def increment(n: int) -> int:
    return n + 1


if __name__ == '__main__':
    main()
```
### map
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{1, 2, 3}
	b := func() func() <-chan int {
		wait := make(chan struct{})
		yield := make(chan int)
		go func() {
			defer close(yield)
			<-wait
			for _, x := range a {
				yield <- increment(x)
				<-wait
			}
		}()
		return func() <-chan int {
			wait <- struct{}{}
			return yield
		}
	}()
	for value, ok := <-b(); ok; value, ok = <-b() {
		fmt.Println(value)
	}
}

func increment(n int) int {
	return n + 1
}
```
#### Go
```go
def main():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    s = repr(nums)
    print(s + s)


if __name__ == '__main__':
    main()
```
### repr
#### Python
```python
package main

import "fmt"

func main() {
	nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9}
	s := fmt.Sprintf("%#v", nums)
	fmt.Println(s + s)
}
```
#### Go
```go
def main():
    f = lambda x: x * 2
    for a in range(10):
        print((lambda x: x + 1)(a) + f(a))

if __name__ == '__main__':
    main()
```
### lambdafunc
#### Python
```python
package main

import "fmt"

func main() {
	f := func(x int) int {
		return int(x) * 2
	}
	for a := 0; a < 10; a++ {
		fmt.Println(func(x int) int {
			return int(x) + 1
		}(a) + f(a))
	}
}
```
#### Go
```go
import time

def main():
    print("Hello")
    time.sleep(3)
    print("... time!")


if __name__ == '__main__':
    main()
```
### timemodule
#### Python
```python
package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Hello")
	time.Sleep(3 * time.Second)
	fmt.Println("... time!")
}
```
#### Go
```go
import sys


def main():
    quit()
    quit(1)
    exit()
    exit(1)
    sys.exit()
    sys.exit(1)


if __name__ == '__main__':
    main()
```
### exit
#### Python
```python
package main

import "os"

func main() {
	os.Exit(0)
	os.Exit(1)
	os.Exit(0)
	os.Exit(1)
	os.Exit(0)
	os.Exit(1)
}
```
#### Go
```go
def main():
    a = []
    a.append(3)

    b = []
    b += a

    c = {}
    c["hello"] = 1

    d = {}
    d[1] = 2
    d["gonna_be_an_interface"] = "yup"

    e = set()
    e.add(1)

    f = [[]]
    f[0].append(1)

    g = {}
    g[(1, 2)] = 3

    h = []
    h.append(1)
    h.append("hi")

    i = {}
    i[1] = "lol"
    i["2"] = "lmao"

    print(a, b, c, d, e, f, g, h)


if __name__ == '__main__':
    main()
```
### retroactive_composite_types
#### Python
```python
package main

import "fmt"

func main() {
	a := []int{}
	a = append(a, 3)
	b := []int{}
	b = append(b, a...)
	c := map[string]int{}
	c["hello"] = 1
	d := map[interface{}]interface{}{}
	d[1] = 2
	d["gonna_be_an_interface"] = "yup"
	e := map[int]struct{}{}
	e[1] = struct{}{}
	f := [][]int{{}}
	f[0] = append(f[0], 1)
	g := map[[2]int]int{}
	g[[2]int{1, 2}] = 3
	h := []interface{}{}
	h = append(h, 1)
	h = append(h, "hi")
	i := map[interface{}]string{}
	i[1] = "lol"
	i["2"] = "lmao"
	fmt.Println(a, b, c, d, e, f, g, h)
}
```
#### Go
```go
def main():
    stuff = [1, 5, "hello", 5, 12, 19, 12.5, [1, 2, 3]]
    write_contents(stuff)
    items = ["", 0, 1.1]
    for x in items:
        if isinstance(x, str):
            print("See? It's not used here so we don't have a type assertion")
        elif isinstance(x, int):
            print("This is very important because go's compiler will complain")
        else:
            print("You know, I wouldn't have to worry about this if we had something to remove unused initializations")

def write_contents(contents):
    with open("contents.txt", "w+") as f:
        for item in contents:
            if isinstance(item, str):
                f.write("str: " + item + "\n")
            elif isinstance(item, int):
                f.write("int: " + str(item) + "\n")
            else:
                f.write("unknown: " + repr(item) + "\n")


if __name__ == '__main__':
    main()
```
### isinstance_gives_type_assertion
#### Python
```python
package main

import (
	"fmt"
	"os"
)

func main() {
	stuff := []interface{}{1, 5, "hello", 5, 12, 19, 12.5, []int{1, 2, 3}}
	write_contents(stuff)
	items := []interface{}{"", 0, 1.1}
	for _, x := range items {
		switch x.(type) {
		case string:
			fmt.Println("See? It's not used here so we don't have a type assertion")
		case int:
			fmt.Println("This is very important because go's compiler will complain")
		default:
			fmt.Println("You know, I wouldn't have to worry about this if we had something to remove unused initializations")
		}
	}
}

func write_contents(contents []interface{}) {
	f := func() *os.File {
		f, err := os.OpenFile("contents.txt", os.O_RDWR|os.O_TRUNC|os.O_CREATE, 0o777)
		if err != nil {
			panic(err)
		}
		return f
	}()
	defer func() {
		if err := f.Close(); err != nil {
			panic(err)
		}
	}()
	for _, item := range contents {
		switch item := item.(type) {
		case string:
			func() int {
				n, err := f.WriteString("str: " + item + "\n")
				if err != nil {
					panic(err)
				}
				return n
			}()
		case int:
			func() int {
				n, err := f.WriteString("int: " + fmt.Sprintf("%v", item) + "\n")
				if err != nil {
					panic(err)
				}
				return n
			}()
		default:
			func() int {
				n, err := f.WriteString("unknown: " + fmt.Sprintf("%#v", item) + "\n")
				if err != nil {
					panic(err)
				}
				return n
			}()
		}
	}
}
```
#### Go
```go
def majorityElement(nums: list[int]) -> int:
    element, cnt = 0, 0

    for e in nums:
        if element == e:
            cnt += 1
        elif cnt == 0:
            element, cnt = e, 1
        else:
            cnt -= 1

    return element

def main():
    print(majorityElement([3,2,3]))  # 3
    print(majorityElement([2,2,1,1,1,2,2]))  # 2

if __name__ == '__main__':
    main()
```
### algomajorityelement
#### Python
```python
package main

import "fmt"

func majorityElement(nums []int) int {
	element, cnt := 0, 0
	for _, e := range nums {
		if element == e {
			cnt += 1
		} else if cnt == 0 {
			element, cnt = e, 1
		} else {
			cnt -= 1
		}
	}
	return element
}

func main() {
	fmt.Println(majorityElement([]int{3, 2, 3}))
	fmt.Println(majorityElement([]int{2, 2, 1, 1, 1, 2, 2}))
}
```
#### Go
```go
def main():
    x = [1, 2, 3, 7, 3]
    print(x.index(7))


if __name__ == '__main__':
    main()
```
### index
#### Python
```python
package main

import (
	"errors"
	"fmt"
)

func main() {
	x := []int{1, 2, 3, 7, 3}
	fmt.Println(func() int {
		for i, val := range x {
			if val == 7 {
				return i
			}
		}
		panic(errors.New("ValueError"))
	}())
}
```

## TODOs

Some things I'd like to add soon...

- "value in range(start, stop, step)" => a conditional statement
- Exhaustive implementation of list/dict/int/float/bytes methods
- 