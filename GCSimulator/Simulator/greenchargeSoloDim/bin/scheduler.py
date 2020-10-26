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

    async def get_message(self, request):
        global dispatched
        global simulated_time

        if(dispatched.empty()):
                res = {"sim_id": "demo", "time": str(simulated_time), "message": "no new message"}

                return aioweb.json_response(res)
        nextmsg = dispatched.get_nowait()
		
        print(nextmsg["message"])
        dictB = json.loads(nextmsg["message"])
        if(nextmsg["time"] != "0"):
                simulated_time = nextmsg["time"]

        dictA = {"sim_id": "demo", "time": str(simulated_time)}
        def merge_two_dicts(x, y):
            z = x.copy()   # start with x's keys and values
            z.update(y)    # modifies z with y's keys and values & returns None
            return z
        z = merge_two_dicts(dictA, dictB)


        return aioweb.json_response(z)

    async def get_time(self, request):
        global simulated_time
        res = {"sim_id": '"demo"', "time": str(simulated_time)}
        return aioweb.json_response(res)

    async def post_answer(self,request):
        data = await request.post()
        global mexToSend
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader = Loader)
            date = cfg['config']['date'] + " 00:00:00"
            path = cfg['config']['simulation_dir']
        try:
                message = data['response']
                parsed_json = (json.loads(message))
                sub = parsed_json['subject']
                if(sub == "ASSIGNED_START_TIME"):

                        id_load = parsed_json['id']
                        ast = parsed_json['ast']
                        producer = parsed_json['producer']
                        mex = sub + " ID " + id_load + " " + ast + " PV " + producer
                        mexToSend.put_nowait(mex)

                elif(sub == "HC_PROFILE"):
                        id_load = parsed_json['id']
                        input_file = data['thefile'].file
                        file_name = data['thefile'].filename
                        print(file_name)
                        if input_file:
                                f = open(path+"/Simulations/"+es.mydir+"/output/HC/"+id_load+".csv", "w+")
                                for line in input_file:
                                      f.write(line.decode("utf-8"))
                elif(sub == "EV_PROFILE"):
                        id_load = parsed_json['id']
                        input_file = data['thefile'].file
                        file_name = data['thefile'].filename
                        print(file_name)
                        if input_file:
                                f = open(path+"/Simulations/"+es.mydir+"/output/EV/"+id_load+".csv", "w+")
                                for line in input_file:
                                      f.write(line.decode("utf-8"))

        except Exception as e:
                print(e)
                print("not valid request")
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
            global dispatched
            global interval
            global last_object_type
            global nextInterval
            global mexToSend
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
            msg = await self.receive(timeout=5)
            print(msg)
            if(isinstance(msg, type(None))):
                   for i in range(mexToSend.qsize()):
                             mex = Message(to=basejid+"/"+simjid)
                             message = mexToSend.get_nowait()
                             mex.body = message
                             await self.send(mex)
            else:
                    #dispatched.put_nowait({"time": msg.metadata, "message": msg.body})
                    try:
                        dictB = json.loads(msg.body)
                        last_object_type = dictB['message']['subject']
                        print(last_object_type)
                        global oldStart
                        print("sonoOqui")
                        if(oldStart == 0):
                            oldStart = int(msg.metadata)
                        if(int(msg.metadata) < int(oldStart) + 900):
                            print("sonoqui")
                            print(last_object_type)
                            dispatched.put_nowait({"time": msg.metadata, "message": msg.body})
                            if(last_object_type == "LOAD" and interval == nextInterval):
                                mex = Message(to=basejid+"/"+simjid)
                                message = "AckMessage"
                                mex.body = message
                                await self.send(mex)
                            elif(last_object_type == "LOAD" and interval != nextInterval and mexToSend.qsize() != 0):
                                for i in range(mexToSend.qsize()):
                                     mex = Message(to=basejid+"/"+simjid)
                                     message = mexToSend.get_nowait()
                                     mex.body = message
                                     await self.send(mex)
                                nextInterval = interval
                            elif(last_object_type == "LOAD" and interval != nextInterval and mexToSend.qsize() == 0):
                                msg = Message(to=basejid+"/"+simjid)
                                message = "AckMessage"
                                msg.body = message
                                print(message)
                                await self.send(msg)
                                nextInterval = interval
                        else:
                            print("sono quiD")
                            dispatched.put_nowait({"time": msg.metadata, "message": msg.body})
                            if(last_object_type == "LOAD" and mexToSend.qsize() != 0):
                                print("sono quiE")
                                for i in range(mexToSend.qsize()):
                                     mex = Message(to=basejid+"/"+simjid)
                                     message = mexToSend.get_nowait()
                                     mex.body = message
                                     print(message)
                                     await self.send(mex)
                                interval += 1
                                nextInterval = interval
                            elif(last_object_type == "LOAD" and mexToSend.qsize() == 0):
                                print("sono quiF")
                                mex = Message(to=basejid+"/"+simjid)
                                message = "AckMessage"
                                mex.body = message
                                print(message)
                                await self.send(mex)
                                nextInterval = interval
                            else:
                                interval += 1
                            oldStart = msg.metadata
                    except Exception as e:
                        print(e)
