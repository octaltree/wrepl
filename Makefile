clean: wrepl.egg-info dist build
	rm -rf $^
build:
	python setup.py sdist bdist_wheel
install:
	python setup.py install
upload:
	twine upload dist/*
