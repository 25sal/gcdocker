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
Dispatcher
=======================================
This agent deals with the message queue management.
"""

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime, timedelta
from agents import setup as es
import csv
from sys import path
from aioxmpp import PresenceShow
from utils.config import Configuration
import logging
from utils.MessageFactory import MessageFactory

path.append("..")
LOGFILE = './gcdaemon.log'

# logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

#################################################################https://calendar.google.com/calendar/u/0/r#####################################################################
# This function calculates the execution time of a scheduled load. It is used to put DeleteMessage in sharedQueue at the right time. #
######################################################################################################################################

def calculateTime(file):
    """
    This function calculates the execution time of a scheduled load. It is used to put DeleteMessage in sharedQueue at the right time.
    Args:
        file: Timeseries whose time delta is to be calculated
    """
    dirPath2 = Configuration.parameters['current_sim_dir'] + "/Inputs/" + file
    f = open(dirPath2)
    csv_f = csv.reader(f)
    data = []
    count = 0
    for row in csv_f:
        data.append(row[0].split()[0])
        count += 1
    f.close()
    delta = int(data[-1]) - int(data[0])
    return delta


def switchInTime(file, ast):
    """
    This function shifts a timeseries over time based on the ast received from the scheduler.
    Args:
        file: Timeseries whose time is to be shift
        ast:  New assigned starting Time
    """
    dirPath2 = Configuration.parameters['runtime_dir'] + "/inputs/" + file
    dirPathArrival = Configuration.parameters['runtime_dir'] + "/output/SH/" + file
    f = open(dirPath2)
    csv_f = csv.reader(f)
    with open(dirPath2, "r") as f:
        with open(dirPathArrival, "w") as f2:
            writer = csv.writer(f2, delimiter=' ')
            reader = csv.reader(f, delimiter=' ')
            first = 0
            firstTime = 0

            for data in reader:
                entry = []
                if(first == 0):
                    firstTime = data[0]
                    first = 1

                entry.append(ast + int(data[0]) - int(firstTime))
                entry.append(data[1])
                writer.writerow(entry)

##################################################################################################
# This method calculates consumption in KW of a load consumer. It is used in the delete message. #
##################################################################################################
def calculate_consum(file):
    """
    This method calculates consumption in KW of a load consumer. It is used in the delete message.
    Args:
        file: Timeseries whose consumption is to be calculated
    """
    dirPath2 = Configuration.parameters['current_sim_dir'] + "/Inputs/" + file
    f = open(dirPath2)
    csv_f = csv.reader(f)
    data = 0
    count = 0
    for row in csv_f:
        data = row[0].split()[1]
    f.close()
    # data = float(data)/1000
    return data

##################################################################################################
# Dispatcher Class, it is a SPADE Agent with two behaviours:                                     #
# 1) Wait for a start/stop message from Setup Module                                             #
# 2) Consume events from a queue. Phases:                                                        #
# 2.1) reads object from the queue                                                               #
# 2.2) prepare a message using MessageFactory using the correct protocol (REST, XMPP)            #
# 2.3) send message                                                                              #
# 2.4) wait for a response (if needed)                                                           #
##################################################################################################
class dispatcher(Agent):

    def __init__(self, address, passw):
        """
        Dispatcher Class, it is a SPADE Agent with two behaviours:
         1) Wait for a start/stop message from Setup Module
         2) Consume events from a queue. Phases:
         2.1) reads object from the queue
         2.2) prepare a message using MessageFactory using the correct protocol (REST, XMPP)
         2.3) send message
         2.4) wait for a response (if needed)
        Args:
            address: The agent Address
            passw: The agent Password
        """
        super(dispatcher, self).__init__(address, passw)
        self.idToLoad = {}
        self.abilitation = False
        self.messageToWait = Configuration.messageToWait

    ##################################################################################
    # This method check periodically if start/stop messages are sent by setupModule. #
    ##################################################################################
    class disRecvBehav(PeriodicBehaviour):
        '''
        This method check periodically if start/stop messages are sent by setupModule.
        Args:
            PeriodicBehaviour: The behaviour's type
        '''
        async def run(self):
            logging.info("DisRecvBehav running")
            msg = await self.receive(timeout=5)
            if msg:
                try:
                    if msg.body == "start":
                        logging.info("Message received with content: {}".format(msg.body))
                        self.agent.abilitation = True


                    elif msg.body == "stop":
                        logging.info("Message received with content: {}".format(msg.body))
                        self.agent.abilitation = False
                    else:
                        logging.info("Did not received any message after 5 seconds")
                except:
                    None
            else:
                logging.debug(" receive timeout ")

    ##############################################
    # This method consume events from the queue. #
    ##############################################
    class consumeEvent(PeriodicBehaviour):
        '''
        This method consume events from the queue.
        Args:
            PeriodicBehaviour: The behaviour's type
        '''
        async def onstart(self):
            logging.info("A ConsumeEvent queue is Starting...")
            self.mydir = Configuration.parameters['user_dir']

        async def run(self):
            finish = True
            WasEnable = False
            protocol_version = Configuration.parameters['protocol']
            date = Configuration.parameters['date'] + " 00:00:00"
            datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
            timestamp = str(datetime.timestamp(datetime_object)).split(".")[0]
            completed = 0
            total = es.Entities.sharedQueue.qsize()
            percent = 0
            deletedList = []
            path = Configuration.parameters['current_sim_dir']
            with open(path + "/Results/" + Configuration.parameters['user_dir'] + "/output/output.txt", "w+") as file:
                finish = 0
                ##############################################
                # Consume all the configuration messages     #
                ##############################################
                while finish == 0:
                    next2 = es.Entities.next_event()
                    if (next2[1].type == "neighborhood"):
                        message = MessageFactory.neighborhood(next2[1], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[1].type == "house":
                        message = MessageFactory.house(next2[1], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        if next2[1].numcp != 0:
                            message = MessageFactory.chargingstation(next2[1], timestamp, protocol_version)
                            await self.send(message)
                            file.write(">>> " + message.body + "\n")
                            file.flush()
                    elif next2[1].type == "chargingStation":
                        message = MessageFactory.chargingstation(next2[1], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[1].type == "chargingPoint":
                        message = MessageFactory.chargingpoint(next2[1], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[1].type == "energy_cost":
                        message = MessageFactory.energyCost(next2[1], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[1].type == "energy_mix":
                        message = MessageFactory.energyMix(next2[1], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[1].type == "EV" and next2[1].device.type == "CREATE_EV":
                        next2[1].device.type = "EV_BOOKING"
                        message = MessageFactory.create_ev(next2[1], next2[0], protocol_version)
                        await self.send(message)
                        file.write(message.body + "\n")
                        file.flush()
                    elif next2[1].type == "heatercooler":
                        message = MessageFactory.heatercooler(next2[1], next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[1].type == "background":
                        message = MessageFactory.background(next2[1], next2[0], protocol_version)
                        await self.send(message)
                    elif next2[1].type == "load" and next2[1].device.type == "Producer":
                        message = MessageFactory.create_producer(next2[1], next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        message = MessageFactory.update_producer(next2[1], next2[0], protocol_version)
                        await self.send(message)
                        msg2 = await self.receive(timeout=3)
                        file.write(">>> " + message.body + "\n")
                        message = MessageFactory.energyCostProducer(next2[1], next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        next2[1].type = "LoadUpdate"
                        next2[1].creation_time = int(next2[1].creation_time) + 21600
                        next2[1].count = 1
                        es.Entities.enqueue_event(int(next2[1].creation_time),  next2[1])
                        file.flush()
                    else:
                        finish = 1
                        es.Entities.enqueue_event(int(next2[0]), next2[1],  int(next2[2]))
                    ##################################################################################
                    # Wait for BG and HC SCHEDULED MESSAGE BUT  DO NOTHING                           #
                    ##################################################################################
                    messageFromScheduler = None
                    if(next2[1].type in self.agent.messageToWait):
                        if protocol_version == "1.0":
                            while isinstance(messageFromScheduler, type(None)):
                                logging.debug("sono in attesa di un messaggio")
                                messageFromScheduler = await self.receive(timeout=20)
                            file.write("<<< " + messageFromScheduler.body + "\r\n")
                            file.flush()
                        else:
                            messageFromScheduler = await self.receive(timeout=20)
                            while not isinstance(messageFromScheduler, type(None)):
                                logging.info(messageFromScheduler.body)
                                if messageFromScheduler.body == "AckMessage":
                                    logging.info("Ack Received")
                                messageFromScheduler = await self.receive(timeout=20)


                    file.write(next2[1].type + "\n")
                    file.flush()

                ##################################################################################
                # When configuration messages are terminated, continue to consume the others     #
                ##################################################################################
                while self.agent.abilitation and finish:
                    WasEnable = True
                    messageFromScheduler = None

                    next2 = es.Entities.next_event()
                    nextload = next2[1]
                    actual_time = next2[0]

                    try:
                        providedby = next2[3]
                    except:
                        None

                    with open("../time.txt", "w") as f2:
                        f2.write(str(next2[0]))
                        f2.close()
                    completed += 1
                    if nextload.device.type == "Producer" and nextload.type == "load":
                        message = MessageFactory.create_producer(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        message = MessageFactory.update_producer(nextload, next2[0], protocol_version)
                        await self.send(message)
                        msg2 = await self.receive(timeout=3)
                        file.write(">>> " + message.body + "\n")
                        message = MessageFactory.energyCostProducer(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        nextload.type = "LoadUpdate"
                        nextload.creation_time = int(nextload.creation_time) + 21600
                        nextload.count = 1
                        es.Entities.enqueue_event(int(nextload.creation_time),  nextload)
                        file.flush()
                    elif nextload.device.type == "Producer" and nextload.type == "LoadUpdate":
                        message = MessageFactory.update_producer(nextload, next2[0], protocol_version)
                        await self.send(message)
                        msg2 = await self.receive(timeout=3)
                        if nextload.count < 2:
                            nextload.creation_time = int(nextload.creation_time) + 21600
                            nextload.count += 1
                            es.Entities.enqueue_event(int(nextload.creation_time),  nextload, int(next2[2]))
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.device.type == "battery":
                        message = MessageFactory.create_Battery(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.type == "load" and nextload.device.type == "Consumer":
                        total += 1
                        message = MessageFactory.create_load(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        self.agent.idToLoad["[" + str(nextload.house) + ']:[' + str(nextload.device.id) + ']'] = nextload
                    elif nextload.type == "delete":
                        if nextload.device.id not in deletedList:
                            deletedList.append(nextload.device.id)
                            message = MessageFactory.delete_load(nextload, next2[0], protocol_version)
                            await self.send(message)
                            file.write(">>> " + message.body + "\n")
                            file.flush()
                    elif nextload.type == "EV" and nextload.device.type == "EV_ARRIVAL":
                        nextload.device.type = "EV_DEPARTURE"
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.type == "EV" and nextload.device.type == "EV_BOOKING":
                        nextload.device.type = "EV_ARRIVAL"
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(message.body + "\n")
                        file.flush()
                    elif nextload.type == "EV" and nextload.device.type == "EV_DEPARTURE":
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.type == "heatercooler":
                        logging.info("condiz")
                        message = MessageFactory.heatercooler(nextload, next2[0], protocol_version)
                        await self.send(message)
                        logging.info("inviato")
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.type == "background":
                        message = MessageFactory.background(nextload, next2[0], protocol_version)
                        logging.info(protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()

                    ##################################################################################
                    # Wait response messages                                                         #
                    ##################################################################################
                    if(nextload.type in self.agent.messageToWait):
                        if protocol_version == "1.0":
                            while isinstance(messageFromScheduler, type(None)):
                                logging.debug("sono in attesa di un messaggio")
                                messageFromScheduler = await self.receive(timeout=20)
                            while messageFromScheduler.body.split(" ")[0] != "SCHEDULED":
                                logging.info("messaggio:" + messageFromScheduler.body)
                                try:
                                    receivedLoad = self.agent.idToLoad[messageFromScheduler.body.split(" ")[1]]
                                    logging.debug(messageFromScheduler.body)
                                    delta = calculateTime(receivedLoad.profile)
                                    newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                    mydel = es.eventDelete(receivedLoad.device, receivedLoad.house, newTime,calculate_consum(receivedLoad.profile))
                                    switchInTime(receivedLoad.profile, int(messageFromScheduler.body.split(" ")[3]))
                                    es.Entities.enqueue_event(int(newTime),  mydel)
                                    file.write("<<< " + messageFromScheduler.body + "\r\n")
                                    file.flush()
                                except Exception as e:
                                    logging.warning(e)
                                    logging.warning("unrecognized Message")
                                messageFromScheduler = await self.receive()
                                while (isinstance(messageFromScheduler, type(None))):
                                    messageFromScheduler = await self.receive(timeout=20)
                                logging.info("messaggio:" + messageFromScheduler.body)
                            file.write("<<< " + messageFromScheduler.body + "\r\n")
                            file.flush()
                        else:
                            messageFromScheduler = await self.receive(timeout=20)
                            while not isinstance(messageFromScheduler, type(None)):
                                logging.info(messageFromScheduler.body)
                                if messageFromScheduler.body == "AckMessage":
                                    logging.info("Ack Received")
                                else:
                                    try:
                                        receivedLoad = self.agent.idToLoad[messageFromScheduler.body.split(" ")[1]]
                                        delta = calculateTime(receivedLoad.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                        mydel = es.eventDelete(receivedLoad.device, receivedLoad.house, newTime,calculate_consum(receivedLoad.profile),messageFromScheduler.body.split(" ")[5])
                                        switchInTime(receivedLoad.profile, int(messageFromScheduler.body.split(" ")[3]))
                                        es.Entities.enqueue_event(int(newTime),  mydel)
                                        file.write(">>> " + message.body + "\n")
                                        file.write("<<< " + messageFromScheduler.body + "\r\n")
                                        file.flush()
                                    except Exception as e:
                                        logging.info(e)
                                messageFromScheduler = await self.receive(timeout=20)

                    if es.Entities.sharedQueue.empty():
                        if protocol_version == "2.0":
                            messageFromScheduler = await self.receive(timeout=10)
                            while not isinstance(messageFromScheduler, type(None)):
                                if messageFromScheduler.body == "AckMessage":
                                    logging.info("Ack Received")
                                else:
                                    try:
                                        receivedLoad = self.agent.idToLoad[messageFromScheduler.body.split(" ")[1]]
                                        delta = calculateTime(receivedLoad.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                        mydel = es.eventDelete(receivedLoad.device, receivedLoad.house, newTime,calculate_consum(receivedLoad.profile),messageFromScheduler.body.split(" ")[4])
                                        switchInTime(receivedLoad.profile, int(messageFromScheduler.body.split(" ")[3]))
                                        es.Entities.enqueue_event(int(newTime),mydel)
                                        es.count += 1
                                        file.write(">>> " + message.body + "\n")
                                        file.write("<<< " + messageFromScheduler.body + "\r\n")
                                        file.flush()
                                    except:
                                        logging.info("unrecognized Message")
                                messageFromScheduler = await self.receive(timeout=10)
                    if es.Entities.sharedQueue.empty():
                        message = MessageFactory.end(actual_time)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        file.close()
                        finish = False
                        logging.info("Simulazione terminata.")

                if WasEnable:
                    logging.info("Ho rilevato un segnale di stop")
            if finish == False:
                message = MessageFactory.end(actual_time)
                await self.send(message)
                await self.agent.stop()

    ################################################################
    # Setup the dispatcher agent, create behaviours and start them #
    ################################################################
    async def setup(self):
        '''
        Setup the dispatcher agent, create behaviours and start them.
        '''
        basejid = Configuration.parameters["userjid"]
        start_at = datetime.now() + timedelta(seconds=3)
        logging.info("ReceiverAgent started")
        b = self.disRecvBehav(1, start_at=start_at)
        template = Template()
        template2 = Template()
        template = Template()
        protocol_version = Configuration.parameters['protocol']
        if protocol_version == "1.0":
            template2.sender = basejid + "/actormanager"
        else:
            template2.sender = basejid + "/adaptor"
        template.set_metadata("control", "startorstop")
        self.presence.set_available(show=PresenceShow.CHAT)
        self.add_behaviour(b, template)
        start_at = datetime.now() + timedelta(seconds=3)
        Behaviour2 = self.consumeEvent(1, start_at=start_at)
        self.add_behaviour(Behaviour2, template2)
