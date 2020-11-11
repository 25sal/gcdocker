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
                self.mexToSend.put_nowait(mex)
        elif(sub == "HC_PROFILE"):
                id_load = parsed_json['id']
                input_file = data['csvfile'].file
                if input_file:
                    f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+id_load+".csv", "w+")
                    for line in input_file:
                        f.write(line.decode("utf-8"))
                copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+id_load+".csv","/home/gcdemo/public_html/Simulations/"+user+"/"+Configuration.parameters['user_dir']+"/output")
                
        elif(sub == "EV_PROFILE"):
                id_load = parsed_json['id']
                input_file = data['csvfile'].file
                file_name = data['csvfile'].filename
                if input_file:
                    f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+id_load+".csv", "w+")
                    for line in input_file:
                        f.write(line.decode("utf-8"))
                copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+id_load+".csv","/home/gcdemo/public_html/Simulations/"+user+"/"+Configuration.parameters['user_dir']+"/output")

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


