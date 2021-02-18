
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
XMPPAdaptor
=======================================
This agent create a REST server in order to communicate with XMPP schedulers.
"""

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from datetime import datetime,timedelta
import queue
from aiohttp import web
import json
from shutil import copy2
from utils.config import Configuration
import logging

LOGFILE = '/home/gc/simulator/gcdaemon.log'

#logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

##########################################
#  Adaptor used for the XMPP protocol    #
##########################################
class Adaptor(Agent):
    '''
    Adaptor used for the XMPP protocol.

    Args:
        Agent: The spade Agent.
    '''
    count = 0
    async def setup(self):
        start_at = datetime.now() + timedelta(seconds=3)
        self.mexToSend = queue.Queue()

        #self.traces.reset()


    #######################################################################
    #  POST API used by schedulers to post a timeseries.                  #
    #  It recieve a file and write the content in simulation directory    #
    #######################################################################
    async def exposePostRestAPI(self, request):
        """
        POST API used by schedulers to post a timeseries.
        It recieve a file and write the content in simulation directory

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
                        f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+str(self.count)+"_"+id_load+".csv", "w+")
                        for line in input_file:
                            f.write(line.decode("utf-8"))
                    copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/HC/"+str(self.count)+"_"+id_load+".csv","/var/www/Simulations/demo/"+Configuration.parameters['user_dir']+"/output")
                    
            elif(sub == "EV_PROFILE"):
                    id_load = parsed_json['id']
                    input_file = data['csvfile'].file
                    file_name = data['csvfile'].filename
                    if input_file:
                        f = open(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+str(self.count)+"_"+id_load+".csv", "w+")
                        for line in input_file:
                            f.write(line.decode("utf-8"))
                        f.flush()    
                        f.close()
                    copy2(path+"/"+simdir+"/Results/"+Configuration.parameters['user_dir']+"/output/EV/"+str(self.count)+"_"+id_load+".csv","/var/www/Simulations/demo/"+Configuration.parameters['user_dir']+"/output")
            self.count+=1
        except Exception as e:
            logging.info(e)
            logging.info("not valid request")
        logging.info("AAAAAA RICEVUTOOO")
        response = web.StreamResponse(
        status=200,
        reason='OK'
        )

        return response


    class XMPPMessageManager(PeriodicBehaviour):

        async def onstart(self):
            logging.info("A ConsumeEvent queue is Starting...")
        async def run(self):
            logging.info("adaptor is running")
