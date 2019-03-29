clean: wrepl.egg-info dist build
	rm -rf $^
build: clean
	python setup.py sdist bdist_wheel
install: build
	python setup.py install
upload: build
	twine upload dist/*
