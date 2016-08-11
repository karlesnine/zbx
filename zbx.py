#!/usr/bin/env python3
# Usage: zbx.py
# Summary: Zabbix commands line interface
# Help: Commands for Zabbix
# Dude, Chick, Read the f****** README.md for dependancy and compliance !!

import re
import io
import os
import sys
import time
import socket
import configparser
from datetime import datetime

# import logging
# stream = logging.StreamHandler(sys.stdout)
# stream.setLevel(logging.DEBUG)
# log = logging.getLogger('pyzabbix')
# log.addHandler(stream)
# log.setLevel(logging.DEBUG)

# Find where the code is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import or use the embed version of fail with a correct warning msg
try:
	import click
except ImportError:
    sys.exit("You need Click! install it from https://github.com/pallets/click or run : sudo pip3 install click.")

try:
	import requests
except ImportError:
    sys.exit("You need requests! install it from https://github.com/kennethreitz/requests or run : sudo pip3 install requests.")

# Force lib version embedded
# Because tested or patched !
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

@zabbix.group()
def maintenance ():
	"""maintenances management sub-commands"""
	pass

##########################################################################
# FUNCTIONS
##########################################################################

def get_host_id(fqdn):
	response = zapi.host.get(
		output='extend',
		filter={"host": fqdn}
		)
	if not response:
		print("Host not found in Zabbix : %s" % fqdn)
		sys.exit(42)
	else:
		result = response[0]["hostid"]
		return result

def get_tempate_id(template_name):
	response = zapi.template.get(
		output='extend',
        filter={"host":"Template OS Linux"}
        )
	if not response:
		print("Template not found in Zabbix : %s" % template_name)
		sys.exit(42)
	else:
		result = response[0]["templateid"]
		return result

def to_date(ts):
    return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')

def get_maintenance_id(host_id):
	response = zapi.maintenance.get(
		output='extend',
		selectHosts='refer',
		selectGroups='refer',
		hostids=host_id
		)
	if not response:
		print("Maintenance not found in Zabbix")
		sys.exit(42)
	else:
		result = response[0]["maintenanceid"]
		return result

def delete_maintenance(maintenance_id):
	response = zapi.maintenance.delete(maintenance_id,)
	error = response.get('error')
	if not response:
		print("Maintenance not found in Zabbix")
		sys.exit(42)
	else:
		result = response["maintenanceids"]
		return result

def add_maintenance(host_id,duration,fqdn):
	start = int(time.time()) - 300 # start maintenance 5 minutes before now to avoid overlapping
	end = start + int(duration) + 300
	response = zapi.maintenance.create(
		groupids = ["5"],
		hostids = [host_id],
		name = "Scripted Maintenance: %s" % fqdn,
		maintenance_type = 0,
		description = "zbx scripted",
		active_since = start,
		active_till = end,
		timeperiods = [{"timeperiod_type":0,"start_date":start,"period":duration}],
		)
	return response

##########################################################################
# Maintenance sub command
##########################################################################

@maintenance.command()
@click.argument('fqdn')
@click.argument('duration', default = 3600)
def add(fqdn,duration):
	"""add a maintenance for the host specified """
	host_id = get_host_id(fqdn)
	click.echo('Adding maintenance for %s during %s secondes' % (fqdn, duration))
	response = add_maintenance(host_id,duration,fqdn)

@maintenance.command()
def list():
	"""List all maintenance currently set in the zabbix server"""
	response = zapi.maintenance.get(
    	output='extend',
    	selectGroups='extend',
    	selectTimeperiods='extend',
    	)
	TableauMaintenance = []
	for m in response:
		TableauMaintenance.append([m["name"],m["description"],to_date(m["active_since"]),to_date(m["active_till"])])
	Header = [Bold+"NAME", "DESCRIPTION", "ACTIVE SINCE", "ACTIVE UNTIL"+UnBold]
	print(tabulate(TableauMaintenance,headers=Header,tablefmt="plain"))

@maintenance.command()
@click.argument('fqdn')
def remove(fqdn):
	"""Remove a maintenance for the host specified """
	host_id = get_host_id(fqdn)
	maintenance_id = get_maintenance_id(host_id)
	response = delete_maintenance(maintenance_id)
	click.echo('Maintenance id %s for %s removed' % (response, fqdn))
	#import pdb; pdb.set_trace()

@maintenance.command()
def gc():
	"""maintenance garbage collector : remove all expired maintenance"""
	response = zapi.maintenance.get(
	output='extend',
	selectGroups='extend',
	selectTimeperiods='extend',
     )
	to_remove = []
	for maintenance in response:
		now = int(time.time())
		if int(maintenance['active_till']) < now:
			to_remove.append(maintenance)
	if len(to_remove) != 0:
		for m in to_remove:
			print("Removing expired %s" % m['name'])
			delete_maintenance(m['maintenanceid'])
	else:
		print("No expired maintenance to remove")

##########################################################################
# zbx general COMMANDS
##########################################################################

@zabbix.command()
@click.argument('fqdn')
@click.option('--add/--remove',default=None, required=True,help='add or remove a Host of the zabbix server')
def host(add,fqdn):
	"""Add or remove a linux host of the zabbix server """
	if add:
		template_os_linux = get_tempate_id("Template OS Linux")
		dns_data = socket.gethostbyname_ex(fqdn)
		ip = dns_data[2][0]
		response = zapi.host.create(
			host=fqdn,
			interfaces={"type":1,"main":1,"useip":0,"ip":ip,"dns":fqdn,"port":"10050"},
			groups={"groupid":"5"},
			templates={"templateid":template_os_linux}
			)
		click.echo('%s id %s is added with basic linux template' % (fqdn, response["hostids"][0]))
	else:
		host_id = get_host_id(fqdn)
		response = zapi.host.delete(host_id)
		click.echo('%s id %s is removed of the zabbix server' % (fqdn, response["hostids"][0]))

@zabbix.command()
@click.argument('fqdn')
@click.option('--enable/--disable',default=None, required=True,help='enable or disable Host monitoring')
def monitor(enable,fqdn):
	"""Enable or Disable monitoring for the host specified"""
	host_id = get_host_id(fqdn)
	# enable is status = 0
	if enable:
		response = zapi.host.update(
			hostid=host_id,
			status=0
			)
		click.echo('%s is monitored now' % fqdn)
	else:
		response = zapi.host.update(
			hostid=host_id,
			status=1
			)
		click.echo('%s is not monitored now' % fqdn)

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