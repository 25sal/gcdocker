


                                    #################################################################################
                                    #                           __author__ = "Dario Branco"                         #
                                    #                           __version__ = "1.0"                                 #
                                    #                           __maintainer__ = "Dario Branco"                     #
                                    #                           __email__ = "dariobranco94@gmail.com"               #
                                    #                           __status__ = "Production"                           #
                                    #################################################################################



###########################****************** IMPORT LIBRARIES SECTION ************************###################################################


import spade
import time
import asyncio
from datetime import datetime
import aioxmpp
import os
from spade.agent import *
from spade.behaviour import *
import xml.etree.ElementTree as ET
from sys import path
path.append(".")
#dir1 = os.path.dirname(os.path.realpath(__file__))
import multiprocessing
import queue
import threading
import glob
from shutil import copy2
import csv
import shutil
import yaml
from yaml import Loader
import sqlite3
###########################****************** END IMPORT LIBRARIES SECTION ************************###################################################




###########################****************** DEFINE CLASS SECTION ************************###################################################
# ANY DEVICE IS DEFINED BY A A COMPLEX OBJECT

class abstract_device:
    def __init__(self,id = '0', house ='0',type='0',name = '0'):
        self.type = type
        self.id = id
        self.house = house
        self.name = name

class backGroundLoad(abstract_device):
    def __init__(self,id = '0', house = '0', name = '0'):
        self.id = id
        self.house = house
        self.name = name
        self.type = "backgroundLoad"


class heaterCooler(abstract_device):
    def __init__(self,id = '0', house = '0', name = '0'):
        self.id = id
        self.house = house
        self.name = name
        self.type = "heaterCooler"



class EV(abstract_device):
    def __init__(self,id = 0, house = 0, chargingPoint = 0, name = '0', capacity = '0', max_ch_pow_ac = '0', max_ch_pow_cc = '0', max_dis_pow_ac = '0', max_dis_pow_cc = '0', max_all_en = '0', min_all_en = '0', sb_ch = '0', sb_dis = '0', ch_eff = '0', dis_eff = '0'):
        self.cp = chargingPoint
        self.id = id
        self.house = house
        self.name = name
        self.type = "EV"
        self.capacity = capacity
        self.max_ch_pow_ac = max_ch_pow_ac
        self.max_ch_pow_cc = max_ch_pow_cc
        self.max_dis_pow_cc = max_dis_pow_cc
        self.max_dis_pow_ac = max_dis_pow_ac
        self.max_all_en = max_all_en
        self.min_all_en = min_all_en
        self.sb_ch = sb_ch
        self.sb_dis = sb_dis
        self.ch_eff = ch_eff
        self.dis_eff = dis_eff

		

class Battery(abstract_device):
    def __init__(self,id = 0, house = 0, name = '0', capacity = '0', max_ch_pow_ac = '0', max_ch_pow_cc = '0', max_dis_pow = '0', max_all_en = '0', min_all_en = '0', sb_ch = '0', sb_dis = '0', ch_eff = '0', dis_eff = '0'):
        self.id = id
        self.house = house
        self.name = name
        self.type = "battery"
        self.capacity = capacity
        self.max_ch_pow_ac = max_ch_pow_ac
        self.max_ch_pow_cc = max_ch_pow_cc
        self.max_dis_pow = max_dis_pow
        self.max_all_en = max_all_en
        self.min_all_en = min_all_en
        self.sb_ch = sb_ch
        self.sb_dis = sb_dis
        self.ch_eff = ch_eff
        self.dis_eff = dis_eff		
		

class device(abstract_device):
    def __init__(self,id = '0', type = '0', name = '0', house = '0'):
        self.id = id
        self.type = type
        self.name = name
        self.house = house


class abstract_event:
    def __init__(self,device = '0', house = '0', creation_time= '0', type2=0):
        self.device=device
        self.type = type2
        self.creation_time = creation_time
        self.house = house



class eventGeneral(abstract_event):
    def __init__(self,device = '0', house = '0', est = '0', lst= '0', creation_time= '0', profile = '0', type2=0):
        self.device=device
        self.est = est
        self.lst = lst
        self.type = type2
        self.creation_time = creation_time
        self.profile=profile
        self.house = house

class eventDelete(abstract_event):
	def __init__(self,device = '0', house = '0', creation_time= '0', consumption = 0):
		self.device=device
		self.type = "delete"
		self.creation_time = creation_time
		self.house = house
		self.consumption = consumption


class eventEcar(abstract_event):
    def __init__(self,device = '0', house = '0', Soc_at_arrival = '0', booking_time = '0', planned_arrival_time = '0',planned_departure_time = '0', actual_arrival_time = '0', actual_departure_time = '0', target_soc = '0', v2g ='0', priority = '0' ):
        self.device=device
        self.type = "EV"
        self.creation_time = booking_time
        self.house = house
        self.Soc_at_arrival = Soc_at_arrival
        self.planned_arrival_time = planned_arrival_time
        self.planned_departure_time = planned_departure_time
        self.actual_arrival_time = actual_arrival_time
        self.actual_departure_time = actual_departure_time
        self.v2g = v2g
        self.target_soc = target_soc
        self.priority = priority

		
		
