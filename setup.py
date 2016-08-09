#!/usr/bin/env python3
# zbx setup.py
from setuptools import setup

import zbx
setup(name = 'zbx',
	version = '1.0.0',
	author = 'karles',
	maintainer = 'karles',
	author_email = 'charles-christian.croix@blablacar.com',
	maintainer_email = 'charles-christian.croix@blablacar.com',
	url = 'https://github.com/karlesnine/zbx',
	description = 'cli for zabbix',
	long_description = 'cli tool for zabbix user',
	install_requires = ['click>=6.0'],
	license = 'GPL V3',
	plateformes = 'ALL',
	entry_points={
          'console_scripts': [
              'zbx = zbx:zabbix'
          ],
    },
	)
