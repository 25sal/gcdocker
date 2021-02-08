#
# Copyright (c) 2019-2020 by University of Campania "Luigi Vanvitelli".
# Developers and maintainers: Salvatore Venticinque, Dario Branco.
# This file is part of GreenCharge
# (see https://www.greencharge2020.eu/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
RESTScheduler
=======================================
This agent create a REST server in order to communicate with REST schedulers.
"""
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from datetime import datetime,timedelta
import queue
from aiohttp import web
from aiohttp import web as aioweb
import json
from shutil import copy2
from utils.config import Configuration
import logging
LOGFILE = '/home/gc/simulator/gcdaemon.log'

# logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

##########################################
#  Adaptor used for the rest protocol    #
##########################################
class scheduler(Agent):
    '''
    Adaptor used for the REST protocol  .
    Args:
        Agent: The spade Agent.
    '''
    ###############################
    #  Initializing Parameters   #
    ###############################
    async def setup(self):
        self.start_at = datetime.now() + timedelta(seconds=3)
        self.interval = 0
        self.nextInterval = 0
        self.oldStart = 0
        self.mexToSend = queue.Queue()
        self.dispatched = queue.Queue()
        self.simulated_time = 0
        self.last_object_type = 0
        Behaviour2 = self.consumeEvent2(1, start_at=self.start_at)
        self.add_behaviour(Behaviour2)
        #self.traces.reset()

    ################################################################################
    #  GET API used by schedulers to get a simulation message.                     #
    #  It consume an object from the dispatched message queue and return a json    #
    ################################################################################
    async def get_message(self, request):
        """
        GET API used by schedulers to get a message.
        Args:
            request: the REST request
        """
        if self.dispatched.empty():
                res = {"sim_id": "demo", "time": str(self.simulated_time), "message": "no new message"}

                return aioweb.json_response(res)
        nextmsg = self.dispatched.get_nowait()

        logging.info(nextmsg["message"])
        dictB = json.loads(nextmsg["message"])
        if(nextmsg["time"] != "0"):
                self.simulated_time = nextmsg["time"]

        dictA = {"sim_id": "demo", "time": str(self.simulated_time)}
        def merge_two_dicts(x, y):
            z = x.copy()   # start with x's keys and values
            z.update(y)    # modifies z with y's keys and values & returns None
            return z
        z = merge_two_dicts(dictA, dictB)
        return aioweb.json_response(z)

    #############################################################
    #  GET API used by scheduler to get simulation time json    #
    #############################################################
    async def get_time(self, request):
        """
        GET API used by schedulers to get simulation time.
        Args:
            request: the REST request
        """
        res = {"sim_id": '"demo"', "time": str(self.simulated_time)}
        return aioweb.json_response(res)


    #######################################################################
    #  POST API used by schedulers to post a timeseries.                  #
    #  It recieve a file and write the content in simulation directory    #
    #######################################################################
    async def post_answer(self,request):
        """
        POST API used by schedulers to post an answer to the dispatcher.
        It recieve a file and write the content in simulation directory or a general message.
        Args:
            request: the REST request
        """
        data = await request.post()
        path = Configuration.parameters['simulation_dir']
        simdir = Configuration.parameters['simulation']

        try:
            message = data['response']
            parsed_json = (json.loads(message))
            sub = parsed_json['subject']
            if(sub == "ASSIGNED_START_TIME"):

                        id_load = parsed_json['id']
                        ast = parsed_json['ast']
                        producer = parsed_json['producer']
                        mex = sub + " " + id_load + " " + ast + " " + producer
                        self.mexToSend.put_nowait(mex)

            elif sub == "HC_PROFILE":
                    id_load = parsed_json['id']
                    input_file = data['csvfile'].file
                    file_name = data['csvfile'].filename
                    logging.info(file_name)
                    if input_file:
                            f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+id_load+".csv", "w+")
                            for line in input_file:
                                  f.write(line.decode("utf-8"))
                    copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+id_load+".csv","/var/www/Simulations/demo/"+Configuration.parameters['user_dir']+"/output")

            elif sub == "EV_PROFILE":
                    id_load = parsed_json['id']
                    input_file = data['csvfile'].file
                    file_name = data['csvfile'].filename
                    logging.info(file_name)
                    if input_file:
                            f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+id_load+".csv", "w+")
                            for line in input_file:
                                  f.write(line.decode("utf-8"))
                    copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+id_load+".csv","/var/www/Simulations/demo/"+Configuration.parameters['user_dir']+"/output")

        except Exception as e:
            logging.info(e)
            logging.info("not valid request")
        response = web.StreamResponse(
        status=200,
        reason='OK'
        )

        return response

    ##################################################
    #  This Behaviour periodically checks if the     #
    #  dispatcher has processed other messages to be #
    #  placed in the dispatched queue.               #
    ##################################################

    class consumeEvent2(PeriodicBehaviour):

        async def onstart(self):
            logging.info("A ConsumeEvent queue is Starting...")

        async def run(self):
            logging.info("adaptor is running")
            basejid = Configuration.parameters['userjid']
            simjid = Configuration.parameters['simulator']
            msg = await self.receive(timeout=5)
            logging.info(msg)
            if isinstance(msg, type(None)):
                   for i in range(self.agent.mexToSend.qsize()):
                             mex = Message(to=basejid+"/"+simjid)
                             message = self.agent.mexToSend.get_nowait()
                             mex.body = message
                             await self.send(mex)
            else:
                    # dispatched.put_nowait({"time": msg.metadata, "message": msg.body})
                    try:
                        dictB = json.loads(msg.body)
                        self.agent.last_object_type = dictB['message']['subject']
                        if self.agent.oldStart == 0:
                            self.agent.oldStart = int(msg.metadata)
                        if int(msg.metadata) < int(self.agent.oldStart) + 900:
                            self.agent.dispatched.put_nowait({"time": msg.metadata, "message": msg.body})
                            if self.agent.last_object_type == "LOAD" and self.agent.interval == self.agent.nextInterval:
                                mex = Message(to=basejid+"/"+simjid)
                                message = "AckMessage"
                                mex.body = message
                                await self.send(mex)
                            elif self.agent.last_object_type == "LOAD" and self.agent.interval != self.agent.nextInterval and self.agent.mexToSend.qsize() != 0:
                                for i in range(self.agent.mexToSend.qsize()):
                                     mex = Message(to=basejid+"/"+simjid)
                                     message = self.agent.mexToSend.get_nowait()
                                     mex.body = message
                                     await self.send(mex)
                                self.agent.nextInterval = self.agent.interval
                            elif self.agent.last_object_type == "LOAD" and self.agent.interval != self.agent.nextInterval and self.agent.mexToSend.qsize() == 0:
                                msg = Message(to=basejid+"/"+simjid)
                                message = "AckMessage"
                                msg.body = message
                                await self.send(msg)
                                self.agent.nextInterval = self.agent.interval
                        else:

                            self.agent.dispatched.put_nowait({"time": msg.metadata, "message": msg.body})
                            if self.agent.last_object_type == "LOAD" and self.agent.mexToSend.qsize() != 0:

                                for i in range(self.agent.mexToSend.qsize()):
                                     mex = Message(to=basejid+"/"+simjid)
                                     message = self.agent.mexToSend.get_nowait()
                                     mex.body = message
                                     await self.send(mex)
                                self.agent.interval += 1
                                self.agent.nextInterval = self.agent.interval
                            elif self.agent.last_object_type == "LOAD" and self.agent.mexToSend.qsize() == 0:

                                mex = Message(to=basejid+"/"+simjid)
                                message = "AckMessage"
                                mex.body = message

                                await self.send(mex)
                                self.agent.nextInterval = self.agent.interval
                            else:
                                self.agent.interval += 1
                            self.agent.oldStart = msg.metadata
                    except Exception as e:

                        logging.warning(e)
