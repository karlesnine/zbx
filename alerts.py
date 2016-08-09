#!/usr/bin/env python3
# Usage: alerts.py
# Summary: Zabbix commands
# Help: Commands for Zabbix
# Python3 compiante only
# embed for failback : [pyzabbix 0.7.4](https://github.com/lukecyca/pyzabbix)
# embed for failback : [tabulate 0.7.5](https://bitbucket.org/cesan3/python-tabulate) commit 3392795 - with fix #65 for ANSI Color


import re
import configparser
import io
from datetime import datetime
import os
import sys

#root_dir = os.getenv('_BBC_ROOT', os.path.dirname(./.abspath(__file__)))

try:
	from pyzabbix import ZabbixAPI
	from tabulate import tabulate
except:

	BASE_DIR = os.path.dirname(os.path.realpath(__file__))
	vendor_dir = os.path.join(BASE_DIR, 'vendor/python')
	sys.path.append(vendor_dir)
	from pyzabbix import ZabbixAPI
	from tabulate import tabulate

# Import config
config = configparser.ConfigParser()
config.read('config.ini')
ZABBIX_SERVER = config['zabbix']['server']
ZABBIX_USER = config['zabbix']['user']
ZABBIX_PASSWORD = config['zabbix']['password']

# Color stuff
eCOLOR_NONE="\033[0;39m"
eLIGHT_RED="\033[1;31m"
eLIGHT_GREEN="\033[1;32m"
Bold="\033[1m"
UnBold="\033(B\033[m"

# Connection to the zabbix api
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(ZABBIX_USER,ZABBIX_PASSWORD)

TableauAlerte =[]
triggers = zapi.trigger.get(limite=200,
	selectLastEvent='extend',
	selectGroups='extend',
	selectHosts='extend',
	monitored=1,
	skipDependent=1,
	output='extend',
	expandDescription=1,
	expandData='host',
	sortfield='lastchange',
	sortorder='DESC',
	filter={"priority":[2,3,4,5],"value":1}
	)

for t in triggers:
	EventId = '-'
	ack = '-'
	Maintenance = '-'
	LastDate = datetime.fromtimestamp( int(t['lastchange']) ).strftime('%Y-%m-%d %H:%M:%S')
	if t['lastEvent']:
		EventId = t['lastEvent']['eventid']
		event = zapi.event.get(eventids=EventId,
			select_acknowledges='extend',
			output='extend')
		#print("{0}".format(t))
		#import pdb; pdb.set_trace()
		if event[0]['acknowledges']:
			ack_by = event[0]["acknowledges"][0]["alias"]
			CleanAckDescription = re.sub('----\[BULK ACKNOWLEDGE\]----', r'', event[0]['acknowledges'][0]['message'] )
			ack = ack_by+ " " + CleanAckDescription
		if t["hosts"][0]["maintenance_status"] == "1":
			Maintenance = "Main.."
	if int(t['priority']) >= 3 and Maintenance != "Main.." and not event[0]['acknowledges'] :
		Alerte = [eLIGHT_RED+t['hosts'][0]['name'],LastDate,EventId,t["description"],Maintenance,ack+ eCOLOR_NONE]
	else:
		Alerte = [t['hosts'][0]['name'],LastDate,EventId,t["description"],Maintenance,ack]
	TableauAlerte.append(Alerte)
Header = [Bold+"Host","Last Event","Event Id","Description","Maintenance","Acknowledge"+UnBold]
print(tabulate(TableauAlerte,headers=Header,tablefmt="plain"))