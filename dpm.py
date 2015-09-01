#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Control Data Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import requests
import xml.etree.cElementTree as ET
import general_functions as gf

topo_v2 = 'vnd.ogf.nsi.topology.v2+xml'
nsa = 'vnd.ogf.nsi.nsa.v1+xml'

def start_dpm():
    dds_url = "http://agg.netherlight.net/dds/documents"

    req = requests.get(dds_url)

    dds_file = ET.XML(req.text)

    domains_topology = gf.get_domains(dds_file, topo_v2)
    domains_nsa = gf.get_domains(dds_file, nsa)

    # Connect to DB
    db_connection = db.database_start()
    cursor =  db_connection.cursor()

    # Clean DB
    db.table_clear(['isalias'], cursor)