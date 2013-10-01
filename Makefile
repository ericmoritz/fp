all: test

deps:
	python setup.py develop

html: test doc-deps
	cd docs; make html


test: deps
	pip install pytest pytest-cov pytest-pep8
	py.test --pep8 --doctest-modules --cov fp fp/

doc-deps:
	pip install sphinx

clean:
	rm -rf docs/build
