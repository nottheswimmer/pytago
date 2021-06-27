ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: build
build:
	py -m build

.PHONY: check
check:
	py -m twine check dist/*

.PHONY: upload
upload:
	py -m twine upload --skip-existing dist/*

.PHONY: uploadtest
uploadtest:
	py -m twine upload --repository-url https://test.pypi.org/legacy/ --skip-existing dist/*

.PHONY: install
install:
	pip install .

.PHONY: devinstall
devinstall:
	pip install -e .

.PHONY: test
test:
	py -m pytest

.PHONY: docs
docs:
	py ./scripts/generate_readme.py

.PHONY: newtest
newtest:
	py ./scripts/newtest.py
