#!/usr/bin/env python

from setuptools import setup, find_packages
import sys

setup(
    name='bluefang',
    version='0.1.2',
    description='Bluetooth and HID utilities for Python 3',
    author='Todd McNeal',
    author_email='todd.mcneal@gmail.com',
    keywords = ['bluetooth', 'hid', 'l2cap', 'bluez', 'pybluez', 'dbus'],
    url='https://www.github.com/tmcneal/bluefang',
    packages=find_packages(exclude=['scripts', 'tests']),
    python_requires='>=3.4',
    install_requires=[
        'dbus-python==1.2.4',
        'PyBluez==0.22.1',
        'vext.gi==0.5.20',
        'lightblue==0.4.1;platform_system=="Darwin"',
        'pyobjc==3.2.1;platform_system=="Darwin"'
    ],
    dependency_links=[
        'git+https://github.com/tmcneal/pybluez@e1311bd83447a641d59a36c8c32d8e3f75e1a34c#egg=PyBluez-0.22.1',
        'git+https://github.com/tmcneal/lightblue-0.4@7575c17bb439029436cba5c0eeba3d745c3361f1#egg=lightblue-0.4.1'
    ]
)
