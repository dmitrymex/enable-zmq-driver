#!/usr/bin/python

import argparse
import subprocess


CONTROLLER_PROCS = [
    'nova-api',
    'nova-cert',
    'nova-conductor',
    'nova-consoleauth',
    'nova-novncproxy',
    'nova-objectstore',
    'nova-scheduler',

#    'neutron-dhcp-agent',
#    'neutron-l3-agent',
#    'neutron-metadata-agent',
#    'neutron-ns-metadata-proxy',
#    'neutron-openvswitch-agent',
    'neutron-server',

    'cinder-api',
    'cinder-backup',
    'cinder-scheduler',
    'cinder-volume',

    'keystone',

    'glance-api',
    'glance-registry',

    'heat-api',
    'heat-api-cfn',
    'heat-api-cloudwatch',
#    'heat-engine',
]

COMPUTE_PROCS = [
    'nova-compute',

    'neutron-plugin-openvswitch-agent'
]

PCS_RESOURCES = [
    'p_neutron-plugin-openvswitch-agent',
    'p_neutron-dhcp-agent',
    'p_neutron-metadata-agent',
    'p_neutron-l3-agent',
    'p_heat-engine'
]

CONTROLLER_CONFIGS = [
    '/etc/neutron/neutron.conf',
    '/etc/keystone/keystone.conf',
    '/etc/cinder/cinder.conf',
    '/etc/nova/nova.conf',
#    '/etc/murano/murano.conf',
    '/etc/glance/glance-registry.conf',
    '/etc/glance/glance-api.conf',
    '/etc/heat/heat.conf',
]

COMPUTE_CONFIGS = [
    '/etc/nova/nova.conf',
    '/etc/neutron/neutron.conf',
]


def get_command_output(cmd):
    #print 'Executing cmd: %s' % cmd
    pp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    outp, err = pp.communicate()

    if pp.returncode != 0:
        raise RuntimeError('Process returned non-zero code %i' % pp.returncode)

    return outp.strip()


def restart_processes_on_nodes(nodes, processes):
    for node in sorted(nodes):
        if not node:
            continue

        print '\nRestarting services on node %s' % node

        for proc in processes:
            if args.dry_run:
                print "ssh %s 'service %s restart'" % (node, proc)
            else:
              try:
                print get_command_output("ssh %s 'service %s %s'" % (node, proc, args.action))
              except:
                pass


def restart_resources(node, resources):
    if args.action == 'start':
        pcs_action = 'enable'
    elif args.action == 'stop':
        pcs_action = 'disable'
    else:
        raise RuntimeError('abacsd')

    print '\nRestarting resources on controller %s' % node
    for res in resources:
        print 'Restarting resource %s' % res
        if not args.dry_run:
            print get_command_output("ssh %s 'pcs resource %s %s'" % (node, pcs_action, res))


parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', dest='dry_run', action='store_true')
parser.add_argument('--action', dest='action', type=str)
args = parser.parse_args()

if args.dry_run:
    print 'Performing dry run'


controllers = get_command_output("fuel nodes 2>&1 | grep controller | awk '{ print $10 }'").split('\n')
computes = get_command_output("fuel nodes 2>&1 | grep compute | awk '{ print $10 }'").split('\n')

if args.dry_run:
    controllers = controllers[:1]
    computes = computes[:2]

restart_resources(controllers[0], PCS_RESOURCES)

#controllers=["10.20.0.5"]
restart_processes_on_nodes(controllers, CONTROLLER_PROCS)
restart_processes_on_nodes(computes, COMPUTE_PROCS)
