#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Data Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

from collections import defaultdict
import database as db

isAlias_type = "http://schemas.ogf.org/nml/2013/05/base#isAlias"

def switch(domains_topology, cursor):

    for domain in domains_topology:
        for relation in domain[2][0].findall('{http://schemas.ogf.org/nml/2013/05/base#}Relation'):
            if relation.attrib['type'] == "http://schemas.ogf.org/nml/2013/05/base#hasService":

                if relation[0].attrib['labelSwapping'] == 'true':
                    db.switch(domain.attrib['id'], relation[0].attrib['id'], 'Yes', cursor)
                else:
                    db.switch(domain.attrib['id'], relation[0].attrib['id'], 'No', cursor)


def domainFromPort(domain_ports, port):

    for domain in domain_ports:
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            if alias[0] == port:
                return domain
    return ''


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


def topology_exists(domain_ports, topology):
    for domain in domain_ports:
        if str(topology) in domain:
            return 1
    return 0


# Review this
def domainFromPortUnk(domain_ports, port, cursor):

    if '::' in port:
        splitted = port.split('::')[0]
        # Check if topology exists
        if not topology_exists(domain_ports, splitted):
            db.add_unknowntopology(splitted, cursor)
        return splitted[0]
    elif ';;' in port:
        splitted = port.split(';;')[0]
        # Check if topology exists
        if not topology_exists(domain_ports, splitted):
            db.add_unknowntopology(splitted, cursor)
        return splitted[0]
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
