.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/

lint: ## check style with flake8
	flake8 --ignore=E265,E226 pint tests

test: ## run tests quickly with the default Python
		cd tests && pytest --ff

coverage: ## check code coverage quickly with the default Python
		pytest tests --cov=pint
		coverage report -m
		coverage html
		$(BROWSER) htmlcov/index.html

notebooks:
	jupytext --sync examples/*.py
	jupytext --pipe black --pipe-fmt py:percent examples/*.ipynb
	jupyter nbconvert --execute --inplace examples/*.ipynb
	jupytext --sync examples/*.ipynb
	# jupytext --to script examples/*.md

docs-clean:
	mkdir -p docs/api
	rm -f docs/api/*
	rm -f docs/modules.rst
	$(MAKE) -C docs clean

docs-build: docs-clean ## generate Sphinx HTML documentation, including API docs
	$(MAKE) -C docs html

docs: docs-build
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

# Release using twine, which will upload to PyPI
release: clean dist
	echo python -m twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
