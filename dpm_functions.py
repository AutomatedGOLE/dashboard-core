#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Data Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

from collections import defaultdict
import database as db
import threading
from general_functions import ping
from general_functions import remote_ping
import time
import os
import paramiko

isAlias_type = "http://schemas.ogf.org/nml/2013/05/base#isAlias"


def add_switchports(topology, switch, switchtype, labeltype, encoding, cursor):
    if switchtype == 'default' or switchtype == 'wildcard':
        # print ("switch default or wildcard")
        # Add all ports -> not yet checking for labeltype and encoding
        for relation in topology[2][0].findall('{http://schemas.ogf.org/nml/2013/05/base#}Relation'):
            if relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasInboundPort" or relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasOutboundPort":
                for portgroup in relation.findall('{http://schemas.ogf.org/nml/2013/05/base#}PortGroup'):
                    if switch != '':
                        db.add_switchports(topology.attrib['id'], switch.attrib['id'], portgroup.attrib['id'], cursor)
                    else:
                        db.add_switchports(topology.attrib['id'], switch, portgroup.attrib['id'], cursor)
    else:
        # print ("normal switch")
        # Add ports in the switch definition
        for relation in switch.findall('{http://schemas.ogf.org/nml/2013/05/base#}Relation'):
            if relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasInboundPort" or relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasOutboundPort":
                for portgroup in relation.findall('{http://schemas.ogf.org/nml/2013/05/base#}PortGroup'):
                    db.add_switchports(topology.attrib['id'], switch.attrib['id'], portgroup.attrib['id'], cursor)
                for port in relation.findall('{http://schemas.ogf.org/nml/2013/05/base#}Port'):
                    db.add_switchports(topology.attrib['id'], switch.attrib['id'], port.attrib['id'], cursor)


def switch(domains_topology, cursor):

    default_encoding = "http://schemas.ogf.org/nml/2012/10/ethernet"
    default_labeltype = "http://schemas.ogf.org/nml/2012/10/ethernet#vlan"

    for topology in domains_topology:
        has_service = 0
        for relation in topology[2][0].findall('{http://schemas.ogf.org/nml/2013/05/base#}Relation'):
            if relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasService":
                has_service = 1

                if relation[0].attrib['labelSwapping'] == 'true':
                    label_swapping = 'Yes'
                else:
                    label_swapping = 'No'

                try:
                    encoding = relation[0].attrib['encoding']
                except KeyError:
                    encoding = default_encoding

                try:
                    labeltype = relation[0].attrib['labelType']
                except KeyError:
                    labeltype = default_labeltype

                relation_port = relation[0].find('{http://schemas.ogf.org/nml/2013/05/base#}Relation')

                if relation_port:
                    if relation_port.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasInboundPort" or relation_port.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasOutboundPort":
                        switchtype = 'Standard'
                    else:
                        switchtype = 'Wildcard'
                else:
                    switchtype = 'Wildcard'

                db.add_switch(topology.attrib['id'], relation[0].attrib['id'], label_swapping, labeltype, switchtype, encoding, cursor)
                add_switchports(topology, relation[0], switchtype, labeltype, encoding, cursor)

        if has_service == 0:
            # Has no switching service defined -> defaults apply
            # print "\n" + topology.attrib['id'] + "  default"
            db.add_switch(topology.attrib['id'], '', 'No', 'http://schemas.ogf.org/nml/2012/10/ethernet#vlan', 'Default', 'http://schemas.ogf.org/nml/2012/10/ethernet', cursor)
            add_switchports(topology, '', 'default', default_labeltype, default_encoding, cursor)


def domainFromPort(domain_ports, port):

    for domain in domain_ports:
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            if alias[0] == port:
                return domain
    return ''


def topology_exists(domains_topology, topology):
    for domain in domains_topology:
        if topology in domain.attrib['id']:
            return 1
    return 0


