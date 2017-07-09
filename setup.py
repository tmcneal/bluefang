#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

setup(
    name='bluefang',
    version='0.1.4',
    description='Bluetooth and HID utilities for Python 3',
    author='Todd McNeal',
    author_email='todd.mcneal@gmail.com',
    keywords = ['bluetooth', 'hid', 'l2cap', 'bluez', 'pybluez', 'dbus'],
    url='https://www.github.com/tmcneal/bluefang',
    packages=find_packages(exclude=['scripts', 'tests']),
    python_requires='>=3.4',
    install_requires=[
        'dbus-python==1.2.4',
        'PyBluez==0.22',
        'vext.gi==0.5.20'
    ]
)
