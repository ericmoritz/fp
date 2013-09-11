all: test

deps:
	python setup.py develop

html: test doc-deps
	cd docs; make html


test: deps
	py.test --doctest-modules fp/ fp/tests.py

doc-deps:
	pip install sphinx

clean:
	rm -rf docs/build
