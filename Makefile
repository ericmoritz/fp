all: test documentation
html:
	cd docs; make html

test:
	python setup.py test
	@make doctest

doctest: doc-deps
	cd docs; make doctest

doc-deps:
	pip install sphinx

clean:
	rm -rf docs/build
