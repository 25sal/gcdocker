import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour,PeriodicBehaviour
from spade.message import Message
from spade.template import Template
import setupmodule as sm
import externalSourceAgent as es
import datetime
import yaml
global abilit
from configure import Configuration

abilit = 0

class SimLifeCycle:
    # status 0: reset, 1: runtime built, 2: running, 
    #
    status = 0

class setupModule(Agent):
    class startService(OneShotBehaviour):
        async def run(self):
            basejid = Configuration.parameters['userjid']
            simjid = Configuration.parameters['simulator']
            print("InformBehav running")
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "start"                    # Set the message content
            #time.sleep(5)

            await self.send(msg)

            print("Message start sent!")
            # stop agent from behaviour
            # await self.agent.stop()

    class stopService(OneShotBehaviour):
        async def run(self):
            basejid = Configuration.parameters['userjid']
            simjid = Configuration.parameters['simulator']
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "stop"                    # Set the message content
            print("Message stop sent!")
            await self.send(msg)

    async def setup(self):
        print("SenderAgent started")
        b = self.startService()
        self.add_behaviour(b)
        self.presence.on_available = self.my_on_available_handler

    def my_on_available_handler(self, peer_jid, stanza):
        print(f"My friend {peer_jid} is now available with show {stanza.show}")
        if peer_jid == Configuration.parameters['userjid'] + '/' + Configuration.parameters['simulator']:
            if SimLifeCycle.status == 0:
                SimLifeCycle.status = 1
                b = self.startService()
                self.add_behaviour(b)


