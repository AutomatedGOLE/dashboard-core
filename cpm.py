#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Control Plane Monitoring

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import xml.etree.cElementTree as ET
import requests
import general_functions as gf
import cpm_functions as cpmf

topo_v2 = 'vnd.ogf.nsi.topology.v2+xml'
nsa = 'vnd.ogf.nsi.nsa.v1+xml'


def start_cpm():
    dds_url = "http://agg.netherlight.net/dds/documents"

    domains_topology = []
    domains_nsa = []

    req = requests.get(dds_url)

    dds_file = ET.XML(req.text)

    domains_topology = gf.get_domains(dds_file, topo_v2)
    domains_nsa = gf.get_domains(dds_file, nsa)

    cpmf.peersWithMismatches(cpmf.peersWith(domains_nsa))
    print '\n'
    cpmf.noPeersWith(domains_nsa)
    print '\n'
    cpmf.unknownPeersWidth(domains_nsa)
