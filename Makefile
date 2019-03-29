clean: wrepl.egg-info dist build
	rm -rf $^
build:
	python setup.py sdist bdist_wheel
upload:
	twine upload dist/*
