#!/usr/bin/env python3
# zbx setup.py
from setuptools import setup

setup(name = 'zbx',
	version = '1.0.0',
	author = 'karles',
	maintainer = 'karles',
	author_email = 'charles-christian.croix@blablacar.com',
	maintainer_email = 'charles-christian.croix@blablacar.com',
	url = 'https://stash.priv.blablacar.net/projects/ADMIN/repos/zbxcli/browse',
	description = 'cli for zabbix',
	long_description = 'cli tool for zabbix user',
	license = 'GPL V3',
	plateformes = 'ALL',
	entry_points={
          'console_scripts': [
              'zbx = zbx:zabbix'
          ],
    },
    install_requires=[
          'click>=6.6',
          'Requests>=2.11.0',
      ],
	)