def splitAndFind(domains_topology, port, num, cursor):
    domain_list = []
    splitted = port.split(':')

    while len(splitted) > num:
        splitted.pop()
    topology = ':'.join(splitted)

    for domain in domains_topology:
        if topology in domain.attrib['id']:
            domain_list.append(domain.attrib['id'])

    if len(domain_list) == 0:
        # The topology does not exist
        db.add_unknowntopology(topology, cursor)
        print "len(domain_list)"
        print topology
        # domain_list.append('')
        domain_list.append(topology)
        return domain_list
    else:
        return domain_list


def domainFromPortUnk(domains_topology, port, cursor):

    if '::' in port:
        splitted = port.split('::')[0]
        # Check if topology exists
        if not topology_exists(domains_topology, splitted):
            db.add_unknowntopology(splitted, cursor)
        return splitted
    elif ';;' in port:
        splitted = port.split(';;')[0]
        # Check if topology exists
        if not topology_exists(domains_topology, splitted):
            db.add_unknowntopology(splitted, cursor)
        return splitted
    else:
        domain_list = splitAndFind(domains_topology, port, 5, cursor)

        if len(domain_list) > 1:
            return splitAndFind(domains_topology, port, 6, cursor)[0]
        else:
            return domain_list[0]


def getAlias(domains_topology):

    domain_ports = defaultdict(list)
    num_alias = 0
    num_domains = 0

    for domain in domains_topology:
        num_domains += 1
        # Matrix for list -> src_port, dst_port, vlan range
        alias = []
        # curr_domain = ''

        for relation in domain[2][0].findall('{http://schemas.ogf.org/nml/2013/05/base#}Relation'):

            if relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasInboundPort" or relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasOutboundPort":

                for portgroup in relation.findall('{http://schemas.ogf.org/nml/2013/05/base#}PortGroup'):
                    # curr_domain = domainFromPort(portgroup.attrib['id'])
                    try:
                        if str(portgroup[1].attrib).find('isAlias'):
                            # alias.append([portgroup.attrib['id'], domainFromPort(portgroup[1][0].attrib['id']), portgroup[1][0].attrib['id'], portgroup[0].text])
                            alias.append([portgroup.attrib['id'], portgroup[1][0].attrib['id'], portgroup[0].text])
                            num_alias += 1
                    except IndexError:
                        pass

        # Add to structure
        if alias:
            domain_ports[domain.attrib['id']].append(alias)
            # print curr_domain
            # print alias
            # print "\n\n"

    print num_domains
    print num_alias

    return domain_ports


def findAlias(domain_ports, src_port, dst_port):

    for domain in domain_ports:
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            if alias[0] == dst_port and alias[1] == src_port:
                return 1
    return 0


def aliasVlans(domain_ports, src_port, dst_port, source_vlans):
    # print "Alias VLANS"

    for domain in domain_ports:
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            if alias[0] == dst_port and alias[1] == src_port:
                if alias[2] == source_vlans:
                    # print "range " + source_vlans + " match " + alias[3]
                    # print "src domain " + src_domain + " dst domain " + domain
                    return 1
                else:
                    # print "range " + source_vlans + " does not match " + alias[3]
                    # print "src domain " + src_domain + " dst domain " + domain
                    return alias[2]

    print "ALIASVLANS FAIL!!!"


def isAlias(domains_topology, cursor):
    num_alias = 0
    num_domains = 0

    domain_ports = getAlias(domains_topology)

    for domain in domain_ports:
        num_domains += 1
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            num_alias += 1
            if not findAlias(domain_ports, alias[0], alias[1]):

                db.add_isAlias(domain, alias[0], domainFromPortUnk(domains_topology, alias[1], cursor), alias[1], cursor)

            else:
                db.add_isAliasMatch(domain, alias[0], domainFromPort(domain_ports, alias[1]), alias[1], cursor)

                dst_vlans = aliasVlans(domain_ports, alias[0], alias[1], alias[2])
                if dst_vlans != 1:

                    db.add_isAliasVlan(domain, alias[0], domainFromPort(domain_ports, alias[1]), alias[1], alias[2], dst_vlans, cursor)
    print num_domains
    print num_alias


