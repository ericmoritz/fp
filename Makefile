all: test documentation
html:
	cd docs; make html

test:
	python setup.py test
	cd docs; make doctest

clean:
	rm -rf docs/build
