#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard General Functions

__author__ = 'Daniel Romão - d.f.romao@uva.nl'

import os
import paramiko


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

    # print result

    return result


def remote_ping(host_from, host_to):
    command = "ping -c 1 " + host_to

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_from, username="dashboard")

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)

    for line in ssh_stdout.readlines():
        print line
        if ", 0% packet loss" in line:
            ssh.close()
            return 1

    ssh.close()
    return 0
