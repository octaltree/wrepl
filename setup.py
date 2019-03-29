from setuptools import setup, find_packages

setup(
        name='wrepl',
        version="0.0.1",
        description="Watch-Read-Eval-Print Loop",
        url='https://github.com/octaltree/wrepl',
        author='octaltree',
        author_email='octalreee@gmail.com',
        license='MIT',
        install_requires=['watchdog', 'readchar'],
        keywords='wrepl',
        classifiers=[
            'Development Status :: 3 - Alpha'],
        packages=find_packages(exclude=('tests')),
        entry_points={'console_scripts': ['wrepl=wrepl.__init__:main']})
