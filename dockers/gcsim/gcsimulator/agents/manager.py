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
Manager
=======================================
This agent starts and stops the simulation.
"""
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message

global abilit
from utils.config import Configuration
import logging

abilit = 0
LOGFILE = '/home/gc/simulator/gcdaemon.log'

# logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

class SimLifeCycle:
    # status 0: reset, 1: runtime built, 2: running,
    #
    status = 0

#####################################################################
#  SetupModule Agent is used for start/stop dispatching messages    #
#####################################################################
class SetupModule(Agent):
    '''
    SetupModule Agent is used for start/stop dispatching messages.

    Args:
        Agent: The spade Agent.
    '''
    #########################################################
    #  startService Behaviour is used for start dispatcher  #
    #########################################################
    class StartService(OneShotBehaviour):
        '''
        The startService Behaviour is used for start dispatcher.

        Args:
            OneShotBehaviour: The behaviour's type.
        '''
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
    class StopService(OneShotBehaviour):
        '''
        The stopService Behaviour is used for stop dispatcher.

        Args:
            OneShotBehaviour: The behaviour's type.
        '''
        async def run(self):
            basejid = Configuration.parameters['userjid']
            simjid = Configuration.parameters['simulator']
            msg = Message(to=basejid+"/"+simjid)     # Instantiate the message
            msg.set_metadata("control", "startorstop")  # Set the "inform" FIPA performative
            msg.body = "stop"                    # Set the message content
            logging.info("Message stop sent!")
            await self.send(msg)

    async def setup(self):
        '''
        The setup method is used for add behaviours to the agent.
        '''
        logging.info("SenderAgent started")
        b = self.StartService()
        self.add_behaviour(b)
        self.presence.on_available = self.my_on_available_handler

    def my_on_available_handler(self, peer_jid, stanza):
        logging.info(f"My friend {peer_jid} is now available with show {stanza.show}")
        if peer_jid == Configuration.parameters['userjid'] + '/' + Configuration.parameters['simulator']:
            if SimLifeCycle.status == 0:
                SimLifeCycle.status = 1
                b = self.StartService()
                self.add_behaviour(b)
