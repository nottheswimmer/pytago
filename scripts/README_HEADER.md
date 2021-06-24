# pytago

Transpiles some Python into human-readable Golang.

## Installation

### Prerequisites

- [Go 1.16.x](https://golang.org/dl/)
- [Python 3.10.x](https://www.python.org/downloads/release/python-3100b3/)
  - No, it will not work on 3.9. Search the code for "match."
- `go get golang.org/x/tools/cmd/goimports`
- `go get mvdan.cc/gofumpt`

### Installing

#### via pip
```
pip install pytago
```

#### via setup.py

```
git clone https://github.com/nottheswimmer/pytago/
cd pytago
pip install .
```

## Usage

```
{% usage %}
```

## Examples

All examples presented here are used as tests for the program.

{% examples %}

## TODOs

Some things I'd like to add soon...

- "value in range(start, stop, step)" => a conditional statement
- Exhaustive implementation of list/dict/int/float/bytes methods
- 