class eventBattery(abstract_event):
    def __init__(self,device = '0', house = '0', Soc_at_arrival = '0', booking_time = '0', start_time = '0', end_time = '0', target_soc = '0'):
        self.device=device
        self.type = "BATTERY"
        self.creation_time = booking_time
        self.house = house
        self.Soc_at_arrival = Soc_at_arrival
        self.start_time = start_time
        self.end_time = end_time
        self.target_soc = target_soc





class eventProducer(abstract_event):
    def __init__(self,device = '0', house = '0',est='0',lst='0', creation_time= '0', profile = '0',type2=0, energycost = '0'):
        self.device=device
        self.type = "load"
        self.creation_time = creation_time
        self.profile=profile
        self.house = house
        self.count = 0
        self.energycost = energycost
        self.est = est
        self.lst = lst

class eventBackground(abstract_event):
    def __init__(self,device = '0', house = '0',  creation_time= '0', profile = '0'):
        self.device=device
        self.creation_time = creation_time
        self.profile=profile
        self.house = house
        self.type = "background"

class eventHeaterCooler(abstract_event):
    def __init__(self,device = '0', house = '0',  creation_time= '0', profile = '0'):
        self.device=device
        self.creation_time = creation_time
        self.profile=profile
        self.house = house
        self.type = "heatercooler"

		
class Energy_Cost():
    def __init__(self, type = '0', profile = '0'):
        self.type = "energy_cost"
        self.profile = profile		

class Energy_Mix():
    def __init__(self, type = '0', profile = '0'):
        self.type = "energy_mix"
        self.profile = profile				

		
class Neighborhood():
    def __init__(self, type = '0', peakload = '0'):
        self.type = "neighborhood"
        self.peakload = peakload

class House():
    def __init__(self, type = '0', id = '0', peakload = '0', numcp = 0):
        self.type = "house"
        self.id = id
        self.peakload = peakload
        self.numcp = numcp 


class ChargingStation():
    def __init__(self, type = '0', id = '0', peakload = '0', numcp = 0):
        self.type = "chargingStation"
        self.id = id
        self.peakload = peakload
        self.numcp = numcp 


class ChargingPoint():
    def __init__(self, type = '0', id = '0', houseid = '0', conntype = '0', peakload = '0'):
        self.type = "chargingPoint"
        self.houseid = houseid
        self.id = id
        self.peakload = peakload
        self.connection_type = conntype






###########################****************** END DEFINE CLASS SECTION ************************###################################################




###########################****************** UTIL VARIABLES SECTION ************************###################################################
'''
listDevice = []  #IN THIS LIST WILL BE STORED ALL THE LOADS
listPanels = [] #IN THIS LIST WILL BE STORED ALL THE PRODUCERS
listEvent = []
"""dir1 = os.path.dirname(os.path.realpath(__file__))
dir2 = dir1.split("/")
dir1 = ""
for i in range(1,len(dir2)-1):
    dir1 = dir1 +"/"+ dir2[i]
"""
pathneighbor=0
pathload2= 0
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader = Loader)
date = cfg['config']['date'] + " 00:00:00"
path = cfg['config']['simulation_dir']
simd = cfg['config']['simulation']
path = path + "/" + simd
dir1 = cfg['config']['simulation_dir']
dir1 = dir1 + "/" + simd

datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
workingdir = 0
webdir = cfg['config']['webdir']
sharedQueue = queue.PriorityQueue()
mydir = 0



#codice aggiunto perchè non funzionava la directory web nel dispatcher
date3 = date.split()
newdir2 = date3[0].replace('/','_')
sim_temp2 = newdir2.split("_")
lock1 = False
if(len(sim_temp2[0]) == 1):
	sim_temp2[0] =  "0" + sim_temp2[0]
	lock1 = True
if(len(sim_temp2[1]) == 1 ):
	sim_temp2[1] = "0" + sim_temp2[1]
	lock1 = True

if (lock1):
	newdir2 = sim_temp2[0] + "_" + sim_temp2[1] + "_" + sim_temp2[2]
dirCount1 = 1
while(os.path.exists(dir1+"/Simulations/"+newdir2+"_"+str(dirCount1))):
	dirCount1+=1
workingdir1 = dir1+"/Simulations/"+newdir2+"_"+str(dirCount1)
mydir = workingdir1.split("/")[-1]
#fine codice aggiunto
'''














###########################****************** END UTIL VARIABLES SECTION ************************###################################################



###########################********************** METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################


# createDevicesList() READS FROM A FILE ALL THE DEVICES, SORTS THEM BY TYPE AND APPEND TO RELATED LIST

