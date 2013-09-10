all: test documentation
html:
	cd docs; make html

test:
	py.test --doctest-modules fp/ fp/tests.py
	@make doctest

doctest: doc-deps
	@make -C docs/ doctest

doc-deps:
	pip install sphinx

clean:
	rm -rf docs/build
