# zbx 
zabbix command line interface 
- Python3
- [pyzabbix 0.7.4](https://github.com/lukecyca/pyzabbix)
- [tabulate 0.7.5](https://bitbucket.org/cesan3/python-tabulate) commit 3392795 - with fix #65 for ANSI Color
- [Click (6.6 tested)](https://github.com/pallets/click) a command line library for Python
- [Requests v2.11.0](https://github.com/kennethreitz/requests) HTTP for Humans

## Install
#### Mandatory 
- Rename `config.ini.example` to `config.ini`
- Add server url, login and password in `config.ini`
- run `sudo pip3 install click`
- run `pip3 install --no-cache-dir --editable .`

#### Optional
- run `sudo pip3 install pyzabbix`
- run `sudo pip3 install tabulate`

## Test
- run `cd ~` + `wich zbx` 
- run `zbx --version`from any where in your filesystem tree

## Versions

- 1.0.0
	- rename to zbx
	- use click for implement argument & option 
- 0.0.0
	- p.o.c alerts.py
