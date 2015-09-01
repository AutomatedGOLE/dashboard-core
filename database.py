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