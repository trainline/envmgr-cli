
reload: uninstall rebuild install

uninstall:
	sudo -H pip uninstall -y envmgr

install:
	sudo -H pip install dist/envmgr-0.2.0-py2.py3-none-any.whl

rebuild:
	python setup.py sdist bdist_wheel
