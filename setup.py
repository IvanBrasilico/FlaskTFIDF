import ast
import re
from setuptools import find_packages, setup
setup(
    name='TEC Rank',
    description='TEC Rank',
    version='0.1',
    url='https://github.com/IvanBrasilico',
    license='MIT',
    author='Ivan Brasilico',
    author_email='brasilico.ivan@gmail.com',
    packages=find_packages(),
    install_requires=[
        'click',
        'Flask',
        'Flask-Bootstrap',
        'Flask-Cors',
        'Flask-nav',
        'matplotlib',
        'nltk',
        'numpy',
        'Pillow',
        'pymongo',
        'SQLAlchemy',
        'wordcloud'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite="tests",
    package_data={
    },
    extras_require={
        'dev': [
            'coverage',
            'flake8',
            'isort',
            'pytest',
            'pytest-cov',
            'pytest-mock',
            'sphinx',
            'testfixtures',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.5',
    ],
)
