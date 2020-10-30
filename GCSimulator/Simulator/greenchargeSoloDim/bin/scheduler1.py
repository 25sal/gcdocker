import time

from multidict import MultiDict
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime,timedelta
import queue
import os
import asyncio
from aiohttp import web
from shutil import copyfileobj
global dispatched
import aiohttp_cors
from aiohttp import web as aioweb
import yaml
from yaml import Loader
import json
import externalSourceAgent as es
from shutil import copy2


dispatched = queue.Queue()
mexToSend = queue.Queue()
simulated_time = 0
last_object_type = 0
interval = 0
nextInterval = 0
oldStart = 0


class scheduler(Agent):

    async def setup(self):
        simulated_time = 0
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
        base_url = "http://"+hostname+":5280/files"
        start_at = datetime.now() + timedelta(seconds=3)
        global interval
        interval = 0
        global oldStart
        oldStart = 0
        Behaviour2 = self.consumeEvent2(1, start_at=start_at)
        self.add_behaviour(Behaviour2)
        #self.traces.reset()



    async def post_answer(self,request):
        data = await request.post()
        global mexToSend
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader = Loader)
            date = cfg['config']['date'] + " 00:00:00"
            path = cfg['config']['simulation_dir']
            simdir = cfg['config']['simulation']
            user = cfg['config']['userjid'].split('@')[0]
        message = data['response']
        parsed_json = (json.loads(message))
        sub = parsed_json['subject']
        f = open(path +"file222.csv", 'w')
        f.write(sub)
        f.close
        

        print("riceveid")

        if(sub == "ASSIGNED_START_TIME"):
                id_load = parsed_json['id']
                ast = parsed_json['ast']
                producer = parsed_json['producer']
                mex = sub + " ID " + id_load + " " + ast + " PV " + producer
                mexToSend.put_nowait(mex)
        elif(sub == "HC_PROFILE"):
                id_load = parsed_json['id']
                input_file = data['csvfile'].file
                file_name = data['csvfile'].filename
                print(file_name)
                if input_file:
                    f = open(path+"/"+simdir+"/Simulations/"+es.mydir+"/output/HC/"+id_load+".csv", "w+")
                    for line in input_file:
                        f.write(line.decode("utf-8"))
                copy2(path+"/"+simdir+"/Simulations/"+es.mydir+"/output/HC/"+id_load+".csv","/home/gcdemo/public_html/Simulations/"+user+"/"+es.mydir+"/output")
                
        elif(sub == "EV_PROFILE"):
                id_load = parsed_json['id']
                input_file = data['csvfile'].file
                file_name = data['csvfile'].filename
                print(file_name)
                print(path+simdir+"/Simulations/"+es.mydir+"/output/EV/"+id_load+".csv")
                if input_file:
                    f = open(path+"/"+simdir+"/Simulations/"+es.mydir+"/output/EV/"+id_load+".csv", "w+")
                    for line in input_file:
                        f.write(line.decode("utf-8"))
                copy2(path+"/"+simdir+"/Simulations/"+es.mydir+"/output/EV/"+id_load+".csv","/home/gcdemo/public_html/Simulations/"+user+"/"+es.mydir+"/output")




        response = web.StreamResponse(
        status=200,
        reason='OK'
        )

        return response


    class consumeEvent2(PeriodicBehaviour):

        async def onstart(self):
            print("A ConsumeEvent queue is Starting...")
        async def run(self):
            print("adaptor is running")

