
build: test
	python setup.py sdist bdist_wheel

test:
	pytest -v
