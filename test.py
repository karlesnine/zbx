#!/usr/bin/env python
"""Test for zbx"""

import pytest
import zbx


@pytest.fixture
def fake_zbx():
    """Fake host."""
    import zbx

    def fake_req(m, p):
        print('M is : %s ' % m)
        if m == "host.get":
            return {'result': [{
                u'available': u'1', u'maintenance_type': u'0', u'snmp_errors_from': u'0',
                u'hostid': u'10084', u'description': u'', u'ipmi_errors_from': u'0',
                u'jmx_errors_from': u'0', u'tls_accept': u'1', u'ipmi_username': u'',
                u'snmp_disable_until': u'0', u'ipmi_authtype': u'-1', u'tls_subject':
                u'', u'host': u'zabbix.prod.zbx',
                u'ipmi_disable_until': u'0', u'disable_until': u'0', u'ipmi_password':
                u'', u'templateid': u'0', u'tls_issuer': u'', u'ipmi_available': u'0',
                u'lastaccess': u'0', u'tls_psk_identity': u'', u'ipmi_error': u'',
                u'snmp_error': u'', u'proxy_hostid': u'0', u'tls_psk': u'', u'name':
                u'vbbczabbix1.prod.par-1.h.blbl.cr', u'ipmi_privilege': u'2',
                u'maintenance_status': u'0', u'tls_connect': u'1',
                u'jmx_disable_until': u'0', u'jmx_error': u'', u'jmx_available': u'0',
                u'maintenanceid': u'0', u'status': u'0', u'snmp_available': u'0',
                u'error': u'', u'maintenance_from': u'0', u'flags': u'0',
                u'errors_from': u'0'}]}
        elif m == "template.get":
            return {'result': [{
                u'proxy_hostid': '0', u'host': u'Template OS Linux', u'status': '3',
                u'disable_until': '0', u'error': '', u'available': '0', u'errors_from': '0',
                u'lastaccess': '0', u'ipmi_authtype': '0', u'ipmi_privilege': '2',
                u'ipmi_username': '', u'ipmi_password': '', u'ipmi_disable_until': '0',
                u'ipmi_available': '0', u'snmp_disable_until': '0', u'snmp_available': '0',
                u'maintenanceid': '0', u'maintenance_status': '0', u'maintenance_type': '0',
                u'maintenance_from': '0', u'ipmi_errors_from': '0', u'snmp_errors_from': '0',
                u'ipmi_error': '', u'snmp_error': '', u'jmx_disable_until': '0',
                u'jmx_available': '0', u'jmx_errors_from': '0', u'jmx_error': '',
                u'name': 'Template OS Linux', u'flags': '0', u'templateid': '10001',
                u'description': '', u'tls_connect': '1', u'tls_accept': '1',
                u'tls_issuer': '', u'tls_subject': '', u'tls_psk_identity': '', u'tls_psk': ''
            }]}
        else:
            return "42"

    zbx.zapi.do_request = fake_req
    return zbx


def test_get_host_id(fake_zbx):
    """Test_get_host_id."""
    response = fake_zbx.get_host_id("zabbix.prod.zbx")
    assert response == "10084"


def test_get_template_id():
    """Test_get_template_id."""
    response = zbx.get_template_id("Template OS Linux")
    assert response == "10001"
