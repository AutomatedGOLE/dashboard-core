#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Data Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

from collections import defaultdict
import database as db

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
                        switchtype = 'standard'
                    else:
                        switchtype = 'wildcard'
                else:
                    switchtype = 'wildcard'

                # print "\n" + topology.attrib['id'] + "  " + relation[0].attrib['id'] + "  " + label_swapping + "  " + labeltype + "  " + switchtype + "  " + encoding
                db.add_switch(topology.attrib['id'], relation[0].attrib['id'], label_swapping, labeltype, switchtype, encoding, cursor)
                add_switchports(topology, relation[0], switchtype, labeltype, encoding, cursor)

        if has_service == 0:
            # Has no switching service defined -> defaults apply
            # print "\n" + topology.attrib['id'] + "  default"
            db.add_switch(topology.attrib['id'], '', 'No', 'http://schemas.ogf.org/nml/2012/10/ethernet#vlan', 'default', 'http://schemas.ogf.org/nml/2012/10/ethernet', cursor)
            add_switchports(topology, '', 'default', default_labeltype, default_encoding, cursor)


def domainFromPort(domain_ports, port):

    for domain in domain_ports:
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            if alias[0] == port:
                return domain
    return ''


def topology_exists(domain_ports, topology):
    for domain in domain_ports:
        if str(topology) in domain:
            return 1
    return 0


def splitAndFind(domain_ports, port, num, cursor):
    domain_list = []
    splitted = port.split(':')

    while len(splitted) > num:
        splitted.pop()
    topology = ':'.join(splitted)

    for domain in domain_ports:
        if topology in domain:
            domain_list.append(domain)

    if len(domain_list) == 0:
        # The topology does not exist
        db.add_unknowntopology(topology, cursor)
        # domain_list.append('')
        domain_list.append(topology)
        return domain_list
    else:
        return domain_list


# Review this
def domainFromPortUnk(domain_ports, port, cursor):

    if '::' in port:
        splitted = port.split('::')[0]
        # Check if topology exists
        if not topology_exists(domain_ports, splitted):
            db.add_unknowntopology(splitted, cursor)
        return splitted
    elif ';;' in port:
        splitted = port.split(';;')[0]
        # Check if topology exists
        if not topology_exists(domain_ports, splitted):
            db.add_unknowntopology(splitted, cursor)
        return splitted
    else:
        domain_list = splitAndFind(domain_ports, port, 5, cursor)

        if len(domain_list) > 1:
            return splitAndFind(domain_ports, port, 6, cursor)[0]
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


def isAlias(domain_ports, cursor):
    num_alias = 0
    num_domains = 0

    for domain in domain_ports:
        num_domains += 1
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            num_alias += 1
            if not findAlias(domain_ports, alias[0], alias[1]):

                db.add_isAlias(domain, alias[0], domainFromPortUnk(domain_ports, alias[1], cursor), alias[1], cursor)

            else:
                db.add_isAliasMatch(domain, alias[0], domainFromPort(domain_ports, alias[1]), alias[1], cursor)

                dst_vlans = aliasVlans(domain_ports, alias[0], alias[1], alias[2])
                if dst_vlans != 1:

                    db.add_isAliasVlan(domain, alias[0], domainFromPort(domain_ports, alias[1]), alias[1], alias[2], dst_vlans, cursor)
    print num_domains
    print num_alias


def topologyNsaMatch(domains_nsa, domains_topology, cursor):
    # Database: Topology | NSA | Status (0 - ok, 1 - nsa mismatch)

    # Make dic to topologies on NSAs
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
