#!/usr/bin/env python3.7
import time
import datetime
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
import dispatcher as di
import setupmodule as sm
import externalSourceAgent as es
import scheduler as sche
import scheduler1 as sche1
import csv
#import starter as s
import random
from lxml import etree as ET
import os
from xml.etree import ElementTree
from xml.dom import minidom
from shutil import copy2
from multiprocessing import Process, Pool
import asyncio
import threading
import pdb
import aiohttp_cors
import yaml
from yaml import Loader



def adaptor():

	with open("config.yml", 'r') as ymlfile:
	    cfg = yaml.load(ymlfile, Loader = Loader)
	port = cfg['config']['adaptor_port']
	jid = cfg['config']['adaptor']
	basejid = cfg['config']['userjid']
	simjid = cfg['config']['simulator']
	schejid = cfg['config']['scheduler']

	protocol_version = cfg['config']['protocol']
	simulation_dir = cfg['config']['simulation_dir']
	simulation_date = cfg['config']['date']
	hostname = cfg['config']['adaptor_address']
	password = cfg['config']['xmpp_password']
	if(protocol_version == "2.0"):
                print("Starting Adaptor")
                scheduler = sche.scheduler(basejid+"/"+jid, password)
                #scheduler.web.add_get("/gettime", scheduler.get_time, "message.html")
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
                'method' : 'GET',
                'path': '/getmessage',
                'handler' : scheduler.get_message,
                'name' : 'test'
                }
                route2 = {
                'method' : 'POST',
                'path' : '/postanswer',
                'handler' : scheduler.post_answer,
                'name' : 'test2'
                }
                route3 = {
                'method' : 'GET',
                'path' : '/gettime',
                'handler' : scheduler.get_time,
                'name' : 'test3'
                }
                cors.add(scheduler.web.app.router.add_route(method=route3['method'],path=route3['path'],handler=route3['handler'],name=route3['name']))
                cors.add(scheduler.web.app.router.add_route(method=route['method'],path=route['path'],handler=route['handler'],name=route['name']))
                cors.add(scheduler.web.app.router.add_route(method=route2['method'],path=route2['path'],handler=route2['handler'],name=route2['name']))

                scheduler.web.start(hostname=hostname,port=port)
                sc2.result()
	if(protocol_version == "1.0"):
                scheduler = sche1.scheduler(basejid+"/"+jid, password)
                #scheduler.web.add_get("/gettime", scheduler.get_time, "message.html")
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
                'method' : 'POST',
                'path' : '/postanswer',
                'handler' : scheduler.post_answer,
                'name' : 'test2'
                }
              
                cors.add(scheduler.web.app.router.add_route(method=route['method'],path=route['path'],handler=route['handler'],name=route['name']))
                scheduler.web.start(hostname=hostname,port=port)
                sc2.result()


def start_disp():
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader = Loader)
    simjid = cfg['config']['simulator']
    basejid = cfg['config']['userjid']
    password = cfg['config']['xmpp_password']

    dispatcher = di.dispatcher(basejid+"/"+simjid, password)
    future = dispatcher.start()



class MyThread(threading.Thread):
    abilit = 1
    def __init__(self):
        super(MyThread,self).__init__()



    def run(self):
        adaptor()
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader = Loader)
        port = cfg['config']['adaptor_port']
        jid = cfg['config']['adaptor']
        basejid = cfg['config']['userjid']
        simjid = cfg['config']['simulator']
        schejid = cfg['config']['scheduler']

        protocol_version = cfg['config']['protocol']
        simulation_dir = cfg['config']['simulation_dir']
        simulation_date = cfg['config']['date']
        hostname = cfg['config']['adaptor_address']
        password = cfg['config']['xmpp_password']
        abilit = 0

        external = es.ExternalSourceAgent(basejid+"/externalSource", password,simulation_dir+"/xml/buildingNeighborhood.xml",simulation_dir+"/xml/buildingLoad.xml")
        print(simulation_dir+"/xml/buildingNeighborhood.xml")
        ex = external.start()
        ex.result()
        external.stop()
        setupmodule = sm.setupModule(basejid+"/setupmodule", password)
        setupmodule.start()
        while(self.abilit == 0):
            None
        while(setupmodule.is_alive()):
            setupmodule.stop()


    def stop(self):
        b = setupmodule.stopService()
        setupmodule.add_behaviour(b)




if __name__ == "__main__":
    mythread = MyThread()
    start_disp()
    mythread.start()
    time.sleep(.9)
