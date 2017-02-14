#!/usr/bin/env python
"""Zabbix command ligne tools"""
# Usage: zbx.py
# Summary: Zabbix commands line interface
# Help: Commands for Zabbix
# Dude, Chick, Read the f****** README.md for dependancy and compliance !!

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
    # from backports import configparser

import os
# import re
# import socket
import sys
import time
# from datetime import datetime

# Find where the code is
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Force lib version embedded because tested or patched !
vendor_dir = os.path.join(BASE_DIR, 'vendor/python')
sys.path.insert(1, vendor_dir)

from pyzabbix import ZabbixAPI

from tabulate import tabulate
############################################
# Use for debug exchange with api
############################################
# import logging
# stream = logging.StreamHandler(sys.stdout)
# stream.setLevel(logging.DEBUG)
# log = logging.getLogger('pyzabbix')
# log.addHandler(stream)
# log.setLevel(logging.DEBUG)
############################################
# Use for debug step by step
############################################
# import pdb; pdb.set_trace()

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
@click.version_option(version='3.0.2')
def zabbix():
    """Zabbix user command line tools."""
    pass


@zabbix.group()
def items():
    """Item sub-commands management."""
    pass

##########################################################################
# FUNCTIONS
##########################################################################


def get_group_id(group_name):
    """Get the group id."""
    response = zapi.hostgroup.get(
        output='extend',
        filter={"name": group_name}
    )
    if not response:
        click.echo('Group Name "%s" not found' % group_name)
        sys.exit(1)
    else:
        result = response[0]["groupid"]
        return result


def get_host_id(fqdn):
    """Get the host id."""
    response = zapi.host.get(
        output='extend',
        filter={"host": fqdn},
    )
    if not response:
        click.echo('Host Name "%s" not found' % fqdn)
        sys.exit(1)
    else:
        result = response[0]["hostid"]
        return result


def get_host_in_a_group(group_id):
    """Get list of host in a group."""
    response = zapi.host.get(
        output='extend',
        groupids=group_id,
        monitored_hosts=1,
        sortfield='host'
    )
    response.sort()
    if not response:
        click.echo('No host found in group id "%s"' % group_id)
        sys.exit(1)
    else:
        result = response
        return result


def get_key_item(host_id, item_key_name):
    """Get the key item id."""
    response = zapi.item.get(
        output="extend",
        hostids=host_id,
        search={"key_": item_key_name},
        sortfield="name"
    )
    if not response:
        click.echo('item key name "%s" not found in host id "%s"' % (item_key_name, host_id))
        sys.exit(1)
    else:
        result = response
        # import pdb; pdb.set_trace()
        return result


def get_item_last_value(item_value_type, item_searched_id, host_id):
    """Get item last value."""
    response = zapi.history.get(
        history=item_value_type,
        output='extend',
        itemids=item_searched_id,
        time_from=time.time() - 7200,
        time_till=time.time(),
        hostids=host_id,
        sortfield='clock',
        sortorder='DESC',
        limit=1
    )
    if not response:
        click.echo('No item value found : %s %s %s' % (item_value_type, item_searched_id, host_id))
        sys.exit(1)
    else:
        result = response
        return result[0]["value"]

##########################################################################
# COMMANDE
##########################################################################


@items.command("get")
@click.argument('item_key_name')
@click.argument('source_name')
@click.option('--group', 'source', flag_value='group', default=True)
@click.option('--host', 'source', flag_value='host')
def items_get(item_key_name, source_name, source):
    """List last value for a item key for all host in a groupe name."""
    if source == "group":
        group_id = get_group_id(source_name)
        tableau_server_in_group = []

        # List host in group
        list_servers = get_host_in_a_group(group_id)

        # get the id of the firt host in the list and
        # get the value_type of the item key required
        # # import pdb; pdb.set_trace()
        firt_host_id = get_host_id(list_servers[0]['host'])
        item = get_key_item(firt_host_id, item_key_name)
        item_value_type = item[0]['value_type']

        # For eatch host
        # Find the host id
        # Find the item id
        # Get the lastdata for the item
        for host in list_servers:
            host_id = get_host_id(host)
            item = get_key_item(host_id, item_key_name)
            item_searched_id = item[0]['itemid']
            item_value = get_item_last_value(item_value_type, item_searched_id, host_id)
            tableau_server_in_group.append([host["name"], source_name, item_value])
        header = [Bold + "NAME", "Group", item_key_name + UnBold]
        print(tabulate(tableau_server_in_group, headers=header, tablefmt="plain", numalign="left"))
    if source == "host":
        host_id = get_host_id(source_name)
        item = get_key_item(host_id, item_key_name)
        item_searched_id = item[0]['itemid']
        item_value_type = item[0]['value_type']
        item_value = get_item_last_value(item_value_type, item_searched_id, host_id)
        click.echo('%s %s %s' % (source_name, item_key_name, item_value))


# MAIN
if __name__ == '__main__':
    zabbix()
