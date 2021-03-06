#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Control Data Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import requests
import xml.etree.cElementTree as ET
import general_functions as gf
import dpm_functions as dpmf
import database as db

topo_v2 = 'vnd.ogf.nsi.topology.v2+xml'
nsa = 'vnd.ogf.nsi.nsa.v1+xml'

def start_dpm(stps_file, source_topology, path_test):
    dds_url = "http://agg.netherlight.net/dds/documents"

    req = requests.get(dds_url)

    dds_file = ET.XML(req.text)

    domains_topology = gf.get_domains(dds_file, topo_v2)
    domains_nsa = gf.get_domains(dds_file, nsa)

    # Connect to DB
    db_connection = db.database_start()
    cursor = db_connection.cursor()

    # Trigger data plane testing
    if path_test:
        db.table_clear(['dp_connectivity'], cursor)
        dpmf.path_test(stps_file, source_topology, cursor)

    # Clean tables
    db.table_clear(['isalias', 'isaliasvlans', 'isaliasmatch', 'switch', 'unknowntopologies', 'topologynsa', 'switchports'], cursor)

    # Find isAlias mismatches
    dpmf.isAlias(domains_topology, cursor)

    dpmf.topologyNsaMatch(domains_nsa, domains_topology, cursor)

    # Find Switch settings
    dpmf.switch(domains_topology, cursor)

    # Commit changes and close connection
    db.database_end(db_connection)
