
reload: uninstall rebuild install

uninstall:
	pip uninstall -y envmgr

install:
	pip install dist/**.whl

rebuild:
	python setup.py sdist bdist_wheel
