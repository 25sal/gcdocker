import time
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import setupmodule as sm
import externalSourceAgent as es
import datetime
import yaml
global abilit
from yaml import Loader

abilit = 0

class setupModule(Agent):
    class startService(OneShotBehaviour):
        async def run(self):
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
            print("InformBehav running")
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "start"                    # Set the message content
            time.sleep(5)

            await self.send(msg)

            print("Message start sent!")
            # stop agent from behaviour
            #await self.agent.stop()

    class stopService(OneShotBehaviour):
        async def run(self):
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "stop"                    # Set the message content
            print("Message stop sent!")
            await self.send(msg)

    async def setup(self):
        print("SenderAgent started")
        b = self.startService()
        self.add_behaviour(b)
