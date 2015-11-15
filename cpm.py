#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Control Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import xml.etree.cElementTree as ET
import requests
import general_functions as gf
import cpm_functions as cpmf
import database as db

topo_v2 = 'vnd.ogf.nsi.topology.v2+xml'
nsa = 'vnd.ogf.nsi.nsa.v1+xml'


def start_cpm():
    dds_url = "http://agg.netherlight.net/dds/documents"

    req = requests.get(dds_url)

    dds_file = ET.XML(req.text)

    domains_topology = gf.get_domains(dds_file, topo_v2)
    domains_nsa = gf.get_domains(dds_file, nsa)

    # Connect to DB
    db_connection = db.database_start()
    cursor = db_connection.cursor()

    # Clean DBs
    db.table_clear(['peerswithmismatches', 'peerswith', 'nopeers', 'unknownpeers', 'notref', 'cp_connectivity', 'nsastopologies', 'peersroles'], cursor)

    domain_peers = cpmf.peersWith(domains_nsa)

    cpmf.peersWithMismatches(domain_peers, cursor)
    cpmf.noPeersWith(domains_nsa, cursor)
    cpmf.unknownPeersWidth(domains_nsa, domain_peers, cursor)
    cpmf.notRef(domain_peers, cursor)
    # cpmf.cp_connectivity(domains_nsa, cursor)
    cpmf.nsasTopologiesMatch(domains_nsa, domains_topology, cursor)
    cpmf.peersroles(domains_nsa, cursor)

    # Commit changes and close connection
    db.database_end(db_connection)
