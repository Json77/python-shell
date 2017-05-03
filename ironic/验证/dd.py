#!/usr/bin/env python
# encoding: utf-8
import urllib2
import json
import sys
import uuid


def get_token(url, username, password):
    auth = {
        "auth": {
            "tenantName": "admin",
            "passwordCredentials": {
                "username": username,
                "password": password
            }
        }
    }

    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    data = json.dumps(auth)
    req = urllib2.Request(url, headers=headers, data=data)
    response = urllib2.urlopen(req)
    if str(response.code).startswith('20'):
        json_str = response.read()
        json_obj = json.loads(json_str)
        return json_obj['access']['token']['id']
    return None


def get_nodes(url, token):
    headers = {'Content-Type': 'application/json',
               'accept': 'application/json',
               'X-Auth-Token': token}
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    return response.read()


def get_ports(url, token):
    headers = {'Content-Type': 'application/json',
               'accept': 'application/json',
               'X-Auth-Token': token}
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    return response.read()


def create_node(url, node, token):
    headers = {'Content-Type': 'application/json',
               'accept': 'application/json',
               'X-Auth-Token': token,
               'X-OpenStack-Ironic-API-Version': '1.9'
              }
    data = json.dumps(node)
    req = urllib2.Request(url, headers=headers, data=data)
    response = urllib2.urlopen(req)
    if str(response.code).startswith('20'):
        return 'SUCCESS'
    print response.reason
    return 'FAILED'


def get_progess(url, token):
    headers = {'Content-Type': 'application/json',
               'accept': 'application/json',
               'X-Auth-Token': token}
    req = urllib2.Request(url, headers=headers)
    response = urllib2.urlopen(req)
    return response.read()


if __name__ == '__main__':
    ip = '192.168.2.40'
    token_url = 'http://{}:5000/v2.0/tokens'.format(ip)
    nodes_url = 'http://{}:6385/v1/nodes'.format(ip)
    ports_url = 'http://{}:6385/v1/ports'.format(ip)
    username = "admin"
    password = "keystone"
    token = get_token(token_url, username, password)
    if not token:
        sys.exit(1)


    action = sys.argv[1]
    if action == 'create':
        # create node
        # node = {
        #     'name': 'node',
        #     'uuid': str(uuid.uuid1()),
        #     'driver': 'pxe_ipmitool',
        #     'driver_info': {
        #         'ipmi_address': '10.42.200.161',
        #         'ipmi_username': 'root',
        #         'ipmi_password': 'ossdbg1'
        #     }
        # }
        node = {
            "name": "node",
            "driver": "pxe_ipmitool",
            "driver_info": {
                "ipmi_address": "10.42.200.161",
                "ipmi_username": "root",
                "ipmi_password": "ossdbg1",
                "deploy_kernel": "cdd108ac-b0d3-40c5-8400-4abdd002b995",
                "deploy_ramdisk": "bf95c806-22b2-4a17-9944-8571de8d02d4",
            },
            "properties": {
                "cpus": 48,
                "memory_mb": 4096,
                "local_gb": 200,
                "cpu_arch": "x86_64"
            }
        }
        print create_node(nodes_url, node, token)
    elif action == 'ports':
        print get_ports(ports_url, token)
    elif action == 'nodes':
        print get_nodes(nodes_url, token)
    elif action == 'progress':
        nodes = get_nodes(nodes_url, token)
        nodes_obj = json.loads(nodes)
        uuid = nodes_obj['nodes'][0]['uuid']
        progress_url = 'http://{}:6385/v1/nodes/{}/progress'.format(ip, uuid)
        print get_progess(progress_url, token)

