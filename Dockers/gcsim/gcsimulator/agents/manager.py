from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

global abilit
from utils.config import Configuration
import logging

abilit = 0
LOGFILE = '/home/gc/simulator/gcdaemon.log'

logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

class SimLifeCycle:
    # status 0: reset, 1: runtime built, 2: running, 
    #
    status = 0

#####################################################################
#  SetupModule Agent is used for start/stop dispatching messages    #
#####################################################################
class setupModule(Agent):
    #########################################################
    #  startService Behaviour is used for start dispatcher  #
    #########################################################
    class startService(OneShotBehaviour):
        async def run(self):
            basejid = Configuration.parameters['userjid']
            simjid = Configuration.parameters['simulator']
            logging.info("InformBehav running")
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "start"                    # Set the message content
            #time.sleep(5)

            await self.send(msg)

            logging.info("Message start sent!")


    #############################################################
    #  stopService Behaviour is used for stop/pause dispatcher  #
    #############################################################
    class stopService(OneShotBehaviour):
        async def run(self):
            basejid = Configuration.parameters['userjid']
            simjid = Configuration.parameters['simulator']
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "stop"                    # Set the message content
            logging.info("Message stop sent!")
            await self.send(msg)

    async def setup(self):
        logging.info("SenderAgent started")
        b = self.startService()
        self.add_behaviour(b)
        self.presence.on_available = self.my_on_available_handler

    def my_on_available_handler(self, peer_jid, stanza):
        logging.info(f"My friend {peer_jid} is now available with show {stanza.show}")
        if peer_jid == Configuration.parameters['userjid'] + '/' + Configuration.parameters['simulator']:
            if SimLifeCycle.status == 0:
                SimLifeCycle.status = 1
                b = self.startService()
                self.add_behaviour(b)

