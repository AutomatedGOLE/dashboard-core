#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Database Functions

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import mysql.connector as db


def database_start():
    db_connection = db.connect(user='monitor', password='monitor_pass', database='dashboard')
    return db_connection


def database_end(db_connection):
    db_connection.commit()
    db_connection.close()


def table_clear(tables, cursor):
    for table in tables:
        query = "TRUNCATE TABLE " + table
        cursor.execute(query)


def add_peerswithmismatches(nsa1, nsa2, cursor):
    query = "INSERT INTO peerswithmismatches (nsa1, nsa2) VALUES (\"" + nsa1 + "\", \"" + nsa2 + "\")"
    cursor.execute(query)


def add_peerswith(nsa1, nsa2, cursor):
    query = "INSERT INTO peerswith (nsa1, nsa2) VALUES (\"" + nsa1 + "\", \"" + nsa2 + "\")"
    cursor.execute(query)


def add_nopeers(nsa, cursor):
    query = "INSERT INTO nopeers (nsa) VALUES (\"" + nsa + "\")"
    cursor.execute(query)


def add_unknownpeer(nsa, unknown, cursor):
    query = "INSERT INTO unknownpeers (nsa, unknown) VALUES (\"" + nsa + "\", \"" + unknown + "\")"
    cursor.execute(query)


def add_isAlias(src_domain, src_port, dst_domain, dst_port, cursor):
    query = "INSERT INTO isalias (src_domain, src_port, dst_domain, dst_port) VALUES (\"" + src_domain + "\", \"" + src_port + "\", \"" + dst_domain + "\", \"" + dst_port + "\")"
    cursor.execute(query)


def add_isAliasMatch(src_domain, src_port, dst_domain, dst_port, cursor):
    query = "INSERT INTO isaliasmatch (src_domain, src_port, dst_domain, dst_port) VALUES (\"" + src_domain + "\", \"" + src_port + "\", \"" + dst_domain + "\", \"" + dst_port + "\")"
    cursor.execute(query)


def add_isAliasVlan(src_domain, src_port, dst_domain, dst_port, src_vlans, dst_vlans, cursor):
    query = "INSERT INTO isaliasvlans (src_domain, src_port, src_vlans, dst_domain, dst_port, dst_vlans) VALUES (\"" + src_domain + "\", \"" + src_port + "\", \"" + src_vlans + "\", \"" + dst_domain + "\", \"" + dst_port + "\", \"" + dst_vlans + "\")"
    cursor.execute(query)


def add_notref(nsa, cursor):
    query = "INSERT INTO notref (nsa) VALUES (\"" + nsa + "\")"
    cursor.execute(query)


def cp_connectivity(nsa, result, cursor):
    query = "INSERT INTO cp_connectivity (nsa, result) VALUES (\"" + nsa + "\", \"" + str(result) + "\")"
    cursor.execute(query)


def dp_connectivity(topology, result, cursor):
    query = "INSERT INTO dp_connectivity (topology, result) VALUES (\"" + topology + "\", \"" + str(result) + "\")"
    cursor.execute(query)


def add_switch(topology, service, labelswapping, labeltype, switchtype, encoding, cursor):
    query = "INSERT INTO switch (topology, service, labelswapping, labeltype, switchtype, encoding) VALUES (\"" + topology + "\", \"" + service + "\", \"" + labelswapping +"\", \"" + labeltype + "\", \"" + switchtype + "\", \"" + encoding + "\")"
    cursor.execute(query)


def add_switchports(topology, service, port, cursor):
    query = "INSERT INTO switchports (topology, service, port) VALUES (\"" + topology + "\", \"" + service + "\", \"" + port + "\")"
    cursor.execute(query)


def add_unknowntopology(topology, cursor):
    query = "INSERT IGNORE INTO unknowntopologies (topology) VALUES (\"" + str(topology) + "\")"
    cursor.execute(query)


def nsastopologies(nsa, topology, status, cursor):
    query = "INSERT INTO nsastopologies (nsa, topology, status) VALUES (\"" + nsa + "\", \"" + topology + "\", \"" + str(status) + "\")"
    cursor.execute(query)


def topologynsa(topology, nsa, status, cursor):
    query = "INSERT INTO topologynsa (topology, nsa, status) VALUES (\"" + topology + "\", \"" + nsa + "\", \"" + str(status) + "\")"
    cursor.execute(query)


def add_peersroles(nsa, role, cursor):
    query = "INSERT INTO peersroles (nsa, role) VALUES (\"" + nsa + "\", \"" + role + "\")"
    cursor.execute(query)