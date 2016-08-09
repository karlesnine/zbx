#!/usr/bin/env python3
# Usage: zbx.py
# Summary: Zabbix commands line interface
# Help: Commands for Zabbix
# Python3 compiante only
# Embed for failback : [pyzabbix 0.7.4](https://github.com/lukecyca/pyzabbix)
# Embed for failback : [tabulate 0.7.5](https://bitbucket.org/cesan3/python-tabulate) commit 3392795 - with fix #65 for ANSI Color
# [Use Click a command line library for Python](https://github.com/pallets/click)

import re
import configparser
import io
import os
import sys
from datetime import datetime

# Find where the code is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import or use the embed version of fail with a correct warning msg
try:
    import click
except ImportError:
    sys.exit("You need Click! install it from https://github.com/pallets/click or run : sudo pip3 install click.")

try:
	from pyzabbix import ZabbixAPI
	from tabulate import tabulate
except:
	vendor_dir = os.path.join(BASE_DIR, 'vendor/python')
	sys.path.append(vendor_dir)
	from pyzabbix import ZabbixAPI
	from tabulate import tabulate


# Import config file for zabbix API access
configfile = BASE_DIR+'/config.ini'
config = configparser.ConfigParser()
config.read(configfile)
ZABBIX_SERVER = config['zabbix']['server']
ZABBIX_USER = config['zabbix']['user']
ZABBIX_PASSWORD = config['zabbix']['password']

# Color stuff
eCOLOR_NONE="\033[0;39m"
eLIGHT_RED="\033[1;31m"
eLIGHT_GREEN="\033[1;32m"
Bold="\033[1m"
UnBold="\033(B\033[m"

# Create connection to the zabbix api
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(ZABBIX_USER,ZABBIX_PASSWORD)

# use Click, a command line library for Python
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def zabbix():
	"""This is a Zabbix user command line tools."""
	pass

# UNMONITORED
@zabbix.command()
def unmonitored():
	"""List all host set in zabbix but not monitored (Disabled)"""
	TableauUnmonitored =[]
	unmonitored = zapi.host.get(
		output='extend',
		filter={"status":1}
		)
	for host in unmonitored:
		TableauUnmonitored.append([host["name"],"Not monitored"])
	Header = [Bold+"NAME", "STATUS"+UnBold]
	print(tabulate(TableauUnmonitored,headers=Header,tablefmt="plain"))

# ALERTS
@zabbix.command()
def alerts():
	"""List the last 200 alerts with all that in "warning" or supperior red if no maintenance is configured or acknowledgement envoy"""
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


# MAIN
if __name__ == '__main__':
	zabbix()