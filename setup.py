#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages,find_namespace_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Evdoxia Taka",
    author_email='e.taka.1@research.gla.ac.uk',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Interactive multiverse diagram is an interactive tool for visualizating and exploring Bayesian probabilistic programming models and inference data.",
    entry_points={
        'console_scripts': [
            'ipme=ipme.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='Bayesian probabilistic modeling, Bayesian inference, Markov Chain Monte Carlo, interactive visualization, uncertainty visualization, interpetability',
    name='ipme',
    packages=find_packages(include=['ipme','ipme*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/evdoxiataka/ipme',
    version='0.1.0',
    zip_safe=False,
)
