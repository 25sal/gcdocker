
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime, timedelta
import externalSourceAgent as es
import csv
import yaml
from yaml import Loader
from sys import path
from configure import Configuration

path.append(".")
"""
dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = dir1.split("/")
dir1 = ""
for i in range(1,len(dir2)-1):
    dir1 = dir1 +"/"+ dir2[i]
"""
abilitation = False


def calculateTime(file):
    dirPath2 = Configuration.parameters['current_sim_di'] + "/Inputs/" + file
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

    @classmethod
    def end(cls, actual_time):

        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "SIMULATION END " + str(actual_time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "SIMULATION_END", "simulation_time": " """ + str(
                actual_time) + """ "}}"""
            mex.body = message
            mex.metadata = "0"
            return mex

    @classmethod
    def energyCost(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            name = cls.basejid.split('@')[0]
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "ENERGY_COST [0] " + "http://" + str(url) + "/~gcdemo/" + cls.realpath + "/" + str(
                es.mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "ENERGY_COST",id: "[0]","profile" : "http://parsec2.unicampania.it/~gcdemo/' + cls.realpath + "/" + str(
                es.mydir) + '/' + str(device.profile) + '"}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    @classmethod
    def energyCostProducer(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            name = cls.basejid.split('@')[0]
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "ENERGY_COST [" + str(device.house) + "]:[" + str(device.device.id) + "] " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/Simulations/" + str(es.mydir) + "/" + str(
                device.energycost) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = '{"message" : {"subject" : "ENERGY_COST",id: "["' + str(device.house) + '"]:["' + str(
                device.device.id) + '"]","profile" : "http://parsec2.unicampania.it/~gcdemo/' + cls.realpath + "/" + str(
                es.mydir) + '/' + str(device.energycost) + '"}}'
            mex.body = message
            mex.metadata = '0'
            return mex

    @classmethod
    def energyMix(cls, device, time, protocol_version):
        url = cls.basejid.split('@')[1]
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "ENERGY_MIX " + "http://" + str(url) + "/~gcdemo/" + cls.realpath + "/" + str(
                es.mydir) + "/" + str(
                device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "ENERGY_MIX","profile" : "http://parsec2.unicampania.it/~gcdemo/""" + cls.realpath + "/" + str(
                es.mydir) + """/""" + str(device.profile) + """ "}}"""
            mex.body = message
            mex.metadata = '0'
            return (mex)

    @classmethod
    def neighborhood(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP [99] " + str(device.peakload) + " " + time
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "CREATE_ENERGY_GROUP","powerpeak" : " """ + str(
                device.peakload) + """ "}}"""
            mex.body = message
            mex.metadata = '0'
            return mex

    @classmethod
    def house(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP [" + str(device.id) + "] " + str(device.peakload) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "CREATE_ENERGY_GROUP", "id" : " """ + str(
                device.id) + """ ", "powerpeak" : " """ + str(device.peakload) + """ "}}"""
            mex.body = message
            mex.metadata = '0'
            return mex

    @classmethod
    def chargingstation(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_ENERGY_GROUP  [" + str(device.id) + "] " + str(device.peakload) + " " + str(time)
            mex.body = message
            return (mex)
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "CREATE_ENERGY_GROUP", "id" : " """ + str(
                device.id) + """ ", "powerpeak" : " """ + str(device.peakload) + """ ", "numcp" : " """ + str(
                device.numcp) + """ "}}"""
            mex.body = message
            mex.metadata = '0'
            return mex

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
            message = """{"message" : {"subject" : "CREATE_ENERGY_GROUP", "id" : "[""" + str(
                device.houseid) + """]:[""" + str(device.id) + """]", "connectors_type" : " """ + str(
                device.connection_type) + """ ", "powerpeak" : " """ + str(device.peakload) + """ "}}"""
            mex.body = message
            mex.metadata = '0'
            return mex

    @classmethod
    def heatercooler(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "HC [" + str(device.house) + "]:[" + str(device.device.id) + "] 0 " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/" + str(es.mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return (mex)
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "HC","id" : "[""" + str(device.house) + """]:[""" + str(
                device.device.id) + """]","profile" : "http://parsec2.unicampania.it/~gcdemo/""" + cls.realpath + "/" + str(
                es.mydir) + """/""" + str(device.profile) + """ "}}"""
            mex.body = message
            mex.metadata = time
            return mex

    @classmethod
    def background(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "BG  [" + str(device.house) + "]:[" + str(device.device.id) + "] 0 " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/" + str(es.mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:

            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "BG","id" : "[""" + str(device.house) + """]:[""" + str(
                device.device.id) + """]","profile" : "http://parsec2.unicampania.it/~gcdemo/""" + cls.realpath + "/" + str(
                es.mydir) + """/""" + str(device.profile) + """ "}}"""
            mex.body = message
            mex.metadata = time
            return (mex)

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
            message = """{"message" : {"subject" : "EV", "capacity" : " """ + str(
                device.device.capacity) + """ " , "max_ch_pow_ac" : " """ + str(
                device.device.max_ch_pow_ac) + """ " , "max_ch_cc" : " """ + str(
                device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(
                device.device.max_all_en) + """ " , "min_all_en" : " """ + str(
                device.device.min_all_en) + """ " , "sb_ch" : " """ + str(
                device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(
                device.device.ch_eff) + """ " , "soc_at_arrival": " """ + str(
                device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(
                device.planned_departure_time) + """ " , "arrival_time" : " """ + str(
                device.actual_arrival_time) + """ " , "v2g" : " """ + str(
                device.v2g) + """ " , "target_soc" : " """ + str(device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return (mex)

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

            message = """{"message" : {"subject" : "EV" , "id" : "[""" + str(
                device.device.id) + """]", "soc_at_arrival": " """ + str(
                device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(
                device.planned_departure_time) + """ " , "arrival_time" : " """ + str(
                device.actual_arrival_time) + """ " ,"charging_point" : "[""" + str(device.house) + """]:[""" + str(
                device.device.cp) + """]", "v2g" : " """ + str(device.v2g) + """ " , "target_soc" : " """ + str(
                device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return (mex)

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
            message = """{"message" : {"subject" : "CREATE_EV" , "id" : "[""" + str(
                device.device.id) + """]", "capacity" : " """ + str(
                device.device.capacity) + """ " , "max_ch_pow_ac" : " """ + str(
                device.device.max_ch_pow_ac) + """ " , "max_ch_pow_cc" : " """ + str(
                device.device.max_ch_pow_cc) + """ " , "max_dis_pow_ac" : " """ + str(
                device.device.max_dis_pow_ac) + """ " , "max_dis_pow_cc" : " """ + str(
                device.device.max_dis_pow_cc) + """ " , "max_all_en" : " """ + str(
                device.device.max_all_en) + """ " , "min_all_en" : " """ + str(
                device.device.min_all_en) + """ " , "sb_ch" : " """ + str(
                device.device.sb_ch) + """ " , "sb_dis" : " """ + str(
                device.device.sb_dis) + """ " , "ch_eff" :  " """ + str(
                device.device.ch_eff) + """ " , "dis_eff": " """ + str(
                device.device.dis_eff) + """ " , "v2g" : " """ + str(device.v2g) + """ "}}"""
            mex.body = message
            mex.metadata = time
            return mex

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
            message = """{"message" : {"subject" : "EV_ARRIVAL" , "capacity" : " """ + str(
                device.device.capacity) + """ " , "max_ch_pow_ac" : " """ + str(
                device.device.max_ch_pow_ac) + """ " , "max_ch_pow_cc" : " """ + str(
                device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(
                device.device.max_all_en) + """ " , "min_all_en" : " """ + str(
                device.device.min_all_en) + """ " , "sb_ch" : " """ + str(
                device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(
                device.device.ch_eff) + """ " , "soc_at_arrival": " """ + str(
                device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(
                device.planned_departure_time) + """ " , "arrival_time" : " """ + str(
                device.actual_arrival_time) + """ " , "v2g" : " """ + str(
                device.v2g) + """ " , "target_soc" : " """ + str(device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return mex

    @classmethod
    def ev_departure(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "EV_DEPARTURE CAPACITY " + device.device.capacity + " MAX_CH_POW_AC " + device.device.max_ch_pow_ac + " MAX_CH_POW_CC " + device.device.max_ch_pow_cc + " MAX_ALL_EN " + device.device.max_all_en + " MIN_ALL_EN " + device.device.min_all_en + " SB_CH " + device.device.sb_ch + " CH_EFF " + device.device.ch_eff + " SOC_AT_ARRIVAL " + device.Soc_at_arrival + " PLANNED_DEPARTURE_TIME " + device.planned_departure_time + " ARRIVAL_TIME " + device.actual_arrival_time + " V2G " + device.v2g + " TARGET_SOC " + device.target_soc
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "EV_DEPARTURE" , "capacity" : " """ + str(
                device.device.capacity) + """ " , "max_ch_pow_ac" : " """ + str(
                device.device.max_ch_pow_ac) + """ " , "max_ch_pow_cc" : " """ + str(
                device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(
                device.device.max_all_en) + """ " , "min_all_en" : " """ + str(
                device.device.min_all_en) + """ " , "sb_ch" : " """ + str(
                device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(
                device.device.ch_eff) + """ " , "soc_at_arrival": " """ + str(
                device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(
                device.planned_departure_time) + """ " , "arrival_time" : " """ + str(
                device.actual_arrival_time) + """ " , "v2g" : " """ + str(
                device.v2g) + """ " , "target_soc" : " """ + str(device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return mex

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
            message = """{"message" : {"subject" : "CREATE_BATTERY" , "capacity" : " """ + str(
                device.device.capacity) + """ " , "max_ch_pow_ac" : " """ + str(
                device.device.max_ch_pow_ac) + """ " , "max_ch_pow_cc" : " """ + str(
                device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(
                device.device.max_all_en) + """ " , "min_all_en" : " """ + str(
                device.device.min_all_en) + """ " , "sb_ch" : " """ + str(
                device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(
                device.device.ch_eff) + """ " , "soc_at_arrival": " """ + str(
                device.Soc_at_arrival) + """ " , "start_time" : " """ + str(
                device.start_time) + """ " , "end_time" : " """ + str(device.end_time) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return mex

    @classmethod
    def create_producer(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "CREATE_PRODUCER [" + str(device.house) + "]:[" + str(device.device.id) + "] " + str(time)
            mex.body = message
            return mex
        else:

            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "CREATE_PRODUCER","type" : "PV","id" : "[""" + str(
                device.house) + """]:[""" + str(device.device.id) + """]"}}"""
            mex.body = message
            mex.metadata = time
            return mex

    @classmethod
    def create_load(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            url = cls.basejid.split('@')[1]
            mex = Message(to=cls.basejid + "/actormanager")
            message = "LOAD [" + str(device.house) + "]:[" + str(device.device.id) + "]:[1] 1 " + str(
                device.est) + " " + str(device.lst) + " " + "http://" + str(
                url) + "/~gcdemo/" + cls.realpath + "/" + str(
                es.mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:

            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """ {"message" :  {"subject" : "LOAD", "id" : "[""" + str(device.house) + """]:[""" + str(
                device.device.id) + """]:[1]", "sequence" : "1", "est" : " """ + str(
                device.est) + """ ", "lst" : " """ + str(
                device.lst) + """ ","profile" : "http://parsec2.unicampania.it/~gcdemo/""" + cls.realpath + "/" + str(
                es.mydir) + """/""" + str(device.profile) + """ "}} """
            mex.body = message
            mex.metadata = time
            return mex

    @classmethod
    def update_producer(cls, device, time, protocol_version):
        url = cls.basejid.split('@')[1]
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            message = "PREDICTION_UPDATE [" + str(device.house) + "]:[" + str(
                device.device.id) + "]  " + "http://" + str(url) + "/~gcdemo/" + cls.realpath + "/" + str(
                es.mydir) + "/" + str(device.profile) + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)
            message = """{"message" : {"subject" : "PREDICTION_UPDATE","type" : "PV","id" : "[""" + str(
                device.house) + """]:[""" + str(
                device.device.id) + """]","profile" : "http://parsec2.unicampania.it/~gcdemo/""" + cls.realpath + "/" + str(
                es.mydir) + """/""" + str(device.profile) + """ "}}"""
            mex.body = message
            mex.metadata = time
            return mex

    @classmethod
    def delete_load(cls, device, time, protocol_version):
        if protocol_version == "1.0":
            mex = Message(to=cls.basejid + "/actormanager")
            # message="DELETE_LOAD ["+str(device.house)+"]:["+str(device.device.id)+"] " + str(device.consumption) + " "+ str(device.panel) + " " + str(time)
            message = "DELETE_LOAD [" + str(device.house) + "]:[" + str(device.device.id) + "]:[1] " + str(
                device.consumption) + " " + " " + str(time)
            mex.body = message
            return mex
        else:
            mex = Message(to=cls.basejid + "/" + cls.jid)

            message = """{ "message":  {"subject": "DELETE_LOAD", "id": "[""" + str(device.house) + """]:[""" + str(
                device.device.id) + """]:[1]" , "energy": " """ + str(
                device.consumption) + """ ", "producer" : " """ + str(device.panel) + """ " }} """
            mex.body = message
            mex.metadata = time
            return mex


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


class dispatcher(Agent):

    def __init__(self, address, passw):
        super(dispatcher, self).__init__(address, passw)
        global abilitation
        global firstTime
        firstTime = True
        abilitation = False

    class disRecvBehav(PeriodicBehaviour):
        async def run(self):
            print("DisRecvBehav running")
            global abilitation
            msg = await self.receive(timeout=40)
            try:
                if msg.body == "start":
                    print("Message received with content: {}".format(msg.body))
                    abilitation = True

                elif msg.body == "stop":
                    print("Message received with content: {}".format(msg.body))
                    abilitation = False
                else:
                    print("Did not received any message after 40 seconds")
            except:
                None

    class consumeEvent(PeriodicBehaviour):

        async def onstart(self):
            print("A ConsumeEvent queue is Starting...")

        async def run(self):
            global firstTime
            global abilitation
            global protocol_version
            finish = True
            WasEnable = False
            with open("config.yml", 'r') as ymlfile:
                cfg = yaml.load(ymlfile, Loader=Loader)
            protocol_version = cfg['config']['protocol']
            date = cfg['config']['date'] + " 00:00:00"
            datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
            timestamp = str(datetime.timestamp(datetime_object)).split(".")[0]
            completed = 0
            total = es.sharedQueue.qsize()
            percent = 0
            deletedList = []
            with open("config.yml", 'r') as ymlfile:
                cfg = yaml.load(ymlfile, Loader=Loader)
            path = cfg['config']['simulation_dir']
            sim = cfg['config']['simulation']
            path = path + "/" + sim
            with open(path + "/Simulations/" + es.mydir + "/output/output.txt", "w+") as file:
                finish = 0
                while (finish == 0):
                    next2 = es.sharedQueue.get()
                    print(next2[2].type)
                    if (next2[2].type == "neighborhood"):
                        message = MessageFactory.neighborhood(next2[2], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[2].type == "house":
                        message = MessageFactory.house(next2[2], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                        if next2[2].numcp != 0:
                            message = MessageFactory.chargingstation(next2[2], timestamp, protocol_version)
                            await self.send(message)
                            file.write(">>> " + message.body + "\n")
                            file.flush()

                    elif next2[2].type == "chargingStation":
                        message = MessageFactory.chargingstation(next2[2], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[2].type == "chargingPoint":
                        message = MessageFactory.chargingpoint(next2[2], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[2].type == "energy_cost":
                        message = MessageFactory.energyCost(next2[2], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[2].type == "energy_mix":
                        message = MessageFactory.energyMix(next2[2], timestamp, protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[2].type == "EV" and next2[2].device.type == "CREATE_EV":
                        next2[2].device.type = "EV_BOOKING"
                        message = MessageFactory.create_ev(next2[2], next2[0], protocol_version)
                        await self.send(message)
                        file.write(message.body + "\n")
                        file.flush()
                    elif next2[2].type == "heatercooler":
                        print("condiz")
                        message = MessageFactory.heatercooler(next2[2], next2[0], protocol_version)
                        await self.send(message)
                        print("inviato")
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif next2[2].type == "background":
                        message = MessageFactory.background(next2[2], next2[0], protocol_version)
                        print(protocol_version)
                        await self.send(message)
                    else:
                        finish = 1
                        es.sharedQueue.put((int(next2[0]), int(next2[1]), next2[2]))

                    file.write(next2[2].type + "\n")
                    file.flush()

                while abilitation and finish:

                    # time.sleep(2)
                    # if(firstTime):
                    #    f=open(path+"/output/output.txt", "w+")
                    #    firstTime=False
                    WasEnable = True
                    next2 = es.sharedQueue.get()
                    file.write(next2[2].device.type + "\n")
                    file.flush()
                    nextload = next2[2]
                    actual_time = next2[0]

                    try:
                        providedby = next2[3]
                    except:
                        None

                    with open("./time.txt", "w") as f2:
                        f2.write(str(next2[0]))
                        f2.close()
                    completed += 1
                    print(nextload)
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
                        es.sharedQueue.put((int(nextload.creation_time), int(next2[1]), nextload))
                        file.flush()
                    elif nextload.device.type == "Producer" and nextload.type == "LoadUpdate":
                        message = MessageFactory.update_producer(nextload, next2[0], protocol_version)
                        await self.send(message)
                        msg2 = await self.receive(timeout=3)
                        if nextload.count < 2:
                            nextload.creation_time = int(nextload.creation_time) + 21600
                            nextload.count += 1
                            es.sharedQueue.put((int(nextload.creation_time), int(next2[1]), nextload))
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

                        print(message.body)
                        # msg2 = await self.receive()
                        # time.sleep(4)
                        messageFromScheduler = None
                        if protocol_version == "1.0":
                            while isinstance(messageFromScheduler, type(None)):
                                print("sono in attesa di un messaggio")
                                messageFromScheduler = await self.receive(timeout=20)
                            while messageFromScheduler.body.split(" ")[0] != "SCHEDULED":
                                print("messaggio:" + messageFromScheduler.body)
                                try:
                                    print(messageFromScheduler.body)
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
                                    with open(path + "/Simulations/" + es.mydir + "/inputs/" + nextload.profile,
                                              "r") as f:
                                        with open(path + "/Simulations/" + es.mydir + "/output/" + nextload.profile,
                                                  "w") as f2:
                                            reader = csv.reader(f)
                                            writer = csv.writer(f2, delimiter=' ')
                                            print(nextload.profile)
                                            data = next(reader)
                                            absolute = int(data[0].split(" ")[0])
                                            print(absolute)
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

                                    es.sharedQueue.put((int(newTime), int(es.count), mydel))
                                    es.count += 1
                                    print(es.count)
                                    file.write("<<< " + messageFromScheduler.body + "\r\n")
                                    file.flush()
                                    # time.sleep(2)


                                except:
                                    print("unrecognized Message")
                                messageFromScheduler = await self.receive()
                                while (isinstance(messageFromScheduler, type(None))):
                                    messageFromScheduler = await self.receive(timeout=20)
                                    print("attendo")
                                print("messaggio:" + messageFromScheduler.body)

                            file.write("<<< " + messageFromScheduler.body + "\r\n")
                            file.flush()
                        else:
                            messageFromScheduler = await self.receive(timeout=20)
                            while not isinstance(messageFromScheduler, type(None)):
                                print(messageFromScheduler.body)
                                if messageFromScheduler.body == "AckMessage":
                                    print("Ack Received")

                                else:
                                    try:
                                        delta = calculateTime(nextload.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                        # es.sharedQueue.put((newTime,es.count,es.eventDelete(nextload.device,nextload.house,messageFromScheduler.body.split(" ")[2],messageFromScheduler.body.split(" ")[2],newTime,nextload.profile,"delete"),messageFromScheduler.body.split(" ")[4]))

                                        mydel = es.eventDelete(nextload.device, nextload.house, newTime,
                                                               calculate_consum(nextload.profile),
                                                               messageFromScheduler.body.split(" ")[5])

                                        path = Configuration.parameters['current_sim_dir']
                                        with open(path + "/Simulations/" + es.mydir + "/inputs/" + nextload.profile,
                                                  "r") as f:
                                            with open(path + "/Simulations/" + es.mydir + "/output/" + nextload.profile,
                                                      "w") as f2:
                                                reader = csv.reader(f)
                                                writer = csv.writer(f2, delimiter=' ')
                                                print(nextload.profile)
                                                data = next(reader)
                                                absolute = int(data[0].split(" ")[0])
                                                print(absolute)
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

                                        es.sharedQueue.put((int(newTime), int(es.count), mydel))
                                        es.count += 1
                                        print(es.count)
                                        file.write(">>> " + message.body + "\n")

                                        file.write("<<< " + messageFromScheduler.body + "\r\n")
                                        file.flush()
                                        # time.sleep(2)

                                    except Exception as e:
                                        print(e)
                                messageFromScheduler = await self.receive(timeout=20)

                    elif nextload.type == "delete":
                        if nextload.device.id not in deletedList:
                            deletedList.append(nextload.device.id)
                            message = MessageFactory.delete_load(nextload, next2[0], protocol_version)
                            await self.send(message)
                            # msg2 = await self.receive(timeout=3)
                            file.write(">>> " + message.body + "\n")
                            file.flush()


                    # elif(nextload.type == "EV" and nextload.planned_arrival_time == '0'):
                    elif nextload.type == "EV" and nextload.device.type == "EV_ARRIVAL":
                        nextload.device.type = "EV_DEPARTURE"
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()

                    # elif(nextload.type == "EV" and nextload.planned_arrival_time != '0' and next2[0] == nextload.creation_time):
                    elif nextload.type == "EV" and nextload.device.type == "EV_BOOKING":
                        nextload.device.type = "EV_ARRIVAL"
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(message.body + "\n")
                        file.flush()

                    # elif (nextload.type == "EV" and nextload.planned_arrival_time != '0' and next2[0] != nextload.creation_time):
                    elif nextload.type == "EV" and nextload.device.type == "EV_DEPARTURE":
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.type == "heatercooler":
                        print("condiz")
                        message = MessageFactory.heatercooler(nextload, next2[0], protocol_version)
                        await self.send(message)
                        print("inviato")
                        file.write(">>> " + message.body + "\n")
                        file.flush()
                    elif nextload.type == "background":
                        message = MessageFactory.background(nextload, next2[0], protocol_version)
                        print(protocol_version)
                        await self.send(message)

                        file.write(">>> " + message.body + "\n")
                        file.flush()

                    if es.sharedQueue.empty():

                        if protocol_version == "2.0":

                            messageFromScheduler = await self.receive(timeout=10)
                            while not isinstance(messageFromScheduler, type(None)):
                                if messageFromScheduler.body == "AckMessage":
                                    print("Ack Received")
                                else:
                                    try:
                                        # print(messageFromScheduler.body)
                                        delta = calculateTime(nextload.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3]) + int(delta))
                                        # es.sharedQueue.put((newTime,es.count,es.event(nextload.device,nextload.house,messageFromScheduler.body.split(" ")[2],messageFromScheduler.body.split(" ")[2],newTime,nextload.profile,"delete"),messageFromScheduler.body.split(" ")[4]))
                                        mydel = es.eventDelete(nextload.device, nextload.house, newTime,
                                                               calculate_consum(nextload.profile),
                                                               messageFromScheduler.body.split(" ")[4])

                                        with open(path + "/Simulations/" + es.mydir + "/inputs/" + nextload.profile,
                                                  "r") as f:
                                            with open(path + "/Simulations/" + es.mydir + "/output/" + nextload.profile,
                                                      "w") as f2:
                                                reader = csv.reader(f)
                                                writer = csv.writer(f2, delimiter=' ')
                                                print(nextload.profile)
                                                data = next(reader)
                                                absolute = int(data[0].split(" ")[0])
                                                print(absolute)
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

                                        es.sharedQueue.put((int(newTime), int(es.count), mydel))
                                        es.count += 1
                                        file.write(">>> " + message.body + "\n")
                                        file.write("<<< " + messageFromScheduler.body + "\r\n")
                                        file.flush()

                                    except:
                                        print("unrecognized Message")
                                messageFromScheduler = await self.receive(timeout=10)
                    if es.sharedQueue.empty():
                        message = MessageFactory.end(actual_time)
                        file.write(">>> " + message.body + "\n")

                        file.flush()
                        file.close()
                        finish = False
                        print("Simulazione terminata.")

                if WasEnable:
                    print("Ho rilevato un segnale di stop")
            if finish == False:
                message = MessageFactory.end(actual_time)
                await self.send(message)
                await self.agent.stop()

    async def setup(self):
        basejid = Configuration.parameters["userjid"]
        start_at = datetime.now() + timedelta(seconds=3)
        print("ReceiverAgent started")
        b = self.disRecvBehav(1, start_at=start_at)
        template = Template()
        template2 = Template()
        template = Template()
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=Loader)
        protocol_version = cfg['config']['protocol']
        if protocol_version == "1.0":
            template2.sender = basejid + "/actormanager"
        else:
            template2.sender = basejid + "/adaptor"
        template.set_metadata("control", "startorstop")
        self.add_behaviour(b, template)
        Behaviour2 = self.consumeEvent(1, start_at=start_at)
        self.add_behaviour(Behaviour2, template2)