def createTable():
	global workingdir
	db_filename = workingdir+'/xml/input.db'
	conn = sqlite3.connect(db_filename)
	schema_filename = '../xml/schema.sql'


	with open(schema_filename, 'rt') as f:
	    schema = f.read()
	conn.executescript(schema)
	f = open(workingdir+"/xml/neighborhood.xml", "r")
	fileIntero = f.read()
	root = ET.fromstring(fileIntero)

	for house in root.findall('house'):         #READ XML FILE
		houseId = house.get('id')
		query = "insert into housecs (id) values(?)"
		cursor = conn.cursor()
		cursor.execute(query,(houseId,))

		for user in house.findall('user'):
			userId = user.get('id')
			for deviceElement in user.findall('device'):
				deviceId = deviceElement.find('id').text
				type = deviceElement.find('type').text
				name = deviceElement.find('name').text
				query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,houseId,name,type,type,))

			for OtherElement in user.findall('heatercooler'):
				deviceId = OtherElement.find('id').text
				name = OtherElement.find('name').text
				query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,houseId,name,"heatercooler","N-S Consumer",))


			for OtherElement in user.findall('backgroundload'):
				deviceId = OtherElement.find('id').text
				name = OtherElement.find('name').text
				query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,houseId,name,"backgroundLoad","N-S Consumer",))


			for OtherElement in user.findall('ecar'):
				deviceId = OtherElement.find('id').text
				name = OtherElement.find('name').text

				capacity = OtherElement.find('capacity').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"Capacity",str(capacity),))

				maxchpowac = OtherElement.find('maxchpowac').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"max_ch_pow_ac",str(maxchpowac),))

				maxchpowcc = OtherElement.find('maxchpowcc').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"max_ch_pow_cc",str(maxchpowcc),))

				maxdispow = OtherElement.find('maxdispow').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"max_dis_pow",str(maxdispow),))

				maxallen = OtherElement.find('maxallen').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"max_all_en",str(maxallen),))

				minallen = OtherElement.find('minallen').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"min_all_en",str(minallen),))

				sbch = OtherElement.find('sbch').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"sbch",str(sbch),))

				sbdis = OtherElement.find('sbdis').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"sbdis",str(sbdis),))

				cheff = OtherElement.find('cheff').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"cheff",str(cheff),))

				dis_eff = OtherElement.find('dis_eff').text
				query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"dis_eff",str(dis_eff),))

				query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,houseId,name,"ecar","Prosumer",))

	f = open(workingdir+"/xml/loads.xml", "r")
	fileIntero = f.read();
	root = ET.fromstring(fileIntero)
	for house in root.findall('house'):
		houseId = house.get('id')
		for user in house.findall('user'):
			userId = user.get('id')
			for device in user.findall('device'):
				deviceId = device.find('id').text

				est = device.find('est').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"est",str(est),))

				lst = device.find('lst').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"lst",str(lst),))
				creation_time = device.find('creation_time').text
				type2 = device.find("type").text

				for c in listDevice:
					if(deviceId == c.id and houseId == c.house):
						if(c.type == "Consumer"):
							query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
							cursor = conn.cursor()
							cursor.execute(query,(creation_time,deviceId,"Load",))
						elif(c.type == "Producer"):
							query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
							cursor = conn.cursor()
							cursor.execute(query,(creation_time,deviceId,"Create PV",))

			for device in user.findall('backgroundload'):
				deviceId = device.find('id').text
				query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,("0",deviceId,"Create BG",))

			for device in user.findall('ecar'):
				deviceId = device.find('id').text
				pat = device.find('pat').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"pat",str(pat),))
				pdt = device.find('pdt').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"pdt",str(pdt),))
				aat = device.find('aat').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"aat",str(aat),))
				adt = device.find('adt').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"adt",str(adt),))
				creation_time = device.find('creation_time').text
				soc = device.find('soc').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"soc",str(soc),))
				targetSoc = device.find('targetSoc').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"targetSoc",str(targetSoc),))
				V2G = device.find('V2G').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"V2G",str(V2G),))
				priority = device.find('priority').text
				query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(deviceId,"targpriorityetSoc",str(priority),))
				query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,(creation_time,deviceId,"ECAR event",))

			for device in user.findall('heatercooler'):
				deviceId = device.find('id').text
				query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
				cursor = conn.cursor()
				cursor.execute(query,("0",deviceId,"Create HC",))
	conn.commit()
	conn.close()



