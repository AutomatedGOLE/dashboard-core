#!/usr/bin/python
# -*- coding: utf-8 -*- 
#
# AutoGOLE Dashboard Core

__author__ = 'Daniel Romão - d.f.romao@uva.nl'
import cpm
import dpm
import logging
import time
import os
import core_functions as cf
from daemon import runner


class Dashboard():

    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = 'dashboard.out'
        self.stderr_path = 'dashboard.err'
        self.pidfile_path = '/var/run/dashboard/dashboard.pid'
        self.pidfile_timeout = 5

    def run(self):
        while True:

            logger.info("AutoGOLE Dashboard Starting")

            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            config_file = os.path.join(__location__, 'dashboard.conf')

            # Read configuration file
            config = cf.parse_config(config_file)

            refresh = float(config.get('refresh'))
            path_testing_refresh = float(config.get('path_testing_refresh'))
            logger.debug("Refresh time = " + str(refresh) + " minutes")

            logger.info("Starting control plane checks")
            cpm.start_cpm()
            logger.info("Starting data plane checks")
            dpm.start_dpm()

            logger.info("Starting path segment checks")


            time.sleep(refresh * 60)

            # logger.debug("Debug message")
            # logger.info("Info message")
            # logger.warn("Warning message")
            # logger.error("Error message")


app = Dashboard()

logger = logging.getLogger("DashboardLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("dashboard.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(app)
daemon_runner.daemon_context.files_preserve = [handler.stream]
daemon_runner.do_action()
