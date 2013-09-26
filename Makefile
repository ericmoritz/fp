all: test

deps:
	python setup.py develop

html: test doc-deps
	cd docs; make html


test: deps
	pip install pytest pytest-cov
	py.test --doctest-modules --cov fp fp/

doc-deps:
	pip install sphinx

clean:
	rm -rf docs/build
