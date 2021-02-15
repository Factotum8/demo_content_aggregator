#!/usr/bin/env python3
# coding=utf-8
from setuptools import setup


setup(
    python_requires='~=3.8',

    install_requires=[
        # Production requirements (always need)
        "aiohttp==3.6.2",
        "PyYAML==5.3.1",
        "python3-logstash==0.4.80",
        "aiopg==1.0.0",
        "peewee==3.13.3",
        "peewee-async==0.7.0",
        "marshmallow>=3.10.0"
    ],

    # tests_require - New in 41.5.0: Deprecated the test command.
    extras_require={
        # test requirements
        'test': [
            "mock==2.0.0",
            "freezegun==0.3.12",
            "asynctest==0.12.2",
            "coverage>=5.1",
        ]
    },
)