def createDevicesList():
    global workingdir
    global count
    global sharedQueue
    timestamp = datetime.timestamp(datetime_object)

    sharedQueue = queue.PriorityQueue()
    count = 0
    print("guarda in " + workingdir)
    f = open(workingdir+"/xml/neighborhood.xml", "r")
    fileIntero = f.read()
    root = ET.fromstring(fileIntero)
    neigh = Neighborhood('neighborhood', root.get('peakLoad2'))
    sharedQueue.put((timestamp,int(count),neigh))
    count+=1
    for energycost in root.findall('energyCost'):
        energycost = Energy_Cost('energyCost', energycost.find('profile').text)
        sharedQueue.put((timestamp,int(count),energycost))
        count+=1
    for energyMix in root.findall('energyMix'):
        energyMix = Energy_Mix('energyMix', energyMix.find('profile').text)
        sharedQueue.put((timestamp,int(count),energyMix))
        count+=1

    #Inserisci qui il codice per la creazione del neighborhood
    for house in root.findall('house'):         #READ XML FILE
        #inserisci qui il codice per la creazione di una house
        houseId = house.get('id')
        housedev = House('house',houseId, house.get('peakLoad'),0)
        
        count+=1
        for user in house.findall('user'):
            userId = user.get('id')
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                c = device(deviceId,type,name, houseId)
                listDevice.append(c)
            for OtherElement in user.findall('heatercooler'):
                print("TROVATO")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = heaterCooler(deviceId, houseId, name)
                listDevice.append(c)

            for OtherElement in user.findall('backgroundload'):
                print("trovatobg")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = backGroundLoad(deviceId, houseId, name)
                listDevice.append(c)
            for OtherElement in user.findall('battery'):
                print("found")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                capacity = OtherElement.find('capacity').text
                maxchpowac = OtherElement.find('maxchpowac').text
                maxchpowcc = OtherElement.find('maxchpowcc').text
                maxdispow = OtherElement.find('maxdispow').text
                maxallen = OtherElement.find('maxallen').text
                minallen = OtherElement.find('minallen').text
                sbch = OtherElement.find('sbch').text
                sbdis = OtherElement.find('sbdis').text
                cheff = OtherElement.find('cheff').text
                dis_eff = OtherElement.find('dis_eff').text
                c = Battery(deviceId, houseId, name,capacity,maxchpowac,maxchpowcc,maxdispow,maxallen,minallen, sbch, sbdis, cheff, dis_eff)
                listDevice.append(c)
				
            for cp in user.findall('ChargingPoint'):
                cpId = cp.get('id')
                cpdev = ChargingPoint('house',houseId,cpId,cp.get('ConnectorsType'), cp.get('peakLoad'))
                #sharedQueue.put((0,int(count),cpdev))
                count+=1
                housedev.numcp += 1
                #inserisci qui il codice per la creazione del Cp
                for OtherElement in cp.findall('ecar'):
                    deviceId = OtherElement.find('id').text
                    name = OtherElement.find('name').text
                    capacity = OtherElement.find('capacity').text
                    maxchpowac = OtherElement.find('maxchpowac').text
                    maxchpowcc = OtherElement.find('maxchpowcc').text
                    maxdispowac = OtherElement.find('maxdispowac').text
                    maxdispowcc = OtherElement.find('maxdispowcc').text

                    maxallen = OtherElement.find('maxallen').text
                    minallen = OtherElement.find('minallen').text
                    sbch = OtherElement.find('sbch').text
                    sbdis = OtherElement.find('sbdis').text
                    cheff = OtherElement.find('cheff').text
                    dis_eff = OtherElement.find('dis_eff').text
                    c = EV(deviceId, houseId,cpId, name,capacity,maxchpowac,maxchpowcc,maxdispowac,maxdispowcc,maxallen,minallen, sbch, sbdis, cheff, dis_eff)
                    listDevice.append(c)
        sharedQueue.put((timestamp,int(count),housedev))
    for house in root.findall('chargingStation'):         #READ XML FILE
        #inserisci qui il codice per la creazione di una cs
        houseId = house.get('id')
        housedev = ChargingStation('house',houseId, house.get('peakLoad'), 0)
        count+=1
        for user in house.findall('user'):
            userId = user.get('id')
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                c = device(deviceId,type,name, houseId)
                listDevice.append(c)
            for OtherElement in user.findall('heatercooler'):
                print("TROVATO")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = heaterCooler(deviceId, houseId, name)
                listDevice.append(c)

            for OtherElement in user.findall('backgroundload'):
                print("trovatobg")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = backGroundLoad(deviceId, houseId, name)
                listDevice.append(c)
            for OtherElement in user.findall('battery'):
                print("found cs")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                capacity = OtherElement.find('capacity').text
                maxchpowac = OtherElement.find('maxchpowac').text
                maxchpowcc = OtherElement.find('maxchpowcc').text
                maxdispow = OtherElement.find('maxdispow').text
                maxallen = OtherElement.find('maxallen').text
                minallen = OtherElement.find('minallen').text
                sbch = OtherElement.find('sbch').text
                sbdis = OtherElement.find('sbdis').text
                cheff = OtherElement.find('cheff').text
                dis_eff = OtherElement.find('dis_eff').text
                c = Battery(deviceId, houseId, name,capacity,maxchpowac,maxchpowcc,maxdispow,maxallen,minallen, sbch, sbdis, cheff, dis_eff)
                listDevice.append(c)
            for cp in user.findall('ChargingPoint'):
                housedev.numcp += 1
                cpId = cp.get('id')
                #cpdev = ChargingPoint('house',houseId,cpId, cp.get('ConnectorsType'), cp.get('peakLoad'))
                #sharedQueue.put((0,int(count),cpdev))
                count+=1
                #inserisci qui il codice per la creazione del Cp
                for OtherElement in cp.findall('ecar'):
                    deviceId = OtherElement.find('id').text
                    name = OtherElement.find('name').text
                    capacity = OtherElement.find('capacity').text
                    maxchpowac = OtherElement.find('maxchpowac').text
                    maxchpowcc = OtherElement.find('maxchpowcc').text
                    maxdispowac = OtherElement.find('maxdispowac').text
                    maxdispowcc = OtherElement.find('maxdispowcc').text

                    maxallen = OtherElement.find('maxallen').text
                    minallen = OtherElement.find('minallen').text
                    sbch = OtherElement.find('sbch').text
                    sbdis = OtherElement.find('sbdis').text
                    cheff = OtherElement.find('cheff').text
                    dis_eff = OtherElement.find('dis_eff').text
                    c = EV(deviceId, houseId,cpId, name,capacity,maxchpowac,maxchpowcc,maxdispowac,maxdispowcc,maxallen,minallen, sbch, sbdis, cheff, dis_eff)
                    listDevice.append(c)
        sharedQueue.put((timestamp,int(count),housedev))

    for fleet in root.findall('fleet'):
        for OtherElement in fleet.findall('ecar'):
                    deviceId = OtherElement.find('id').text
                    name = OtherElement.find('name').text
                    capacity = OtherElement.find('capacity').text
                    maxchpowac = OtherElement.find('maxchpowac').text
                    maxchpowcc = OtherElement.find('maxchpowcc').text
                    maxdispowac = OtherElement.find('maxdispowac').text
                    maxdispowcc = OtherElement.find('maxdispowcc').text

                    maxallen = OtherElement.find('maxallen').text
                    minallen = OtherElement.find('minallen').text
                    sbch = OtherElement.find('sbch').text
                    sbdis = OtherElement.find('sbdis').text
                    cheff = OtherElement.find('cheff').text
                    dis_eff = OtherElement.find('dis_eff').text
                    c = EV(deviceId, -1,-1, name,capacity,maxchpowac,maxchpowcc,maxdispowac,maxdispowcc,maxallen,minallen, sbch, sbdis, cheff, dis_eff)
                    listDevice.append(c)



