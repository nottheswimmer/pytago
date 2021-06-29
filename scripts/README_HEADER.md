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
- `go get -u golang.org/x/tools/cmd/goimports mvdan.cc/gofumpt github.com/segmentio/golines`

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