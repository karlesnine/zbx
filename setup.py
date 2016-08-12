#!/usr/bin/env python
"""Install,"""
# zbx setup.py
from setuptools import setup

setup(name='zbx',
      version='3.0.0',
      author='karles',
      maintainer='karles',
      author_email='charles-christian.croix@blablacar.com',
      maintainer_email='charles-christian.croix@blablacar.com',
      url='https://stash.priv.blablacar.net/projects/ADMIN/repos/zbxcli/browse',
      description='cli for zabbix',
      long_description='cli tool for zabbix user',
      license='GPL V3',
      plateformes='ALL',
      entry_points={
          'console_scripts': [
              'zbx = zbx:zabbix'
          ],
      },
      extras_require={
          ':python_version=="2.7"': ['click>=6', 'requests>=2.11.0', 'logging>=0.4.9.6', 'configparser>=3.5.0'],
          ':python_version=="3.5"': ['click>=6.6', 'requests>=2.11.0', 'configparser2>=4']
      }
      )