# END OF createDevicesList()


# createEventList() READS FROM A FILE EVENT INFORMATIONS AND APPEND THEM TO LOADSLIST

def createEventList():
    global workingdir

    f = open(workingdir+"/xml/loads.xml", "r")
    fileIntero = f.read();
    root = ET.fromstring(fileIntero)
    for house in root:
        if(house.tag != 'fleet'):
            houseId = house.get('id')
            # print 'house id ' + houseId
            for user in house.findall('user'):
                userId = user.get('id')
                for device in user.findall('device'):
                    deviceId = device.find('id').text
                    est = device.find('est').text
                    lst = device.find('lst').text
                    creation_time = device.find('creation_time').text
                    type2 = device.find("type").text
                    if(device.find('profile').text.endswith(' ')):
                        profile = device.find('profile').text[:-1]
                        copy2(path+"/Inputs/"+profile, workingdir+"/inputs")
                    else:
                        profile = device.find('profile').text
                        copy2(path+"/Inputs/"+profile, workingdir+"/inputs")

                    for c in listDevice:
                        if(deviceId == c.id and houseId == c.house):
                            if(c.type == "Consumer"):
                                e= eventGeneral(c,houseId,est,lst,creation_time,profile,"load")
                                listEvent.append(e)
                            elif(c.type == "Producer"):
                                energycost = device.find('energy_cost').text
                                copy2(path+"/Inputs/"+profile, workingdir+"/inputs")
                                e= eventProducer(c,houseId,est,lst,creation_time,profile, "load", energycost)
                                listEvent.append(e)
                                #CODICE PROVVISORIO
                                # H = int(creation_time) + 21600
                                # print(H)
                                # print(int(creation_time))
                                # e1= eventGeneral(c,houseId,est,lst,H,profile, "LoadUpdate")
                                # H1 = int(creation_time) + 2*21600
								# print(H1)
                                # e2= eventGeneral(c,houseId,est,lst,H1,profile, "LoadUpdate")
                                # H2 = int(creation_time) + 3*21600
								# print(H2)
                                # e3= eventGeneral(c,houseId,est,lst,H2,profile, "LoadUpdate")
                                # listEvent.append(e1)
                                # listEvent.append(e2)
                                # listEvent.append(e3)
                                # #FineCodiceProvvisorio
                for device in user.findall('backgroundload'):
                    deviceId = device.find('id').text
                    global mydir
                    if (device.find('profile').text.endswith(' ')):
                        profile = device.find('profile').text[:-1]
                        copy2(path+"/Inputs/" + profile, workingdir + "/inputs")
                        copy2(path+"/Inputs/" + profile,path+"/Simulations/"+mydir+"/output/BG/")
                    else:
                        profile = device.find('profile').text
                        copy2(path+"/Inputs/" + profile, workingdir + "/inputs")
                        copy2(path+"/Inputs/" + profile,path+"/Simulations/"+mydir+"/output/BG/")
                    for c in listDevice:
                        if(deviceId == c.id and houseId == c.house):
                            if (c.type == "backgroundLoad"):
                                e = eventBackground(c, houseId,0,profile)
                                listEvent.append(e)
                for device in user.findall('heatercooler'):
                    deviceId = device.find('id').text
                    if (device.find('profile').text.endswith(' ')):
                        profile = device.find('profile').text[:-1]
                        copy2(path+"/Inputs/" + profile, workingdir + "/inputs")
                    else:
                        profile = device.find('profile').text
                        copy2(path+"/Inputs/" + profile, workingdir + "/inputs")
                    for c in listDevice:
                        if (deviceId == c.id and houseId == c.house):
                            if (c.type == "heaterCooler"):
                                e = eventHeaterCooler(c, houseId, 0, profile)
                                listEvent.append(e)
                for device in user.findall('battery'):
                    deviceId = device.find('id').text
                    for c in listDevice:
                        if (deviceId == c.id and houseId == c.house):
                            if (c.type == "battery"):
                                print("found")
                                aat = device.find('startTime').text
                                adt = device.find('endTime').text
                                creation_time = device.find('creation_time').text
                                soc = device.find('soc').text
                                targetSoc = device.find('targetSoc').text
                                e = eventBattery(c, houseId, soc, creation_time, aat, adt, targetSoc)
                                listEvent.append(e)
                for cp in user.findall('ChargingPoint'):
                    for device in cp.findall('ecar'):
                            deviceId = device.find('id').text
                            for c in listDevice:
                                if (deviceId == c.id and houseId == c.house):
                                    if (c.type == "EV"):
                                        pat = device.find('pat').text
                                        pdt = device.find('pdt').text
                                        aat = device.find('aat').text
                                        adt = device.find('adt').text
                                        creation_time = device.find('creation_time').text
                                        soc = device.find('soc').text
                                        targetSoc = device.find('targetSoc').text
                                        V2G = device.find('V2G').text
                                        priority = device.find('priority').text
                                        e = eventEcar(c, houseId, soc, creation_time, pat, pdt, aat, adt, targetSoc, V2G, priority)
                                        listEvent.append(e)
        else:
            for device in house.findall('ecar'):
                            deviceId = device.find('id').text
                            for c in listDevice:
                                if (deviceId == c.id):
                                    if (c.type == "EV"):
                                        pat = device.find('pat').text
                                        pdt = device.find('pdt').text
                                        aat = device.find('aat').text
                                        adt = device.find('adt').text
                                        creation_time = device.find('creation_time').text
                                        soc = device.find('soc').text
                                        targetSoc = device.find('targetSoc').text
                                        V2G = device.find('V2G').text
                                        priority = device.find('priority').text
                                        e = eventEcar(c, -1, soc, creation_time, pat, pdt, aat, adt, targetSoc, V2G, priority)
                                        listEvent.append(e)

