
build: test
	python setup.py sdist bdist_wheel

test:
	python setup.py test --addopts -v
