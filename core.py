#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Core

__author__ = 'Daniel Romão - d.f.romao@uva.nl'
import io
import os
import sys
import json
import atexit
import requests
import socket
import subprocess
from time import sleep
from threading import Thread
import xml.etree.cElementTree as ET
from collections import defaultdict

topo_v2 = 'vnd.ogf.nsi.topology.v2+xml'
nsa = 'vnd.ogf.nsi.nsa.v1+xml'






# Main
if __name__ == '__main__':

	# dds_url = "http://agg.netherlight.net/dds/documents"

	# domains_topology = []
	# domains_nsa = []

	# req = requests.get(dds_url)

	# dds_file = ET.XML(req.text)

	# domains_topology = get_domains(dds_file, topo_v2)
	# domains_nsa = get_domains(dds_file, nsa)


	

	#Debug
	# for domain in domains_nsa:
	# 	print domain[2][0].attrib

	

	#print peersWith(domains_nsa).items()

	# peersWithMismatches(peersWith(domains_nsa))
	# print '\n'
	# noPeersWith(domains_nsa)
	# print '\n'
	# unknownPeersWidth(domains_nsa)