def adjustTime():
    global workingdir
    timestamp = datetime.timestamp(datetime_object)
    entry = []
    for e in listEvent:
        if(e.device.type == "Producer" or e.device.type == "Consumer"):
                with open(workingdir+"/inputs/"+e.profile, "r") as f:
                    with open(workingdir+"/inputs/temp"+e.profile, "w") as f2:
                        reader = csv.reader(f)
                        writer = csv.writer(f2, delimiter =' ')
                        for data in reader:
                            entry = []
                            oldtimestamp = datetime.fromtimestamp(int(data[0].split(" ")[0]))
                            datetime_new = datetime(year = datetime_object.year, month = datetime_object.month, day = datetime_object.day, hour = oldtimestamp.hour, minute = oldtimestamp.minute, second = oldtimestamp.second)
                            seconds = datetime.timestamp(datetime_new)
                            entry.append(str(int(seconds)))
                            entry.append(data[0].split(" ")[1])
                            writer.writerow(entry)
                os.remove(workingdir+"/inputs/"+e.profile)
                os.rename(workingdir+"/inputs/temp"+e.profile, workingdir+"/inputs/"+e.profile)

#UPLOADINPUTREPOSITORY() UPLOADS DEVICES IN INPUT REPOSITORY, CLEANES TABLES BEFORE UPLOAD

