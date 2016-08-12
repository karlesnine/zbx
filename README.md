# zbx 
zabbix command line interface 
- Python3
- [pyzabbix 0.7.4](https://github.com/lukecyca/pyzabbix)
- [tabulate 0.7.5](https://bitbucket.org/cesan3/python-tabulate) commit 3392795 - with fix #65 for ANSI Color
- [Click (6.6 tested)](https://github.com/pallets/click) a command line library for Python
- [Requests v2.11.0](https://github.com/kennethreitz/requests) HTTP for Humans

## Install
Exemple based on a debian linux box

#### Python 
- Install python 3 `apt-get install python3` 
- Install pip3 `apt-get install python3-pip`
- Upgrade pip3 `easy_install3 -U pip`

#### zbx 
- Rename `config.ini.example` to `config.ini`
- Add server url, login and password in `config.ini`
- run `sudo pip3 install click`
- run `pip3 install --no-cache-dir --editable .`

## Test
- run `cd ~` + `wich zbx` 
- run `zbx --version`from any where in your filesystem tree

## Versions
- 2.0.0
  - zbx alert list
  - zbx alert ack EVEN-ID MESSAGE
  - zbx host add FQDN
  - zbx host del FQDN
  - zbx maintenance add FQDN DURATION
  - zbx maintenance del FQDN DURATION
  - zbx maintenance list
  - zbx maintenance gc
  - zbx monitor enable FQDN
  - zbx monitor disable FQDN
  - zbx unmonitored

- 1.0.0
	- rename to zbx
	- use click for implement argument & option 
- 0.0.0
	- p.o.c alerts.py
