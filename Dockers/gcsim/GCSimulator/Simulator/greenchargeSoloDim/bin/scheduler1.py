from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime,timedelta
import queue
from aiohttp import web
import yaml
from yaml import Loader
import json
import externalSourceAgent as es
from shutil import copy2
from configure import Configuration
import logging

LOGFILE = '/home/gc/simulator/gcdaemon.log'

logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

##########################################
#  Adaptor used for the XMPP protocol    #
##########################################
class scheduler(Agent):

    async def setup(self):
        start_at = datetime.now() + timedelta(seconds=3)
        self.mexToSend = queue.Queue()

        #self.traces.reset()


    #######################################################################
    #  POST API used by schedulers to post a timeseries.                  #
    #  It recieve a file and write the content in simulation directory    #
    #######################################################################
    async def post_answer(self,request):
        data = await request.post()
        path = Configuration.parameters['simulation_dir']
        simdir = Configuration.parameters['simulation']
        try:
            message = data['response']
            parsed_json = (json.loads(message))
            sub = parsed_json['subject']


            logging.info("riceveid")

            if(sub == "ASSIGNED_START_TIME"):
                    id_load = parsed_json['id']
                    ast = parsed_json['ast']
                    producer = parsed_json['producer']
                    mex = sub + " ID " + id_load + " " + ast + " PV " + producer
                    self.mexToSend.put_nowait(mex)
            elif(sub == "HC_PROFILE"):
                    id_load = parsed_json['id']
                    input_file = data['csvfile'].file
                    if input_file:
                        f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+id_load+".csv", "w+")
                        for line in input_file:
                            f.write(line.decode("utf-8"))
                    copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+id_load+".csv","/var/www/Simulations/demo/"+Configuration.parameters['user_dir']+"/output")
                    
            elif(sub == "EV_PROFILE"):
                    id_load = parsed_json['id']
                    input_file = data['csvfile'].file
                    file_name = data['csvfile'].filename
                    if input_file:
                        f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+id_load+".csv", "w+")
                        for line in input_file:
                            f.write(line.decode("utf-8"))
                        f.flush()    
                        f.close()
                    copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+id_load+".csv","/var/www/Simulations/demo/"+Configuration.parameters['user_dir']+"/output")
        except Exception as e:
            logging.info(e)
            logging.info("not valid request")
        logging.info("AAAAAA RICEVUTOOO")
        response = web.StreamResponse(
        status=200,
        reason='OK'
        )

        return response


    class consumeEvent2(PeriodicBehaviour):

        async def onstart(self):
            logging.info("A ConsumeEvent queue is Starting...")
        async def run(self):
            logging.info("adaptor is running")


