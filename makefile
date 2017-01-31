
reload: uninstall rebuild install

uninstall:
	pip uninstall -y envmgr

install:
	pip install dist/envmgr-0.1.0-py2.py3-none-any.whl

rebuild:
	python setup.py sdist bdist_wheel