def uploadInInputRepository():

    global sharedQueue
    global count
  
   
    timestamp = datetime.timestamp(datetime_object)
    for c in listEvent:
        if(c.device.type == "Consumer" or c.device.type == "Producer"):
            print("iamhere")
            est_data = datetime.fromtimestamp(int(c.est))
            lst_data = datetime.fromtimestamp(int(c.lst))
            ct_data = datetime.fromtimestamp(int(c.creation_time))
            midsecondsEST = ((est_data.hour) * 60 * 60) + ((est_data.minute) * 60) + (est_data.second)
            midsecondsLST = ((lst_data.hour) * 60 * 60) + ((lst_data.minute) * 60) + (lst_data.second)
            midsecondsCT = ((ct_data.hour) * 60 * 60) + ((ct_data.minute) * 60) + (ct_data.second)
            c.lst=str(int(timestamp+midsecondsLST))
            c.creation_time = str(int(timestamp + midsecondsCT))
            if(c.creation_time != '0'):
                c.creation_time= str(int(timestamp + midsecondsCT))
            else:
                c.creation_time=str(int(timestamp))
            if(c.est != '0'):
                c.est=str(int(timestamp + midsecondsEST))
            else:
                c.est=str(int(timestamp))
            if(c.device.type == "Consumer"):
                sharedQueue.put((int(c.creation_time) + 100,int(count)+100,c))
            if(c.device.type == "Producer"):
                sharedQueue.put((int(c.creation_time),int(count),c))

        #print("inserito")
        elif(c.device.type == "EV"):
            print("EV found")
            book_time = datetime.fromtimestamp(int(c.creation_time))
            planned_arrival_time = datetime.fromtimestamp(int(c.planned_arrival_time))
            planned_departure_time = datetime.fromtimestamp(int(c.planned_departure_time))
            actual_arrival_time = datetime.fromtimestamp(int(c.actual_arrival_time))
            actual_departure_time = datetime.fromtimestamp(int(c.actual_departure_time))
            midseconds_book_time = ((book_time.hour) * 60 * 60) + ((book_time.minute) * 60) + (book_time.second)
            midseconds_planned_arrival_time = ((planned_arrival_time.hour) * 60 * 60) + ((planned_arrival_time.minute) * 60) + (planned_arrival_time.second)
            midseconds_planned_departure_time = ((planned_departure_time.hour) * 60 * 60) + ((planned_departure_time.minute) * 60) + (planned_departure_time.second)
            midseconds_actual_departure_time = ((actual_departure_time.hour) * 60 * 60) + ((actual_departure_time.minute) * 60) + (actual_departure_time.second)
            midseconds_actual_arrival_time = ((actual_arrival_time.hour) * 60 * 60) + ((actual_arrival_time.minute) * 60) + (actual_arrival_time.second)
            c.creation_time=str(int(timestamp+midseconds_book_time))
            c.planned_arrival_time=str(int(timestamp+midseconds_planned_arrival_time))
            c.planned_departure_time=str(int(timestamp+midseconds_planned_departure_time))
            c.actual_arrival_time=str(int(timestamp+midseconds_actual_arrival_time))
            c.actual_departure_time=str(int(timestamp+midseconds_actual_departure_time))
            c.device.type = "CREATE_EV"
            print(c.device.id)
            print("timestamp = " + str(timestamp))
            print("BookingTime = " + str(c.creation_time))
            print("arrival_Time = " + str(c.actual_arrival_time))
            print("departure_Time = " + str(c.actual_departure_time))
            sharedQueue.put((int(timestamp),int(count),c))

            sharedQueue.put((int(c.creation_time),int(count),c))

            sharedQueue.put((int(c.actual_arrival_time),int(count),c))

            sharedQueue.put((int(c.actual_departure_time),int(count),c))


        elif(c.device.type== "heaterCooler"):
            c.creation_time = str(int(timestamp))
            sharedQueue.put((int(c.creation_time),int(count),c))
        elif(c.device.type == "backgroundLoad"):
            c.creation_time = str(int(timestamp))
            sharedQueue.put((int(c.creation_time),int(count),c))
        elif(c.device.type == "battery"):
            est_data = datetime.fromtimestamp(int(c.start_time))
            lst_data = datetime.fromtimestamp(int(c.end_time))
            ct_data = datetime.fromtimestamp(int(c.creation_time))
            midsecondsEST = ((est_data.hour) * 60 * 60) + ((est_data.minute) * 60) + (est_data.second)
            midsecondsLST = ((lst_data.hour) * 60 * 60) + ((lst_data.minute) * 60) + (lst_data.second)
            midsecondsCT = ((ct_data.hour) * 60 * 60) + ((ct_data.minute) * 60) + (ct_data.second)
            c.start_time = str(int(timestamp+midsecondsEST))
            c.end_time=str(int(timestamp+midsecondsLST))
            c.creation_time = str(int(timestamp + midsecondsCT))
            sharedQueue.put((int(c.creation_time),int(count),c))
        count+=1


