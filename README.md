# zbx 
[Zabbix](http://www.zabbix.com/) command line interface 
Python2.7 & Python3.5 tested

## Sponsor
**Developed with the support and help of [BlaBlaCar](https://www.blablacar.co.uk/).**

BlaBlaCar is trusted community marketplace that connects drivers with empty seats to passengers looking for a ride.
Hoping to give them an effective tool

## Requirement
- >= [pyzabbix 0.7.4](https://github.com/lukecyca/pyzabbix)
- >= [tabulate 0.7.5](https://bitbucket.org/cesan3/python-tabulate) commit 3392795 - with fix #65 for ANSI Color
- >= [Click (6.6 tested)](https://github.com/pallets/click) a command line library for Python
- >= [Requests v2.11.0](https://github.com/kennethreitz/requests) HTTP for Humans

## Install
Exemple based on a debian linux box

#### Python2
- Install pip `apt-get install python-pip`
- Upgrade pip `easy_install -U pip`
- Install ConfigParser `pip install ConfigParser`
- Install Loggin `pip install logging`
- Rename `config.ini.example` to `config.ini`
- Add server url, login and password in `config.ini`
- run `pip3 install --editable .`

#### Python3
- Install python 3 `apt-get install python3` 
- Install pip3 `apt-get install python3-pip`
- Upgrade pip3 `easy_install3 -U pip`
- Rename `config.ini.example` to `config.ini`
- Add server url, login and password in `config.ini`
- run `pip3 install --no-cache-dir --editable .`

## Test
- run `cd ~` + `wich zbx` 
- run `zbx --version`from any where in your filesystem tree

## Versions
- 3.0.1
  - zbx group list
  - zbx alert history
  - zbx host notemplate
- 3.0.0
  - Python 2.7 & 3.5 compliance
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
