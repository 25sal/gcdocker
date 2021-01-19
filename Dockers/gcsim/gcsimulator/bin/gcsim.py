#!/usr/bin/env python3.7
import time
from agents import xmppscheduler as sche, restscheduler as sche1, setup as es, manager as sm, \
    dispatcher as di
import aiohttp_cors
from utils.config import Configuration
import logging
import ptvsd
from daemons.prefab import run
import sys
import os 
import signal
import argparse




#####################################################################
#  This Method configure all the API to be exposed to the scheduler #
#  It depends on adotped protocol for the simulation                #
#####################################################################
def adaptor():
    port = Configuration.parameters['adaptor_port']
    jid = Configuration.parameters['adaptor']
    basejid = Configuration.parameters['userjid']

    protocol_version = Configuration.parameters['protocol']
    simulation_dir = Configuration.parameters['simulation_dir']
    logging.debug("simdir:" + simulation_dir)
    hostname = Configuration.parameters['adaptor_address']
    password = Configuration.parameters['xmpp_password']
    if protocol_version == "2.0":
        logging.info("Starting Adaptor")
        scheduler = sche.scheduler(basejid + "/" + jid, password)
        # scheduler.web.add_get("/gettime", scheduler.get_time, "message.html")
        # scheduler.web.add_post("/postanswer", scheduler.post_answer, "message2.html")
        sc2 = scheduler.start()
        cors = aiohttp_cors.setup(scheduler.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        })

        route = {
            'method': 'GET',
            'path': '/getmessage',
            'handler': scheduler.get_message,
            'name': 'test'
        }
        route2 = {
            'method': 'POST',
            'path': '/postanswer',
            'handler': scheduler.post_answer,
            'name': 'test2'
        }
        route3 = {
            'method': 'GET',
            'path': '/gettime',
            'handler': scheduler.get_time,
            'name': 'test3'
        }
        cors.add(
            scheduler.web.app.router.add_route(method=route3['method'], path=route3['path'], handler=route3['handler'],
                                               name=route3['name']))
        cors.add(
            scheduler.web.app.router.add_route(method=route['method'], path=route['path'], handler=route['handler'],
                                               name=route['name']))
        cors.add(
            scheduler.web.app.router.add_route(method=route2['method'], path=route2['path'], handler=route2['handler'],
                                               name=route2['name']))

        temp=scheduler.web.start(hostname=hostname, port=port)
        temp2=scheduler.web.is_started()
        sc2.result()
    if protocol_version == "1.0":
        scheduler = sche1.scheduler(basejid + "/" + jid, password)
        # scheduler.web.add_get("/gettime", scheduler.get_time, "message.html")
        #scheduler.web.add_post("/postanswer", scheduler.post_answer, "message2.html")
        sc2 = scheduler.start()
        cors = aiohttp_cors.setup(scheduler.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        })

        route = {
            'method': 'POST',
            'path': '/postanswer',
            'handler': scheduler.post_answer,
            'name': 'test2'
        }

        cors.add(
            scheduler.web.app.router.add_route(method=route['method'], path=route['path'], handler=route['handler'],
                                               name=route['name']))
        temp=scheduler.web.start(hostname=hostname, port=port)
        temp.result()
        temp2=scheduler.web.is_started()
        sc2.result()

############################################
#  This Method is used to start dispatcher #
############################################
def start_disp():
    simjid = Configuration.parameters['simulator']
    basejid = Configuration.parameters['userjid']
    password = Configuration.parameters['xmpp_password']
    dispatcher = di.dispatcher(basejid + "/" + simjid, password)
    future = dispatcher.start()
    future.result()
######################################################
#  This Method is used to start externalSource Agent #
######################################################
def setup_simulation():
    
    basejid = Configuration.parameters['userjid']
    simulation_dir = Configuration.parameters['current_sim_dir']
    password = Configuration.parameters['xmpp_password']
    external = es.ExternalSourceAgent(basejid + "/externalSource", password, simulation_dir + "/xml/buildingNeighborhood.xml",
                                          simulation_dir + "/xml/buildingLoad.xml")
    logging.debug(simulation_dir + "/xml/buildingNeighborhood.xml")
    external.simulation_setup()
    adaptor()


class GCDaemon(run.RunDaemon):
    @staticmethod
    def main():
        Configuration.load()
        logging.info("configuration loaded")
        di.MessageFactory.init_parameters()
        setup_simulation()
        logging.info("simulation runtime built")

        setup_jid = Configuration.parameters['userjid'] + "/setupmodule"
        password = Configuration.parameters['xmpp_password']
        start_disp()
        setupmodule = sm.setupModule(setup_jid, password)
        setupmodule.start()

    @staticmethod
    def run():
            GCDaemon.main()
            while True:
                try:
                    time.sleep(5)
                except KeyboardInterrupt:
                    break



if __name__ == "__main__":

    PIDFILE = '/home/gc/simulator/gcdaemon.pid'
    LOGFILE = '/home/gc/simulator/gcdaemon.log'
    logging.basicConfig(filename=LOGFILE, filemode='w', level=logging.INFO)
    daemon = GCDaemon(pidfile=PIDFILE)
    parser = argparse.ArgumentParser(description='gc simulator daemon')
    parser.add_argument('cmd', metavar='CMD', choices=['start', 'stop', 'restart', 'status'],
                        help='the daemon command ')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        default=False, help='wait for remote debugger')
    parser.add_argument('--nodaemon', dest='nodaemon', action='store_true',
                        default=False, help='starts as a standalone application')
    args = parser.parse_args()

    if 'start' == args.cmd:
        if args.debug:
            logging.info('debugger active')
            ptvsd.enable_attach(address=('0.0.0.0', 5678))
            ptvsd.wait_for_attach()
        if args.nodaemon:
            daemon.main()
        else:
            try:
                daemon.start()
            except:
                logging.error("start failed")

    elif 'stop' ==  args.cmd:
        print("Stopping ...")
        pf = open(PIDFILE,'r')
        pid = int(pf.read().strip())
        logging.info(pid)
        pf.close()
        os.killpg(os.getpgid(pid), signal.SIGHUP)
        os.killpg(os.getpgid(pid), signal.SIGKILL)
        os.kill(pid,signal.SIGKILL)
        #daemon.stop()

    elif 'restart' == sys.argv[1]:
        print("Restarting ...")
        daemon.restart()

    elif 'status' == args.cmd:
        try:
            pf = open(PIDFILE,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            print('GCDaemon is running as pid %s' % pid)
        else:
            print('GCDaemon is not running.')


