#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'click',
    'keyring==8.7',
    'selenium'
]

setup(
    name='wat',
    version='0.1.0',
    description="Web Automation Toolkit",
    long_description=readme + '\n',
    author="Shaohan Hu",
    author_email='hushaohan@gmail.com',
    url='https://github.com/hushaohan/wat',
    python_requires='>=3.6',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wat=wat.main:cli'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='wat',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)
