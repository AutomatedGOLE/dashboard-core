#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard General Functions

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import os


def get_domains(dds_file, domain_type):
    domains = []

    for doc in dds_file:
        if domain_type in doc[1].text:
            domains.append(doc)

    return domains


def ping(host):
    result = 0

    for n in range(0, 2):
        if os.system("ping -c 1 " + host) == 0:
            result += 1

    return result
