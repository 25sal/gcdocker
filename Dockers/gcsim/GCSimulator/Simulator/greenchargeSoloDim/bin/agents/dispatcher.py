
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

path.append("..")
"""
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = dir1.split("/")
dir1 = ""
for i in range(1,len(dir2)-1):
    dir1 = dir1 +"/"+ dir2[i]
"""
LOGFILE = '/home/gc/simulator/gcdaemon.log'

logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)

#################################################################https://calendar.google.com/calendar/u/0/r#####################################################################
# This function calculates the execution time of a scheduled load. It is used to put DeleteMessage in sharedQueue at the right time. #
######################################################################################################################################

def calculateTime(file):
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


##################################################################################################################
# This Class manages all messages between scheduler and dispatcher. It prepares the messages based on subjects.  #
##################################################################################################################
class MessageFactory:
    realpath = None
    jid = None
    basejid = None
    dir1 = None

    @classmethod
    def init_parameters(cls):
        cls.jid = Configuration.parameters['adaptor']
        cls.basejid = Configuration.parameters['userjid']
        cls.dir1 = Configuration.parameters['current_sim_dir']
        webdir = Configuration.parameters['webdir']
        '''
        webarray = webdir.split("/")
        found = 0
        realpath = ""
        for element in webarray:
            if (found == 1):
                realpath = realpath + "/" + element
            if (element == "public_html"):
                found = 1
        '''
        cls.realpath = webdir

    #######################################
    # This Method manages "End" message.  #
    #######################################
    @classmethod
    def end(cls, actual_time):
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
    @classmethod
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

    ##########################################
    # Method used for Ev arrival, departure  #
    ##########################################
    @classmethod
    def booking_request(cls, device, time, protocol_version):

        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "EV [" + str(
                device.device.id) + "] " + device.Soc_at_arrival + " " + device.planned_departure_time + " " + device.actual_arrival_time + " [" + str(
                device.house) + "]:[" + str(device.device.cp) + "] " + device.v2g + " " + device.target_soc + " " + str(
                time)
            mex.body = message

            return (mex)

        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)

            message = '{"message" : {"subject" : "EV" , "id" : "[' + str(
                device.device.id) + ']", "soc_at_arrival": " ' + str(
                device.Soc_at_arrival) + ' " , "planned_departure_time" : " ' + str(
                device.planned_departure_time) + ' " , "arrival_time" : " ' + str(
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
    @classmethod
    def ev_arrival(cls, device, time, protocol_version):

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

    #################################################
    # This Method manages "create_Battery" message. #
    #################################################
    @classmethod
    def create_Battery(cls, device, time, protocol_version):
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




##################################################################################################
# This method calculates consumption in KW of a load consumer. It is used in the delete message. #
##################################################################################################
def calculate_consum(file):
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
        super(dispatcher, self).__init__(address, passw)
        
        self.abilitation = False

    ##################################################################################
    # This method check periodically if start/stop messages are sent by setupModule. #
    ##################################################################################
    class disRecvBehav(PeriodicBehaviour):
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

                    file.write(next2[1].type + "\n")
                    file.flush()

                ##################################################################################
                # When configuration messages are terminated, continue to consume the others     #
                ##################################################################################
                while self.agent.abilitation and finish:
                    WasEnable = True
                    next2 = es.Entities.next_event()
                    #file.write(next2[1].device.type + "\n")
                    #file.flush()
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
                    if nextload.device.type == "battery":
                        message = MessageFactory.create_Battery(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()

                    elif nextload.type == "load" and nextload.device.type == "Consumer":
                        total += 1
                        message = MessageFactory.create_load(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")

                        messageFromScheduler = None
                        if protocol_version == "1.0":
                            while isinstance(messageFromScheduler, type(None)):
                                logging.debug("sono in attesa di un messaggio")
                                messageFromScheduler = await self.receive(timeout=20)
                            while messageFromScheduler.body.split(" ")[0] != "SCHEDULED":
                                logging.info("messaggio:" + messageFromScheduler.body)
                                try:
                                    logging.debug(messageFromScheduler.body)
                                    delta = calculateTime(nextload.profile)
                                    newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                    # es.sharedQueue.put((newTime,es.count,es.eventDelete(nextload.device,
                                    # nextload.house,messageFromScheduler.body.split(" ")[2],
                                    # messageFromScheduler.body.split(" ")[2],newTime,nextload.profile,"delete"),
                                    # messageFromScheduler.body.split(" ")[4]))

                                    # mydel = es.eventDelete(nextload.device, nextload.house, newTime,
                                    # calculate_consum(nextload.profile),messageFromScheduler.body.split(" ")[4])
                                    mydel = es.eventDelete(nextload.device, nextload.house, newTime,
                                                           calculate_consum(nextload.profile))

                                    # date = cfg['config']['date'] + " 00:00:00"

                                    path = Configuration.parameters['current_sim_dir']
                                    with open(path + "/Results/" +Configuration.parameters['user_dir'] + "/inputs/" + nextload.profile,
                                              "r") as f:
                                        with open(path + "/Results/" + Configuration.parameters['user_dir'] + "/output/" + nextload.profile,
                                                  "w") as f2:
                                            reader = csv.reader(f)
                                            writer = csv.writer(f2, delimiter=' ')
                                            data = next(reader)
                                            absolute = int(data[0].split(" ")[0])
                                            entry = []
                                            entry.append(int(messageFromScheduler.body.split(" ")[3]))
                                            entry.append(data[0].split(" ")[1])
                                            writer.writerow(entry)
                                            for data in reader:
                                                entry = []
                                                entry.append(int(str(data[0].split(" ")[0])) - absolute + int(
                                                    messageFromScheduler.body.split(" ")[3]))
                                                entry.append(str(data[0].split(" ")[1]))
                                                writer.writerow(entry)

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
                                        delta = calculateTime(nextload.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                        mydel = es.eventDelete(nextload.device, nextload.house, newTime,
                                                               calculate_consum(nextload.profile),
                                                               messageFromScheduler.body.split(" ")[5])

                                        path = Configuration.parameters['current_sim_dir']
                                        with open(path + "/Results/" + Configuration.parameters['user_dir'] + "/inputs/" + nextload.profile,
                                                  "r") as f:
                                            with open(path + "/Results/" + Configuration.parameters['user_dir'] + "/output/" + nextload.profile,
                                                      "w") as f2:
                                                reader = csv.reader(f)
                                                writer = csv.writer(f2, delimiter=' ')
                                                data = next(reader)
                                                absolute = int(data[0].split(" ")[0])
                                                entry = []
                                                entry.append(int(messageFromScheduler.body.split(" ")[3]))
                                                entry.append(data[0].split(" ")[1])
                                                writer.writerow(entry)
                                                for data in reader:
                                                    entry = []
                                                    entry.append(int(str(data[0].split(" ")[0])) - absolute + int(
                                                        messageFromScheduler.body.split(" ")[3]))
                                                    entry.append(str(data[0].split(" ")[1]))
                                                    writer.writerow(entry)

                                        es.Entities.enqueue_event(int(newTime),  mydel)
                                      
                                        file.write(">>> " + message.body + "\n")

                                        file.write("<<< " + messageFromScheduler.body + "\r\n")
                                        file.flush()
                                    except Exception as e:
                                        logging.info(e)
                                messageFromScheduler = await self.receive(timeout=20)

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

                    if es.Entities.sharedQueue.empty():

                        if protocol_version == "2.0":

                            messageFromScheduler = await self.receive(timeout=10)
                            while not isinstance(messageFromScheduler, type(None)):
                                if messageFromScheduler.body == "AckMessage":
                                    logging.info("Ack Received")
                                else:
                                    try:
                                        delta = calculateTime(nextload.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                        mydel = es.eventDelete(nextload.device, nextload.house, newTime,
                                                               calculate_consum(nextload.profile),
                                                               messageFromScheduler.body.split(" ")[4])

                                        with open(path + "/Results/" + Configuration.parameters['user_dir'] + "/inputs/" + nextload.profile,
                                                  "r") as f:
                                            with open(path + "/Results/" + Configuration.parameters['user_dir'] + "/output/" + nextload.profile,
                                                      "w") as f2:
                                                reader = csv.reader(f)
                                                writer = csv.writer(f2, delimiter=' ')
                                                logging.info(nextload.profile)
                                                data = next(reader)
                                                absolute = int(data[0].split(" ")[0])
                                                logging.info(absolute)
                                                entry = []
                                                entry.append(int(messageFromScheduler.body.split(" ")[3]))
                                                entry.append(data[0].split(" ")[1])
                                                writer.writerow(entry)
                                                for data in reader:
                                                    entry = []
                                                    entry.append(int(str(data[0].split(" ")[0])) - absolute + int(
                                                        messageFromScheduler.body.split(" ")[3]))
                                                    entry.append(str(data[0].split(" ")[1]))
                                                    writer.writerow(entry)

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




