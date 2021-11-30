from setuptools import setup, find_packages

setup(
    name='app',
    version='0.1.0',
    description='csv-parse setup',
    author='Diego Nieto',
    author_email='dnieto@gmail.com',
    url='https://www.dnieto-it.es',
    packages=find_packages(include=['app', 'app.*']),
    install_requires=[
        'PyQt5',
        'dateutils',
        'click',
        'numpy',
        'scipy'
    ],
    extras_require={'plotting': ['matplotlib']},
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest']
)
