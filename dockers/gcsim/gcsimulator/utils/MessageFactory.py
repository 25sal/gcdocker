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
Message Factory
=======================================
This Class deals with the message creation from data.
"""

from utils.config import Configuration
from spade.message import Message
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


##################################################################################################################
# This Class manages all messages between scheduler and dispatcher. It prepares the messages based on subjects.  #
##################################################################################################################
class MessageFactory:
    """
    This Class deals with the message creation from data.
    """
    realpath = None
    jid = None
    basejid = None
    dir1 = None

    @classmethod
    def init_parameters(cls):
        """
        This Method initializes the parameters useful to the class.
        """
        cls.jid = Configuration.parameters['adaptor']
        cls.basejid = Configuration.parameters['userjid']
        cls.dir1 = Configuration.parameters['current_sim_dir']
        webdir = Configuration.parameters['webdir']
        cls.realpath = webdir

    #######################################
    # This Method manages "End" message.  #
    #######################################
    @classmethod
    def end(cls, actual_time):
        """
        This method creates the end message.
        Args:
            actual_time: Simulation Time.
        """
        protocol_version = Configuration.parameters["protocol"]
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "SIMULATION END " + str(actual_time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '({"message" : {"subject" : "SIMULATION_END", "simulation_time": " ' + str(actual_time) + ' "}}'
            mex.body = message
            mex.metadata = "0"
            return mex

    ##############################################
    # This Method manages "EnergyCost" message.  #
    ##############################################
    @classmethod
    def energyCost(cls, device, time, protocol_version):
        """
        This method creates the EnergyCost message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        web_url = Configuration.parameters['web_url']
        mydir = Configuration.parameters['user_dir']
        if protocol_version == "1.0":
            name = cls.basejid.split('@')[0]
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "ENERGY_COST [0] " + "http://" + str(url) + "/~gcdemo/" + cls.realpath + "/" + str(
                Configuration.mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "ENERGY_COST",id: "[0]","profile" : "' + web_url + '/' + cls.realpath + "/" + str(mydir) + '/' + str(device.profile) + '"}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    ############################################################
    # This Method manages "EnergyCost" for producers message.  #
    ############################################################
    @classmethod
    def energyCostProducer(cls, device, time, protocol_version):
        """
        This method creates the EnergyCost for producers message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        web_url = Configuration.parameters['web_url']
        mydir = Configuration.parameters['user_dir']
        if protocol_version == "1.0":
            name = cls.basejid.split('@')[0]
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "ENERGY_COST [" + str(device.house) + "]:[" + str(device.device.id) + "] " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/Results/" + str(mydir) + "/" + str(
                device.energycost) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "ENERGY_COST",id: "["' + str(device.house) + '"]:["' + str(
                device.device.id) + '"]","profile" : "' + web_url + '/' + cls.realpath + "/" + str(
                mydir) + '/' + str(device.energycost) + '"}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    #############################################
    # This Method manages "EnergyMix" message.  #
    #############################################
    @classmethod
    def energyMix(cls, device, time, protocol_version):
        """
        This method creates the EnergyMix message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        web_url = Configuration.parameters['web_url']
        mydir = Configuration.parameters['user_dir']
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "ENERGY_MIX " +  str(web_url) + "/" + cls.realpath + "/" + str(mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "ENERGY_MIX","profile" : "' + web_url + '/' + cls.realpath + "/" + str(mydir) + '/' + str(device.profile) + ' "}}'
            mex.body = message
            mex.metadata = '0'
            return (mex)

    #################################################################
    # This Method manages "EnergyGroup" message for Neighborhood.   #
    #################################################################
    @classmethod
    def neighborhood(cls, device, time, protocol_version):
        """
        This method creates the EnergyHub for neighborhood message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP [99] " + str(device.peakload) + " " + time
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_ENERGY_GROUP","powerpeak" : " ' + str(
                device.peakload) + ' "}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    ###########################################################
    # This Method manages "EnergyGroup" message for houses.   #
    ###########################################################
    @classmethod
    def house(cls, device, time, protocol_version):
        """
        This method creates the EnergyHub for houses message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP [" + str(device.id) + "] " + str(device.peakload) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_ENERGY_GROUP", "id" : " ' + str(
                device.id) + ' ", "powerpeak" : " ' + str(device.peakload) + ' "}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    #####################################################################
    # This Method manages "EnergyGroup" message for ChargingStations.   #
    #####################################################################
    @classmethod
    def chargingstation(cls, device, time, protocol_version):
        """
        This method creates the EnergyHub for Charging Station message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP  [" + str(device.id) + "] " + str(device.peakload) + " " + str(time)
            mex.body = message
            return (mex)
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_ENERGY_GROUP", "id" : " ' + str(
                device.id) + ' ", "powerpeak" : " ' + str(device.peakload) + ' ", "numcp" : " ' + str(
                device.numcp) + ' "}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    ###################################################################
    # This Method manages "EnergyGroup" message for ChargingPoints.   #
    ###################################################################
    @classmethod
    def chargingpoint(cls, device, time, protocol_version):
        """
        This method creates the EnergyHub for Charging Point message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP [" + str(device.houseid) + "]:[" + str(
                device.id) + "]" + " CONNECTORS_TYPE " + str(device.connection_type) + " POWERPEAK " + str(
                device.peakload) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_ENERGY_GROUP", "id" : "[' + str(
                device.houseid) + ']:[' + str(device.id) + ']", "connectors_type" : " ' + str(
                device.connection_type) + ' ", "powerpeak" : " ' + str(device.peakload) + ' "}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    #################################################
    # This Method manages "HeaterCooler" message.   #
    #################################################
    @classmethod
    def heatercooler(cls, device, time, protocol_version):
        """
        This method creates the HeaterCooler message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        web_url = Configuration.parameters['web_url']
        mydir = Configuration.parameters['user_dir']
        if protocol_version == "1.0":
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "HC [" + str(device.house) + "]:[" + str(device.device.id) + "] 0 " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/" + str(mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return (mex)
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "HC","id" : "[' + str(device.house) + ']:[' + str(
                device.device.id) + ']","profile" : "' + web_url + '/' + cls.realpath + "/" + str(mydir) + '/' + str(device.profile) + ' "}}'
            mex.body = message
            mex.metadata = time
            return mex

    #################################################
    # This Method manages "Background" message.   #
    #################################################
    @classmethod
    def background(cls, device, time, protocol_version):
        """
        This method creates the Background message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        mydir = Configuration.parameters['user_dir']
        web_url = Configuration.parameters['web_url']
        if protocol_version == "1.0":
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "BG  [" + str(device.house) + "]:[" + str(device.device.id) + "] 0 " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/" + str(mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:

            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "BG","id" : "[' + str(device.house) + ']:[' + str(
                device.device.id) + ']","profile" : "' + web_url + '/' + cls.realpath + "/" + str(
                mydir) + '/' + str(device.profile) + ' "}}'
            mex.body = message
            mex.metadata = time
            return mex


    ##############################################################
    # METHOD NOT USED. MAYBE USEFULL IN  FUTURE IMPLEMENTATION   #
    ##############################################################
    """@classmethod
    def charge_on_demand(cls, device, time, protocol_version):

        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = '"message: {"subject": "EV", "capacity":' + str(
                device.device.capacity) + ', "max_ch_pow_ac":' + str(
                device.device.max_ch_pow_ac) + ',"max_ch_cc":' + str(
                device.device.max_ch_pow_cc) + ', "max_all_en":' + str(
                device.device.max_all_en) + ',"min_all_en:' + str(device.device.min_all_en) + ',"sb_ch:"' + str(
                device.device.sb_ch) + ',"ch_eff:"' + str(device.device.ch_eff) + ',"soc_at_arrival":' + str(
                device.Soc_at_arrival) + ',"planned_departure_time":' + str(
                device.planned_departure_time) + ',"arrival_time:"' + str(
                device.actual_arrival_time) + ', "v2g":' + str(device.v2g) + ',"target_soc":' + str(
                device.target_soc) + '}}'
            mex.body = message

            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "EV", "capacity" : " ' + str(
                device.device.capacity) + ' " , "max_ch_pow_ac" : " ' + str(
                device.device.max_ch_pow_ac) + ' " , "max_ch_cc" : " ' + str(
                device.device.max_ch_pow_cc) + ' " , "max_all_en" : " ' + str(
                device.device.max_all_en) + ' " , "min_all_en" : " ' + str(
                device.device.min_all_en) + ' " , "sb_ch" : " ' + str(
                device.device.sb_ch) + ' " , "ch_eff" :  " ' + str(
                device.device.ch_eff) + ' " , "soc_at_arrival": " ' + str(
                device.Soc_at_arrival) + ' " , "planned_departure_time" : " ' + str(
                device.planned_departure_time) + ' " , "arrival_time" : " ' + str(
                device.actual_arrival_time) + ' " , "v2g" : " ' + str(
                device.v2g) + ' " , "target_soc" : " ' + str(device.target_soc) + ' " }}'
            mex.body = message
            mex.metadata = time
            return (mex)
    """
    ##########################################
    # Method used for Ev arrival, departure  #
    ##########################################
    @classmethod
    def booking_request(cls, device, time, protocol_version):
        """
        This method creates the booking_request message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "EV [" + str(
                device.device.id) + "] " + device.Soc_at_arrival + " " + device.actual_departure_time + " " + device.actual_arrival_time + " [" + str(
                device.house) + "]:[" + str(device.device.cp) + "] " + device.v2g + " " + device.target_soc + " " + str(
                time)
            mex.body = message

            return (mex)

        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)

            message = '{"message" : {"subject" : "EV" , "id" : "[' + str(
                device.device.id) + ']", "soc_at_arrival": " ' + str(
                device.Soc_at_arrival) + ' " , "actual_departure_time" : " ' + str(
                device.actual_departure_time) + ' " , "arrival_time" : " ' + str(
                device.actual_arrival_time) + ' " ,"charging_point" : "[' + str(device.house) + ']:[' + str(
                device.device.cp) + ']", "v2g" : " ' + str(device.v2g) + ' " , "target_soc" : " ' + str(
                device.target_soc) + ' " }}'
            mex.body = message
            mex.metadata = time
            return (mex)

    ##############################################
    # This Method manages "Create_EV" message.   #
    ##############################################
    @classmethod
    def create_ev(cls, device, time, protocol_version):
        """
        This method creates the Create Ev message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_EV [" + str(
                device.device.id) + "] " + device.device.capacity + " " + device.device.max_ch_pow_ac + " " + \
                      device.device.max_ch_pow_cc + " " + device.device.max_all_en + " " + device.device.min_all_en + \
                      " " + device.device.sb_ch + " " + device.device.sb_dis + " " + device.device.ch_eff + " " + \
                      device.device.dis_eff + " " + device.v2g + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_EV" , "id" : "[' + str(
                device.device.id) + ']", "capacity" : " ' + str(
                device.device.capacity) + ' " , "max_ch_pow_ac" : " ' + str(
                device.device.max_ch_pow_ac) + ' " , "max_ch_pow_cc" : " ' + str(
                device.device.max_ch_pow_cc) + ' " , "max_dis_pow_ac" : " ' + str(
                device.device.max_dis_pow_ac) + ' " , "max_dis_pow_cc" : " ' + str(
                device.device.max_dis_pow_cc) + ' " , "max_all_en" : " ' + str(
                device.device.max_all_en) + ' " , "min_all_en" : " ' + str(
                device.device.min_all_en) + ' " , "sb_ch" : " ' + str(
                device.device.sb_ch) + ' " , "sb_dis" : " ' + str(
                device.device.sb_dis) + ' " , "ch_eff" :  " ' + str(
                device.device.ch_eff) + ' " , "dis_eff": " ' + str(
                device.device.dis_eff) + ' " , "v2g" : " ' + str(device.v2g) + ' "}}'
            mex.body = message
            mex.metadata = time
            return mex

    ##############################################################
    # METHOD NOT USED. MAYBE USEFULL IN  FUTURE IMPLEMENTATION   #
    ##############################################################
    """@classmethod
    def ev_arrival(cls, device, time, protocol_version):

      
        Args:
            device:
            time:
            protocol_version:
   
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "EV_ARRIVAL CAPACITY " + device.device.capacity + " MAX_CH_POW_AC " + \
                      device.device.max_ch_pow_ac + " MAX_CH_POW_CC " + device.device.max_ch_pow_cc + " MAX_ALL_EN " + \
                      device.device.max_all_en + " MIN_ALL_EN " + device.device.min_all_en + " SB_CH " + \
                      device.device.sb_ch + " CH_EFF " + device.device.ch_eff + " SOC_AT_ARRIVAL " + \
                      device.Soc_at_arrival + " PLANNED_DEPARTURE_TIME " + device.planned_departure_time + \
                      " ARRIVAL_TIME " + device.actual_arrival_time + " V2G " + device.v2g + " TARGET_SOC " + \
                      device.target_soc
            mex.body = message

            return mex

        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "EV_ARRIVAL" , "capacity" : " ' + str(
                device.device.capacity) + ' " , "max_ch_pow_ac" : " ' + str(
                device.device.max_ch_pow_ac) + ' " , "max_ch_pow_cc" : " ' + str(
                device.device.max_ch_pow_cc) + ' " , "max_all_en" : " ' + str(
                device.device.max_all_en) + ' " , "min_all_en" : " ' + str(
                device.device.min_all_en) + ' " , "sb_ch" : " ' + str(
                device.device.sb_ch) + ' " , "ch_eff" :  " ' + str(
                device.device.ch_eff) + ' " , "soc_at_arrival": " ' + str(
                device.Soc_at_arrival) + ' " , "planned_departure_time" : " ' + str(
                device.planned_departure_time) + ' " , "arrival_time" : " ' + str(
                device.actual_arrival_time) + ' " , "v2g" : " ' + str(
                device.v2g) + ' " , "target_soc" : " ' + str(device.target_soc) + ' " }}'
            mex.body = message
            mex.metadata = time
            return mex

    ##############################################################
    # METHOD NOT USED. MAYBE USEFULL IN  FUTURE IMPLEMENTATION   #
    ##############################################################
    @classmethod
    def ev_departure(cls, device, time, protocol_version):
     
        Args:
            device:
            time:
            protocol_version:
        
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "EV_DEPARTURE CAPACITY " + device.device.capacity + " MAX_CH_POW_AC " + device.device.max_ch_pow_ac + " MAX_CH_POW_CC " + device.device.max_ch_pow_cc + " MAX_ALL_EN " + device.device.max_all_en + " MIN_ALL_EN " + device.device.min_all_en + " SB_CH " + device.device.sb_ch + " CH_EFF " + device.device.ch_eff + " SOC_AT_ARRIVAL " + device.Soc_at_arrival + " PLANNED_DEPARTURE_TIME " + device.planned_departure_time + " ARRIVAL_TIME " + device.actual_arrival_time + " V2G " + device.v2g + " TARGET_SOC " + device.target_soc
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "EV_DEPARTURE" , "capacity" : " ' + str(
                device.device.capacity) + ' " , "max_ch_pow_ac" : " ' + str(
                device.device.max_ch_pow_ac) + ' " , "max_ch_pow_cc" : " ' + str(
                device.device.max_ch_pow_cc) + ' " , "max_all_en" : " ' + str(
                device.device.max_all_en) + ' " , "min_all_en" : " ' + str(
                device.device.min_all_en) + ' " , "sb_ch" : " ' + str(
                device.device.sb_ch) + ' " , "ch_eff" :  " ' + str(
                device.device.ch_eff) + ' " , "soc_at_arrival": " ' + str(
                device.Soc_at_arrival) + ' " , "planned_departure_time" : " ' + str(
                device.planned_departure_time) + ' " , "arrival_time" : " ' + str(
                device.actual_arrival_time) + ' " , "v2g" : " ' + str(
                device.v2g) + ' " , "target_soc" : " ' + str(device.target_soc) + ' " }}'
            mex.body = message
            mex.metadata = time
            return mex
    """
    #################################################
    # This Method manages "create_Battery" message. #
    #################################################
    @classmethod
    def create_Battery(cls, device, time, protocol_version):
        """
        This method creates the Create Battery message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_BATTERY " + "[" + str(device.house) + "]:[" + str(
                device.device.id) + "] " + device.device.capacity + " " + device.device.max_ch_pow_ac + " " + device.device.max_ch_pow_cc + " " + device.device.max_all_en + " " + device.device.min_all_en + " " + device.device.sb_ch + " " + device.device.ch_eff + " " + device.Soc_at_arrival + " " + device.start_time + " " + device.end_time
            mex.body = message

            return mex

        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_BATTERY" , "capacity" : " ' + str(
                device.device.capacity) + ' " , "max_ch_pow_ac" : " ' + str(
                device.device.max_ch_pow_ac) + ' " , "max_ch_pow_cc" : " ' + str(
                device.device.max_ch_pow_cc) + ' " , "max_all_en" : " ' + str(
                device.device.max_all_en) + ' " , "min_all_en" : " ' + str(
                device.device.min_all_en) + ' " , "sb_ch" : " ' + str(
                device.device.sb_ch) + ' " , "ch_eff" :  " ' + str(
                device.device.ch_eff) + ' " , "soc_at_arrival": " ' + str(
                device.Soc_at_arrival) + ' " , "start_time" : " ' + str(
                device.start_time) + ' " , "end_time" : " ' + str(device.end_time) + ' " }}'
            mex.body = message
            mex.metadata = time
            return mex

    ##################################################
    # This Method manages "create_producer" message. #
    ##################################################
    @classmethod
    def create_producer(cls, device, time, protocol_version):
        """
        This method creates the Create Producer message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_PRODUCER [" + str(device.house) + "]:[" + str(device.device.id) + "] " + str(time)
            mex.body = message
            return mex
        else:

            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "CREATE_PRODUCER","type" : "PV","id" : "[' + str(
                device.house) + ']:[' + str(device.device.id) + ']"}}'
            mex.body = message
            mex.metadata = time
            return mex

    #######################################
    # This Method manages "Load" message. #
    #######################################
    @classmethod
    def create_load(cls, device, time, protocol_version):
        """
        This method creates the Create Load message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        mydir = Configuration.parameters['user_dir']
        web_url = Configuration.parameters['web_url']
        if protocol_version == "1.0":
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "LOAD [" + str(device.house) + "]:[" + str(device.device.id) + "] 1 " + str(
                device.est) + " " + str(device.lst) + " " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/" + str(
                mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:

            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = ' {"message" :  {"subject" : "LOAD", "id" : "[' + str(device.house) + ']:[' + str(
                device.device.id) + ']", "sequence" : "1", "est" : " ' + str(
                device.est) + ' ", "lst" : " ' + str(
                device.lst) + ' ","profile" : "' + web_url + '/' + cls.realpath + "/" + str(
                mydir) + '/' + str(device.profile) + ' "}} '
            mex.body = message
            mex.metadata = time
            return mex

    ##################################################
    # This Method manages "update_producer" message. #
    ##################################################
    @classmethod
    def update_producer(cls, device, time, protocol_version):
        """
        This method creates the Update Producer message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        web_url = Configuration.parameters['web_url']
        mydir = Configuration.parameters['user_dir']
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "PREDICTION_UPDATE [" + str(device.house) + "]:[" + str(device.device.id) + "]  " + str(web_url) + "/" + cls.realpath + "/" + str(mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "PREDICTION_UPDATE","type" : "PV","id" : "[' + str(
                device.house) + ']:[' + str(
                device.device.id) + ']","profile" : "' + web_url + '/' + cls.realpath + "/" + str(
                mydir) + '/' + str(device.profile) + ' "}}'
            mex.body = message
            mex.metadata = time
            return mex

    ##############################################
    # This Method manages "delete_load" message. #
    ##############################################
    @classmethod
    def delete_load(cls, device, time, protocol_version):
        """
        This method creates the Delete load message.
        Args:
            device: Device the message refers to.
            time: Simulation Time.
            protocol_version: Distinguish between schedulers.
        """
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "DELETE_LOAD [" + str(device.house) + "]:[" + str(device.device.id) + "] " + str(
                device.consumption) + " " + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)

            message = '{ "message":  {"subject": "DELETE_LOAD", "id": "[' + str(device.house) + ']:[' + str(
                device.device.id) + ']" , "energy": " ' + str(
                device.consumption) + ' ", "producer" : " ' + str(device.panel) + ' " }} '
            mex.body = message
            mex.metadata = time
            return mex