def  makeNewSimulation(pathneigh,pathload):
    date2 = date.split()
    print(dir1)
    with open("./time.txt","w") as f:
        f.write(str(datetime.timestamp(datetime_object)).split(".")[0])
        f.close()
    newdir = date2[0].replace('/','_')
    print(newdir)
    sim_temp = newdir.split("_")
    lock = False
    if(len(sim_temp[0]) == 1):
    	sim_temp[0] =  "0" + sim_temp[0]
    	lock = True
    if(len(sim_temp[1]) == 1 ):
    	sim_temp[1] = "0" + sim_temp[1]
    	lock = True

    if (lock):
	    newdir = sim_temp[0] + "_" + sim_temp[1] + "_" + sim_temp[2]

    global dirCount
    dirCount = 1
    while(os.path.exists(dir1+"/Simulations/"+newdir+"_"+str(dirCount))):
        dirCount+=1
    os.mkdir(dir1+"/Simulations/"+newdir+"_"+str(dirCount),0o755)
    global workingdir
    global path
    workingdir = dir1+"/Simulations/"+newdir+"_"+str(dirCount)
    print(workingdir)
    print(dir1)
    os.mkdir(workingdir+"/xml",0o755)
    os.mkdir(workingdir+"/output",0o755)
    print("creo: " +workingdir+"/output")
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader = Loader)
    path = cfg['config']['simulation_dir']
    simd = cfg['config']['simulation']
    path = path + "/" + simd
    os.mkdir(workingdir+"/inputs",0o755)
    os.mkdir(workingdir+"/output/HC/",0o755)
    os.mkdir(workingdir+"/output/BG/",0o755)
    os.mkdir(workingdir+"/output/EV/",0o755)

    if (os.path.exists(path+"/output/")):
        shutil.rmtree(path+"/output/")
        os.mkdir(path+"/output/",0o755)
        os.mkdir(path+"/output/BG/",0o755)
        os.mkdir(path+"/output/HC/",0o755)
        os.mkdir(path+"/output/EV/",0o755)

    else:
        os.mkdir(path+"/output/",0o755)
        os.mkdir(path+"/output/BG/",0o755)
        os.mkdir(path+"/output/HC/",0o755)
        os.mkdir(path+"/output/EV/",0o755)


    copy2(pathneigh, workingdir+"/xml")


    os.rename(workingdir+"/xml/"+os.path.basename(pathneigh), workingdir+"/xml/neighborhood.xml")
    copy2(pathload, workingdir+"/xml")
    os.rename(workingdir+"/xml/"+os.path.basename(pathload), workingdir+"/xml/loads.xml")
    csvfiles=glob.glob(dir1+"/Inputs/*.csv")



    for csvfile in csvfiles:
        copy2(csvfile, workingdir+"/inputs")
    """for filename in os.listdir(workingdir+"/inputs"):
        src = workingdir+"/inputs/"+filename
        dst= os.path.splitext(filename)
        newFirstText = dst[0][:-1] + str(dirCount)
        dst = workingdir+"/inputs/"+newFirstText+dst[1]
        os.rename(src, dst)"""


###########################********************** END METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################



###########################********************** SPADE METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################

def copyInscheduler():
    global workingdir
    global mydir
    global webdir
    src_files = os.listdir(workingdir+"/inputs/")
    #mydir = workingdir.split("/")[-1]
    #print(mydir)
    os.mkdir(webdir+"/"+mydir)
    os.mkdir(webdir+"/"+mydir+"/output")

    for file_name in src_files:
        full_file_name = os.path.join(workingdir+"/inputs/", file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, webdir+"/"+mydir)

class ExternalSourceAgent(spade.agent.Agent):
    def __init__(self,address,passw,pathneigh,pathload):
            super(ExternalSourceAgent,self).__init__(address,passw)
            global pathneighbor
            global pathload2
            pathneighbor = pathneigh
            pathload2 = pathload
    class LoadsManager(OneShotBehaviour):
        async def onstart(self):

            print("Starting...")


        async def run(self):
            global pathneighbor
            global pathload2
            global listEvent
            global listDevice
            global listPanels
            global sharedQueue

            sharedQueue.queue.clear()
            listDevice = []  #IN THIS LIST WILL BE STORED ALL THE LOADS
            listPanels = [] #IN THIS LIST WILL BE STORED ALL THE PRODUCERS
            listEvent = []
            makeNewSimulation(pathneighbor,pathload2)
            createDevicesList()
            print("List Created.")
            createEventList()
            print("Information Added.")
            uploadInInputRepository()
            adjustTime()
            copyInscheduler()
            print(datetime_object)
            print("Information Uploaded.")
            await asyncio.sleep(1)
            #createTable()

    async def setup(self):
        print("Agent External Agent Starting")
        Behaviour = self.LoadsManager()
        self.add_behaviour(Behaviour)



###########################********************** END SPADE METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################
