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
        print '\nNSA: ' + domain[0].text
        for peers in domain.iter('peersWith'):
            domain_peers[domain[0].text].append(peers.text)
            print 'Peerswith: ' + peers.text
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
            if nsa not in domain_peers[peer]:
                print nsa + ' is peer with ' + peer + ', but the opposite does not happen'
                db.add_peerswithmismatches(nsa, peer, cursor)
            else:
                db.add_peerswith(nsa, peer, cursor)


def unknownPeersWidth(domains_nsa, domain_peers, cursor):
    domain_names = []
    print "\n\n"
    # Get domain names
    for domain in domains_nsa:
        domain_names.append(domain[0].text)

    for nsa, peers in domain_peers.items():
        # for each peer, check if it is a real domain
        for peer in peers:
            if peer not in domain_names:
                print nsa + ' is peer with an unknown NSA: ' + peer
                db.add_unknownpeer(nsa, peer, cursor)


# Find NSAs not referenced by any peerswith
def notRef(domain_peers, cursor):
    peer_list = []
    nsa_list = []

    # Get lists of NSAs and Peers
    for nsa, peers in domain_peers.items():
        nsa_list.append(nsa)
        for peer in peers:
            peer_list.append(peer)

    for nsa in nsa_list:
        if nsa not in peer_list:
            db.add_notref(nsa, cursor)
            print str(nsa) + ' not referenced by any peerswith'