def topologyNsaMatch(domains_nsa, domains_topology, cursor):
    # Database: Topology | NSA | Status (0 - ok, 1 - nsa mismatch)

    nsastopologies = defaultdict(list)
    topologiesnsas = defaultdict()

    # Get topologies for each domain
    for domain in domains_nsa:
        for topologies in domain.iter('networkId'):
            nsastopologies[domain[0].text].append(topologies.text)

    # Get NSA for each topology
    for topology in domains_topology:
        topologiesnsas[topology.attrib['id']] = topology[0].text

    # Match Topology with NSA
    for topology, nsa in topologiesnsas.items():
        if topology in nsastopologies[nsa]:
            db.topologynsa(topology, nsa, 0, cursor)
        else:
            db.topologynsa(topology, nsa, 1, cursor)


def get_stps(stps_file):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, stps_file), 'r')
    stps = []

    for line in f:
        if '#' not in line.split(' ')[0]:
            parsed = line.split(' ')
            if len(parsed) == 4:
                stps.append(parsed)
    return stps


def make_reservation(data_plane_vlan, stp):
    server = "nsa.uvalight.net"
    #command = "onsa reserveprovision -r uvalight.net:2013:requester:onsa -p uvalight.net:2013:requester:onsa -s urn:ogf:network:uvalight.net:2013:topology:ps#" + data_plane_vlan.replace('\n', '') + " -d " + stp.replace('urn:ogf:network:', '') + " -j user=admin -u https://nsa.uvalight.net:9443/NSI/services/CS2 -a +10 -e +300 -l /etc/opennsa/certs/signed/nsa.uvalight.net-terenachain.pem -k /etc/opennsa/certs/signed/nsa.uvalight.net.key -i /etc/opennsa/certs -b 100 -x -z -v"
    command = "onsa reserveprovision -r uvalight.net:2013:requester:onsa -p netherlight.net:2013:nsa:safnari -s uvalight.net:2013:topology:ps#" + data_plane_vlan.replace('\n', '') + " -d " + stp.replace('urn:ogf:network:', '') + " -j user=urn:collab:person:surfguest.nl:39a1749e-617a-4f72-9b91-1031397b4454,token=56d5b8bb-489f-4134-99be-7ecf5fb01feb -u https://agg.netherlight.net:443/nsi-v2/ConnectionServiceProvider?wsdl -a +10 -e +300 -l /etc/opennsa/certs/signed/nsa.uvalight.net-terenachain.pem -k /etc/opennsa/certs/signed/nsa.uvalight.net.key -i /etc/opennsa/certs -b 100 -x -z -v"

    print command
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username="dashboard")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

    for line in ssh_stdout.readlines():
        print line
        if "provisioned" in line:
            print "reservation successful"
            ssh.close()
            return 1

    print "reservation failed"
    ssh.close()
    return 0


def path_test(stps_file, source_topology, cursor):
    # DP Connectivity: 0 - Success, 1 - Fail, 2 - Is_Source, 3 - Reservation_Fail
    stps = get_stps(stps_file)
    host_from = "nsa.uvalight.net"

    for topology, stp, host, data_plane_vlan in stps:
        if topology is source_topology:
            db.dp_connectivity(topology, 2, cursor)
        elif make_reservation(data_plane_vlan, stp):
            time.sleep(240)
            if remote_ping(host_from, host) != 0:
                db.dp_connectivity(topology, 0, cursor)
                print "connectivity"
            else:
                print "no connectivity"
                db.dp_connectivity(topology, 1, cursor)
            # Wait 1 minute before going to the next one
            time.sleep(120)
        else:
            print "reservation failed"
            db.dp_connectivity(topology, 3, cursor)
