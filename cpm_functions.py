#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Control Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

from collections import defaultdict
import database as db

def peersWith(domains_nsa):
    domain_peers = defaultdict(list)

    for domain in domains_nsa:
        # print '\nNSA: ' + domain[0].text
        for peers in domain.iter('peersWith'):
            domain_peers[domain[0].text].append(peers.text)
        # print 'Peerswith: ' + peers.text
    return domain_peers


def noPeersWith(domains_nsa, cursor):
    for domain in domains_nsa:
        if not domain[2][0].findall('peersWith'):
            print domain[0].text + ' does not have peers'
            db.add_nopeers(domain[0].text, cursor)


def peersWithMismatches(domain_peers, cursor):
    for nsa, peers in domain_peers.items():
        # for each peer, check if the opposite is present
        for peer in peers:
            if not nsa in domain_peers[peer]:
                print nsa + ' is peer with ' + peer + ', but the opposite does not happen'
                db.add_peerswithmismatches(nsa, peer, cursor)
            else:
                db.add_peerswith(nsa, peer, cursor)


def unknownPeersWidth(domains_nsa, cursor):
    domain_names = []

    # Get domain names
    for domain in domains_nsa:
        domain_names.append(domain[0].text)

    for nsa, peers in peersWith(domains_nsa).items():
        # for each peer, check if it is a real domain
        for peer in peers:
            if not peer in domain_names:
                print nsa + ' is peer with an unknown NSA: ' + peer
                db.add_unknownpeer(nsa, peer, cursor)