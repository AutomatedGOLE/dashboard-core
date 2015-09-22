#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Data Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

from collections import defaultdict
import database as db

isAlias_type = "http://schemas.ogf.org/nml/2013/05/base#isAlias"


def domainFromPort(port):
    splitted = port.split(':')
    # Removes port part
    splitted.pop()
    return ':'.join(splitted)


def getAlias(domains_topology):

    domain_ports = defaultdict(list)
    num_alias = 0
    num_domains=0

    for domain in domains_topology:
        num_domains += 1
        # Matrix for list -> src_port, dst_domain, dst_port
        alias = []

        for relation in domain[2][0].findall('{http://schemas.ogf.org/nml/2013/05/base#}Relation'):

            if relation[0].find('{http://schemas.ogf.org/nml/2013/05/base#}Relation') and str(relation[0][1].attrib).find('isAlias'):
                alias.append([relation[0].attrib['id'], domainFromPort(relation[0][1][0].attrib['id']), relation[0][1][0].attrib['id']])
                num_alias += 1

        # Add to structure
        domain_ports[domainFromPort(relation[0].attrib['id'])].append(alias)

    print num_domains
    print num_alias
    return domain_ports


def findAlias(domain_ports, src_domain, src_port, dst_port):

    for domain in domain_ports:
        if domain != src_domain:
            alias_list = domain_ports[domain][0]
            for alias in alias_list:
                if alias[0] == dst_port and alias[2] == src_port:
                    return 1
    return 0


def isAlias(domain_ports, cursor):
    num_alias = 0
    num_domains = 0
    # Iterate domains
    for domain in domain_ports:
        num_domains += 1
        alias_list = domain_ports[domain][0]
        for alias in alias_list:
            num_alias += 1
            if not findAlias(domain_ports, domain, alias[0], alias[2]):
                 # Add mismatch to database
                 db.add_isAlias(domain, alias[0], alias[1], alias[2], cursor)
                 print "Found isAlias mismatch: Source: " + alias[0] + " Destination: " + alias[2]
            else:
                 print "Found isAlias MATCH: Source: " + alias[0] + " Destination: " + alias[2]
    print num_domains
    print num_alias