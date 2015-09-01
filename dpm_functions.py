#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Data Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

from collections import defaultdict
import database as db

def isAlias(domains_nsa):

    domain_ports = defaultdict(list)

    for domain in domains_nsa:

        for peers in domain.iter('peersWith'):
            domain_peers[domain[0].text].append(peers.text)
        # print 'Peerswith: ' + peers.text
    return domain_ports