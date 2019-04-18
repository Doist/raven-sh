# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        return ''

setup(
    name='raven-sh',
    version='0.5',
    author='Doist Developers',
    author_email='dev@doist.com',
    url='https://github.com/doist/raven-sh',
    description='raven-sh is a client for Sentry which can be used as '
                'a wrapper for cron jobs',
    long_description=read('README.rst'),
    py_modules=['raven_sh'],
    install_requires=[
        'sentry-sdk>=0.7.10',
    ],
    entry_points={
        'console_scripts': [
            'raven-sh = raven_sh:main',
        ],
    },
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development',
    ],
)
