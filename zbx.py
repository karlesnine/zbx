#!/usr/bin/env python3
"""blablacar,"""
# Usage: zbx.py
# Summary: Zabbix commands line interface
# Help: Commands for Zabbix
# Dude, Chick, Read the f****** README.md for dependancy and compliance !!

import configparser
import os
import re
import socket
import sys
import time
from datetime import datetime

# Find where the code is
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Force lib version embedded because tested or patched !
vendor_dir = os.path.join(BASE_DIR, 'vendor/python')
sys.path.insert(1, vendor_dir)

from pyzabbix import ZabbixAPI

from tabulate import tabulate

# import logging
# stream = logging.StreamHandler(sys.stdout)
# stream.setLevel(logging.DEBUG)
# log = logging.getLogger('pyzabbix')
# log.addHandler(stream)
# log.setLevel(logging.DEBUG)

# Import or use the embed version of fail with a correct warning msg
try:
    import click
except ImportError:
    sys.exit("""
You need Click! install it from https://github.com/pallets/click"
or run : sudo pip3 install click."
""")

# Import config file for zabbix API access
configfile = BASE_DIR + '/config.ini'
config = configparser.ConfigParser()
config.read(configfile)
ZABBIX_SERVER = config['zabbix']['server']
ZABBIX_USER = config['zabbix']['user']
ZABBIX_PASSWORD = config['zabbix']['password']

# Color stuff
eCOLOR_NONE = "\033[0;39m"
eLIGHT_RED = "\033[1;31m"
eLIGHT_GREEN = "\033[1;32m"
Bold = "\033[1m"
UnBold = "\033(B\033[m"

# Create connection to the zabbix api
zapi = ZabbixAPI(ZABBIX_SERVER)
zapi.login(ZABBIX_USER, ZABBIX_PASSWORD)

# use Click, a command line library for Python
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.0.0')
def zabbix():
    """Zabbix user command line tools."""
    pass


@zabbix.group()
def maintenance():
    """Maintenance management sub-commands"""
    pass


@zabbix.group()
def host():
    """Host management sub-commands"""
    pass


@zabbix.group()
def monitor():
    """Monitore management sub-commands"""
    pass


##########################################################################
# FUNCTIONS
##########################################################################


def get_host_id(fqdn):
    """Get the host id."""
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


def get_template_id(template_name):
    """Get the template id"""
    response = zapi.template.get(
        output='extend',
        filter={"host": "Template OS Linux"}
    )
    if not response:
        print("Template not found in Zabbix : %s" % template_name)
        sys.exit(42)
    else:
        result = response[0]["templateid"]
        return result


def to_date(ts):
    """Humane date format."""
    return datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')


def get_maintenance_id(host_id):
    """Gate the maintenance id."""
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
    """Delete the maintenance."""
    response = zapi.maintenance.delete(maintenance_id,)
    if not response:
        print("Maintenance not found in Zabbix")
        sys.exit(42)
    else:
        result = response["maintenanceids"]
        return result


def add_maintenance(host_id, duration, fqdn):
    """Add a maintenance."""
    # start maintenance 5 minutes before now to avoid overlapping
    start = int(time.time()) - 300
    end = start + int(duration) + 300
    response = zapi.maintenance.create(
        groupids=["5"],
        hostids=[host_id],
        name="Scripted Maintenance: %s" % fqdn,
        maintenance_type=0,
        description="zbx scripted",
        active_since=start,
        active_till=end,
        timeperiods=[{"timeperiod_type": 0,
                      "start_date": start,
                      "period": duration
                      }],
    )
    result = response["maintenanceids"]
    return result

##########################################################################
# Maintenance sub command
##########################################################################


@maintenance.command()
def list():
    """List all maintenance currently set in the zabbix server"""
    response = zapi.maintenance.get(
        output='extend',
        selectGroups='extend',
        selectTimeperiods='extend',
    )
    tableau_maintenance = []
    for m in response:
        tableau_maintenance.append([
            m["name"], m["description"],
            to_date(m["active_since"]), to_date(m["active_till"])
        ])
    header = [Bold + "NAME", "DESCRIPTION", "ACTIVE SINCE", "ACTIVE UNTIL" + UnBold]
    print(tabulate(tableau_maintenance, headers=header, tablefmt="plain"))


@maintenance.command()
@click.argument('fqdn')
@click.argument('duration', default=3600)
def add(fqdn, duration):
    """Add a maintenance for the host specified."""
    host_id = get_host_id(fqdn)
    click.echo('Adding maintenance for %s during %s secondes' % (fqdn, duration))
    response = add_maintenance(host_id, duration, fqdn)
    click.echo('Maintenance id %s for %s added' % (response, fqdn))


