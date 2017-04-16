# -*- coding: utf-8 -*-

from setuptools import setup

version = '2.1.19'

setup(
    name = 'qqbot',
    version = version,
    packages = ['qqbot'],
    entry_points = {
        'console_scripts': [
            'qqbot = qqbot:RunBot',
            'qq = qqbot:QTerm'
        ]
    },
    install_requires = ['requests', 'certifi', 'flask', 'apscheduler'],
    description = "QQBot: A conversation robot base on Tencent's SmartQQ",
    author = 'pandolia',
    author_email = 'pandolia@yeah.net',
    url = 'https://github.com/pandolia/qqbot/',
    download_url = 'https://github.com/pandolia/qqbot/archive/%s.tar.gz' % \
                    version,
    keywords = ['QQBot', 'conversation robot', 'tencent', 'qq',
                'web', 'network', 'python', 'http'],
    classifiers = [],
)