@maintenance.command()
@click.argument('fqdn')
def remove(fqdn):
    """Remove a maintenance for the host specified."""
    host_id = get_host_id(fqdn)
    maintenance_id = get_maintenance_id(host_id)
    response = delete_maintenance(maintenance_id)
    click.echo('Maintenance id %s for %s removed' % (response, fqdn))


@maintenance.command()
def gc():
    """Maintenance garbage collector : remove all expired maintenance."""
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
# Host COMMANDS
##########################################################################


@host.command()
@click.argument('fqdn')
def create(fqdn):
    """Create a host in zabbix server."""
    template_os_linux = get_template_id("Template OS Linux")
    dns_data = socket.gethostbyname_ex(fqdn)
    ip = dns_data[2][0]
    response = zapi.host.create(
        host=fqdn,
        interfaces={"type": 1, "main": 1, "useip": 0, "ip": ip, "dns": fqdn, "port": "10050"},
        groups={"groupid": "5"},
        templates={"templateid": template_os_linux}
    )
    click.echo('%s id %s is added with basic linux template' % (fqdn, response["hostids"][0]))


@host.command()
@click.argument('fqdn')
def delete(fqdn):
    """Delete a host in zabbix server."""
    host_id = get_host_id(fqdn)
    response = zapi.host.delete(host_id)
    click.echo('%s id %s is removed of the zabbix server' % (fqdn, response["hostids"][0]))

##########################################################################
# Monitore COMMANDS
##########################################################################


@monitor.command()
@click.argument('fqdn')
def enable(fqdn):
    """Enable monitoring for a host."""
    host_id = get_host_id(fqdn)
    # enable is status = 0
    response = zapi.host.update(
        hostid=host_id,
        status=0
    )
    click.echo('%s id %s is monitored now' % (fqdn, response["hostids"]))


@monitor.command()
@click.argument('fqdn')
def disable(fqdn):
    """Disable monitoring for a host."""
    host_id = get_host_id(fqdn)
    response = zapi.host.update(
        hostid=host_id,
        status=1
    )
    click.echo('%s id %s is not monitored now' % (fqdn, response["hostids"]))


##########################################################################
# zbx general COMMANDS
##########################################################################


@zabbix.command()
def unmonitored():
    """List all host set in zabbix but not monitored (Disabled)"""
    tableau_unmonitored = []
    unmonitored = zapi.host.get(
        output='extend',
        filter={"status": 1}
    )
    for host in unmonitored:
        tableau_unmonitored.append([host["name"], "Not monitored"])
    header = [Bold + "NAME", "STATUS" + UnBold]
    print(tabulate(tableau_unmonitored, headers=header, tablefmt="plain"))


@zabbix.command()
def alerts():
    """List the last 200 alert.

    With all that in "warning" or supperior in red
    if no maintenance is configured or acknowledgement envoy
    """
    tableau_alerte = []
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
                                filter={"priority": [2, 3, 4, 5], "value": 1}
                                )

    for t in triggers:
        event_id = '-'
        ack = '-'
        maintenance = '-'
        last_date = datetime.fromtimestamp(int(t['lastchange'])).strftime('%Y-%m-%d %H:%M:%S')
        if t['lastEvent']:
            event_id = t['lastEvent']['eventid']
            event = zapi.event.get(eventids=event_id,
                                   select_acknowledges='extend',
                                   output='extend')
            if event[0]['acknowledges']:
                ack_by = event[0]["acknowledges"][0]["alias"]
                clean_ack_description = re.sub('----\[BULK ACKNOWLEDGE\]----', r'', event[0]['acknowledges'][0]['message'])
                ack = ack_by + " " + clean_ack_description
            if t["hosts"][0]["maintenance_status"] == "1":
                maintenance = "Main.."
        if int(t['priority']) >= 3 and maintenance != "Main.." and not event[0]['acknowledges']:
            alert = [eLIGHT_RED + t['hosts'][0]['name'], last_date, event_id, t["description"], maintenance, ack + eCOLOR_NONE]
        else:
            alert = [t['hosts'][0]['name'], last_date, event_id, t["description"], maintenance, ack]
        tableau_alerte.append(alert)
    header = [Bold + "Host", "Last Event", "Event Id", "Description", "Maintenance", "Acknowledge" + UnBold]
    print(tabulate(tableau_alerte, headers=header, tablefmt="plain"))

# MAIN
if __name__ == '__main__':
    zabbix()
