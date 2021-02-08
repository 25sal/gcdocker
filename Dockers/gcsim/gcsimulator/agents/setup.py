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
Setup
=======================================
This agent deals with the creation of the message queue.
"""

###########################****************** IMPORT LIBRARIES SECTION ************************#########################
import spade
import os
from spade.behaviour import *
import xml.etree.ElementTree as ET
import queue
import glob
from shutil import copy2
import csv
import shutil
from utils.config import Configuration
import sqlite3
import logging
from os import listdir
LOGFILE = '/home/gc/simulator/gcdaemon.log'

# logging.basicConfig(filename=LOGFILE, filemode= 'w', level=logging.INFO)


# dir1 = os.path.dirname(os.path.realpath(__file__))
###########################****************** END IMPORT LIBRARIES SECTION ************************####################


###########################****************** DEFINE CLASS SECTION ************************###########################
# ANY DEVICE IS DEFINED BY A A COMPLEX OBJECT

class abstract_device:
    """This class defines an abstract device, will be implemented by other classes."""
    def __init__(self, id='0', house='0', type='0', name='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            type: The device's type .
            name: The device's name.
        """
        self.type = type
        self.id = id
        self.house = house
        self.name = name


class backGroundLoad(abstract_device):
    """This class defines an background load."""
    def __init__(self, id='0', house='0', name='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            name: The device's name.
        """
        super(backGroundLoad,self).__init__(id, house, "backgroundLoad", name)


class heaterCooler(abstract_device):
    """This class defines an heater/cooler device."""
    def __init__(self, id='0', house='0', name='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            name: The device's name.
        """
        super(heaterCooler,self).__init__(id, house, "heaterCooler",  name)


class EV(abstract_device):
    """This class defines an EV device."""
    def __init__(self, id=0, house=0, chargingPoint=0, name='0', capacity='0', max_ch_pow_ac='0', max_ch_pow_cc='0',
                 max_dis_pow_ac='0', max_dis_pow_cc='0', max_all_en='0', min_all_en='0', sb_ch='0', sb_dis='0',
                 ch_eff='0', dis_eff='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            chargingPoint: The chargingPoint where the device is located.
            name: The device's name.
            capacity:  It is the maximum amount of energy can be stored.
            max_ch_pow_ac: Max charging power when alternate current is used.
            max_ch_pow_cc: Max charging power when direct current is used.
            max_dis_pow_ac: Max discharging power in alternate current.
            max_dis_pow_cc: Max discharging power in direct current.
            max_all_en: Maximum allowed energy can be stored as a percentage of the capacity.
            min_all_en: Minimum allowed energy must be stored as a percentage of the capacity.
            sb_ch: Energy threshold above which the charging efficiency decrease.
            sb_dis: Energy threshold below the discharging efficiency decrease.
            ch_eff: This parameter must be multiplied to the nominal maximum charging power to obtain the actual maximum charging power above sb_ch.
            dis_eff: This parameter must be multiplied to the nominal maximum discharging power to obtain the actual maximum discharging power below sb_dis.
        """
        super(EV,self).__init__(id, house, "EV", name)
        self.cp = chargingPoint
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
    """This class defines an Battery device."""

    def __init__(self, id=0, house=0, name='0', capacity='0', max_ch_pow_ac='0', max_ch_pow_cc='0',
                 max_dis_pow='0', max_all_en='0', min_all_en='0', sb_ch='0', sb_dis='0', ch_eff='0',
                 dis_eff='0'):
        """
        Args:
            id: The device's id.
            house: The house where the device is located.
            name: The device's name.
            capacity:  It is the maximum amount of energy can be stored.
            max_ch_pow_ac: Max charging power when alternate current is used.
            max_ch_pow_cc: Max charging power when direct current is used.
            max_dis_pow_ac: Max discharging power.
            max_all_en: Maximum allowed energy can be stored as a percentage of the capacity.
            min_all_en: Minimum allowed energy must be stored as a percentage of the capacity.
            sb_ch: Energy threshold above which the charging efficiency decrease.
            sb_dis: Energy threshold below the discharging efficiency decrease.
            ch_eff: This parameter must be multiplied to the nominal maximum charging power to obtain the actual maximum charging power above sb_ch.
            dis_eff: This parameter must be multiplied to the nominal maximum discharging power to obtain the actual maximum discharging power below sb_dis.
        """
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
    """This class defines a schedulable device or a producer device."""

    def __init__(self, id='0', type='0', name='0', house='0'):
        """
        Args:
            id: The device's id.
            type: The device's type .
            name: The device's name.
            house: The house where the device is located.
        """
        super().__init__(id, house, type, name)


class abstract_event:
    """This class defines an abstract event."""
    def __init__(self, device='0', house='0', creation_time='0', type2=0):
        """
        Args:
            device: The device to which the event refers
            house: The house where the device is located.
            creation_time: The time in which the event has to be triggered
            type2: Type of the event
        """
        self.device = device
        self.type = type2
        self.creation_time = creation_time
        self.house = house


class eventGeneral(abstract_event):
    """This class defines a schedulable event."""
    def __init__(self, device='0', house='0', est='0', lst='0', creation_time='0', profile='0', type2=0):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            est: The earliest start time.
            lst: The latest start time.
            creation_time: The time in which the event has to be triggered.
            profile: The consumption profile the device has to perform.
            type2: The event type.
        """
        super(eventGeneral, self).__init__(device, house, creation_time, type2)
        self.est = est
        self.lst = lst
        self.profile = profile


class eventDelete(abstract_event):
    """This class defines a delete event."""

    def __init__(self, device='0', house='0', creation_time='0', consumption=0):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the event has to be triggered.
            consumption: Total consumption energy value.
        """
        self.device = device
        self.type = "delete"
        self.creation_time = creation_time
        self.house = house
        self.consumption = consumption


class eventEcar(abstract_event):
    """This class defines an EV event."""

    def __init__(self, device='0', house='0', Soc_at_arrival='0', booking_time='0', planned_arrival_time='0'
                 , planned_departure_time='0', actual_arrival_time='0', actual_departure_time='0',
                 target_soc='0', v2g='0', priority='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            Soc_at_arrival: The status of charge at plug-in time.
            booking_time: The booking time of charging session.
            planned_arrival_time: The planned arrival time to the charging point.
            planned_departure_time: The planned departure time from the charging point.
            actual_arrival_time: The actual arrival time to the charging point.
            actual_departure_time: The actual departure time from the charging point.
            target_soc: The desidered status of charge at plug-out time.
            v2g: Flag to set in order to use vehicle to grid.
            priority: Set the priority charging for the charging session.
        """
        self.device = device
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
    """This class defines a battery event."""
    def __init__(self, device='0', house='0', Soc_at_arrival='0', booking_time='0', start_time='0', end_time='0',
                 target_soc='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            Soc_at_arrival: The status of charge at start time.
            booking_time: The time in which the battery entered into the system.
            start_time: The time in which the battery starts to work.
            end_time: The time in which the battery stops to work.
            target_soc: The desidered status of charge at the end time.
        """
        self.device = device
        self.type = "BATTERY"
        self.creation_time = booking_time
        self.house = house
        self.Soc_at_arrival = Soc_at_arrival
        self.start_time = start_time
        self.end_time = end_time
        self.target_soc = target_soc


class eventProducer(abstract_event):
    """This class defines a producer event."""
    def __init__(self, device='0', house='0', est='0', lst='0', creation_time='0', profile='0', type2=0,
                 energycost='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the producer entered into the system.
            profile: The production profile.
            type2: The event type.
            energycost: The energy cost.
        """
        self.device = device
        self.type = "load"
        self.creation_time = creation_time
        self.profile = profile
        self.house = house
        self.count = 0
        self.energycost = energycost
        self.est = est
        self.lst = lst


class eventBackground(abstract_event):
    """This class defines a background load event."""

    def __init__(self, device='0', house='0', creation_time='0', profile='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the background load entered into the system.
            profile: The consumption profile.
        """
        self.device = device
        self.creation_time = creation_time
        self.profile = profile
        self.house = house
        self.type = "background"


class eventHeaterCooler(abstract_event):
    """This class defines a heater/cooler load event."""
    def __init__(self, device='0', house='0', creation_time='0', profile='0'):
        """
        Args:
            device: The device to which the event refers.
            house: The house where the device is located.
            creation_time: The time in which the heater/cooler load entered into the system.
            profile: The consumption profile.
        """
        self.device = device
        self.creation_time = creation_time
        self.profile = profile
        self.house = house
        self.type = "heatercooler"


class Energy_Cost():
    """This class defines an energy cost  event."""
    def __init__(self, type='0', profile='0'):
        """
        Args:
            type: Type of event.
            profile: The energy cost profile.
        """
        self.type = "energy_cost"
        self.profile = profile


class Energy_Mix():
    """This class defines an energy mix event."""
    def __init__(self, type='0', profile='0'):
        """
        Args:
            type: Type of event.
            profile: The energy cost profile.
        """
        self.type = "energy_mix"
        self.profile = profile


class Neighborhood():
    """This class defines a neighborhood."""
    def __init__(self, type='0', peakload='0'):
        """
        Args:
            type: Type of energy Hub.
            peakload: The power peak.
        """
        self.type = "neighborhood"
        self.peakload = peakload


class House():
    """This class defines an house."""
    def __init__(self, type='0', id='0', peakload='0', numcp=0):
        """
        Args:
            type: Type of energy Hub.
            id: The id of energy hub.
            peakload: The power peak.
            numcp: The number of charging point the house has.
        """
        self.type = "house"
        self.id = id
        self.peakload = peakload
        self.numcp = numcp


class ChargingStation():
    """This class defines a charging Station."""
    def __init__(self, type='0', id='0', peakload='0', numcp=0):
        """
        Args:
            type: Type of energy Hub.
            id: The id of energy hub.
            peakload: The power peak.
            numcp: The number of charging point the house has.
        """
        self.type = "chargingStation"
        self.id = id
        self.peakload = peakload
        self.numcp = numcp


class ChargingPoint():
    """This class defines a charging Point."""

    def __init__(self, type='0', id='0', houseid='0', conntype='0', peakload='0'):
        """
        Args:
            type: Type of energy Hub.
            id: The id of energy hub.
            houseid: The id of energy hub parent.
            conntype: Type of connectors the charging point has (AC/DC)
            peakload: The power peak.
        """
        self.type = "chargingPoint"
        self.houseid = houseid
        self.id = id
        self.peakload = peakload
        self.connection_type = conntype


###########################****************** END DEFINE CLASS SECTION ************************###################################################


###########################****************** UTIL VARIABLES SECTION ************************###################################################
from dataclasses import dataclass


##########################################################
# Override the comparison methods for the shared queue   #
##########################################################
@dataclass(order=False)
class EnqueuedEvent:
    """This class overrides the comparison methods for the shared queue."""

    unique_id = 0

    def __init__(self, timestamp, event, unique_id=None):
        """
        Args:
            timestamp: Event time.
            event: The event.
            unique_id: An unique id in case of same timestamp for two events.
        """
        self.timestamp = timestamp
        self.event = event
        if unique_id is None:
            EnqueuedEvent.unique_id +=1
            self.unique_id = EnqueuedEvent.unique_id
        else:
            self.unique_id = unique_id

    def __lt__(self, other):
        if self.timestamp == other.timestamp:
            return self.unique_id < other.unique_id
        else:
            return self.timestamp < other.timestamp

    def __gt__(self, other):
        if self.timestamp == other.timestamp:
            return self.unique_id > other.unique_id
        return self.timestamp > other.timestamp

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.unique_id == other.id

    def __ne__(self, other):
        return not  self.timestamp == other.timestamp and self.unique_id == other.id


####################################################################
# Class entities, used to enqueue/get an object in/from the queue  #
####################################################################
class Entities:
    """This class is used to enqueue/get an object in/from the queue."""

    listDevice = []  # IN THIS LIST WILL BE STORED ALL THE LOADS
    listPanels = []  # IN THIS LIST WILL BE STORED ALL THE PRODUCERS
    listEvent = []
    sharedQueue = queue.PriorityQueue()

    @classmethod
    def enqueue_event(cls, timestamp, event, unique_id=None):
        """
        This method is used to enqueue an event in the event queue.
        Args:
            timestamp: Event time.
            event: The event.
            unique_id: An unique id in case of same timestamp for two events.
        """
        cls.sharedQueue.put(EnqueuedEvent(timestamp, event, unique_id))

    @classmethod
    def next_event(cls):
        """
        This method is used to dequeue an event from the event queue.
        """
        item = cls.sharedQueue.get()
        return   (item.timestamp, item.event, item.unique_id)

###########################****************** END UTIL VARIABLES SECTION ************************###################################################


###########################********************** METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################


######################################################################
# Create a Database Table to store all events/devices of a scenario  #
######################################################################
def createTable():
    workingdir = Configuration.parameters['workingdir']
    db_filename = workingdir + '/xml/input.db'
    conn = sqlite3.connect(db_filename)
    schema_filename = '../xml/schema.sql'

    with open(schema_filename, 'rt') as f:
        schema = f.read()
    conn.executescript(schema)
    f = open(workingdir + "/xml/neighborhood.xml", "r")
    fileIntero = f.read()
    root = ET.fromstring(fileIntero)

    for house in root.findall('house'):  # READ XML FILE
        houseId = house.get('id')
        query = "insert into housecs (id) values(?)"
        cursor = conn.cursor()
        cursor.execute(query, (houseId,))

        for user in house.findall('user'):
            userId = user.get('id')
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, houseId, name, type, type,))

            for OtherElement in user.findall('heatercooler'):
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, houseId, name, "heatercooler", "N-S Consumer",))

            for OtherElement in user.findall('backgroundload'):
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, houseId, name, "backgroundLoad", "N-S Consumer",))

            for OtherElement in user.findall('ecar'):
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text

                capacity = OtherElement.find('capacity').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "Capacity", str(capacity),))

                maxchpowac = OtherElement.find('maxchpowac').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "max_ch_pow_ac", str(maxchpowac),))

                maxchpowcc = OtherElement.find('maxchpowcc').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "max_ch_pow_cc", str(maxchpowcc),))

                maxdispow = OtherElement.find('maxdispow').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "max_dis_pow", str(maxdispow),))

                maxallen = OtherElement.find('maxallen').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "max_all_en", str(maxallen),))

                minallen = OtherElement.find('minallen').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "min_all_en", str(minallen),))

                sbch = OtherElement.find('sbch').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "sbch", str(sbch),))

                sbdis = OtherElement.find('sbdis').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "sbdis", str(sbdis),))

                cheff = OtherElement.find('cheff').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "cheff", str(cheff),))

                dis_eff = OtherElement.find('dis_eff').text
                query = "insert into staticParameter(iddevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "dis_eff", str(dis_eff),))

                query = "insert into device(id,id_house,name,type,class) values(?,?,?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, houseId, name, "ecar", "Prosumer",))

    f = open(workingdir + "/xml/loads.xml", "r")
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
                cursor.execute(query, (deviceId, "est", str(est),))

                lst = device.find('lst').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "lst", str(lst),))
                creation_time = device.find('creation_time').text
                type2 = device.find("type").text

                for c in Entities.listDevice:
                    if deviceId == c.id and houseId == c.house:
                        if c.type == "Consumer":
                            query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
                            cursor = conn.cursor()
                            cursor.execute(query, (creation_time, deviceId, "Load",))
                        elif c.type == "Producer":
                            query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
                            cursor = conn.cursor()
                            cursor.execute(query, (creation_time, deviceId, "Create PV",))

            for device in user.findall('backgroundload'):
                deviceId = device.find('id').text
                query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, ("0", deviceId, "Create BG",))

            for device in user.findall('ecar'):
                deviceId = device.find('id').text
                pat = device.find('pat').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "pat", str(pat),))
                pdt = device.find('pdt').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "pdt", str(pdt),))
                aat = device.find('aat').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "aat", str(aat),))
                adt = device.find('adt').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "adt", str(adt),))
                creation_time = device.find('creation_time').text
                soc = device.find('soc').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "soc", str(soc),))
                targetSoc = device.find('targetSoc').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "targetSoc", str(targetSoc),))
                V2G = device.find('V2G').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "V2G", str(V2G),))
                priority = device.find('priority').text
                query = "insert into dinamicParameter(idDevice,key,val) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (deviceId, "targpriorityetSoc", str(priority),))
                query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, (creation_time, deviceId, "ECAR event",))

            for device in user.findall('heatercooler'):
                deviceId = device.find('id').text
                query = "insert into event(creation_time,idDevice,type) values(?,?,?)"
                cursor = conn.cursor()
                cursor.execute(query, ("0", deviceId, "Create HC",))
    conn.commit()
    conn.close()

#
#############################################################################################################
# createDevicesList() READS FROM A FILE ALL THE DEVICES, SORTS THEM BY TYPE AND APPEND THEM TO DEVICE LIST  #
#############################################################################################################
def createDevicesList():
    """ This method read from neighborhood.xml all the devices, sort them by type and append them to device list."""
    workingdir = Configuration.parameters['runtime_dir']
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
    timestamp = datetime.timestamp(datetime_object)


    logging.debug("runtime folder: " + workingdir)
    f = open(workingdir + "/xml/neighborhood.xml", "r")
    fileIntero = f.read()
    root = ET.fromstring(fileIntero)
    neigh = Neighborhood('neighborhood', root.get('peakLoad2'))
    Entities.enqueue_event(timestamp, neigh)
    for energycost in root.findall('energyCost'):
        energycost = Energy_Cost('energyCost', energycost.find('profile').text)
        Entities.enqueue_event(timestamp, energycost)
    for energyMix in root.findall('energyMix'):
        energyMix = Energy_Mix('energyMix', energyMix.find('profile').text)
        Entities.enqueue_event(timestamp, energyMix)

    # Inserisci qui il codice per la creazione del neighborhood
    for house in root.findall('house'):  # READ XML FILE
        # inserisci qui il codice per la creazione di una house
        houseId = house.get('id')
        housedev = House('house', houseId, house.get('peakLoad'), 0)

        for user in house.findall('user'):
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                c = device(deviceId, type, name, houseId)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('heatercooler'):
                logging.debug("new heatercooler")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = heaterCooler(deviceId, houseId, name)
                Entities.listDevice.append(c)

            for OtherElement in user.findall('backgroundload'):
                logging.debug("new bg")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = backGroundLoad(deviceId, houseId, name)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('battery'):
                logging.debug("new battery")
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
                c = Battery(deviceId, houseId, name, capacity, maxchpowac, maxchpowcc, maxdispow, maxallen, minallen,
                            sbch, sbdis, cheff, dis_eff)
                Entities.listDevice.append(c)

            for cp in user.findall('ChargingPoint'):
                cpId = cp.get('id')
                cpdev = ChargingPoint('house', houseId, cpId, cp.get('ConnectorsType'), cp.get('peakLoad'))
                # sharedQueue.put((0,int(count),cpdev))

                housedev.numcp += 1
                # inserisci qui il codice per la creazione del Cp
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
                    c = EV(deviceId, houseId, cpId, name, capacity, maxchpowac, maxchpowcc, maxdispowac, maxdispowcc
                           , maxallen, minallen, sbch, sbdis, cheff, dis_eff)
                    Entities.listDevice.append(c)
        Entities.enqueue_event(timestamp, housedev)
    for house in root.findall('chargingStation'):  # READ XML FILE
        # inserisci qui il codice per la creazione di una cs
        houseId = house.get('id')
        housedev = ChargingStation('house', houseId, house.get('peakLoad'), 0)

        for user in house.findall('user'):
            userId = user.get('id')
            for deviceElement in user.findall('device'):
                deviceId = deviceElement.find('id').text
                type = deviceElement.find('type').text
                name = deviceElement.find('name').text
                c = device(deviceId, type, name, houseId)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('heatercooler'):
                logging.debug("new heatercooler")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = heaterCooler(deviceId, houseId, name)
                Entities.listDevice.append(c)

            for OtherElement in user.findall('backgroundload'):
                logging.debug("new bg")
                deviceId = OtherElement.find('id').text
                name = OtherElement.find('name').text
                c = backGroundLoad(deviceId, houseId, name)
                Entities.listDevice.append(c)
            for OtherElement in user.findall('battery'):
                logging.debug("new buttery")
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
                c = Battery(deviceId, houseId, name, capacity, maxchpowac, maxchpowcc, maxdispow, maxallen, minallen,
                            sbch, sbdis, cheff, dis_eff)
                Entities.listDevice.append(c)
            for cp in user.findall('ChargingPoint'):
                housedev.numcp += 1
                cpId = cp.get('id')
                # cpdev = ChargingPoint('house',houseId,cpId, cp.get('ConnectorsType'), cp.get('peakLoad'))
                # sharedQueue.put((0,int(count),cpdev))

                # inserisci qui il codice per la creazione del Cp
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
                    c = EV(deviceId, houseId, cpId, name, capacity, maxchpowac, maxchpowcc, maxdispowac, maxdispowcc
                           , maxallen, minallen, sbch, sbdis, cheff, dis_eff)
                    Entities.listDevice.append(c)
        Entities.enqueue_event(timestamp,  housedev)

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
            c = EV(deviceId, -1, -1, name, capacity, maxchpowac, maxchpowcc, maxdispowac, maxdispowcc, maxallen
                   , minallen, sbch, sbdis, cheff, dis_eff)
            Entities.listDevice.append(c)





##############################################################################################
#  createEventList() READS FROM A FILE THE EVENTS INFORMATIONS AND APPEND THEM TO LOADSLIST  #
##############################################################################################
def createEventList():
    """ This method read from loads.xml the events info and append them to loadslist."""

    workingdir = Configuration.parameters['runtime_dir']
    path = Configuration.parameters['current_sim_dir']
    f = open(workingdir + "/xml/loads.xml", "r")
    fileIntero = f.read();
    root = ET.fromstring(fileIntero)
    for house in root:
        if house.tag != 'fleet':
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
                    if device.find('profile').text.endswith(' '):
                        profile = device.find('profile').text[:-1]
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                    else:
                        profile = device.find('profile').text
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")

                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "Consumer":
                                e = eventGeneral(c, houseId, est, lst, creation_time, profile, "load")
                                Entities.listEvent.append(e)
                                #copy2(workingdir + "/Inputs/" + profile, workingdir + "/inputs")
                                copy2(workingdir + "/inputs/" + profile, workingdir + "/output/SH")
                            elif c.type == "Producer":
                                energycost = device.find('energy_cost').text
                                #copy2(workingdir + "/Inputs/" + profile, workingdir + "/inputs")
                                copy2(workingdir + "/inputs/" + profile, workingdir + "/output/PV")

                                e = eventProducer(c, houseId, est, lst, creation_time, profile, "load", energycost)

                                Entities.listEvent.append(e)
                                # CODICE PROVVISORIO
                                # H = int(creation_time) + 21600
                                # logging.info(H)
                                # logging.info(int(creation_time))
                                # e1= eventGeneral(c,houseId,est,lst,H,profile, "LoadUpdate")
                                # H1 = int(creation_time) + 2*21600
                            # logging.info(H1)
                            # e2= eventGeneral(c,houseId,est,lst,H1,profile, "LoadUpdate")
                            # H2 = int(creation_time) + 3*21600
                        # logging.info(H2)
                        # e3= eventGeneral(c,houseId,est,lst,H2,profile, "LoadUpdate")
                        # Entities.listEvent.append(e1)
                        # Entities.listEvent.append(e2)
                        # Entities.listEvent.append(e3)
                        # #FineCodiceProvvisorio
                for device in user.findall('backgroundload'):
                    deviceId = device.find('id').text
                    mydir = Configuration.mydir
                    if device.find('profile').text.endswith(' '):
                        profile = device.find('profile').text[:-1]
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                        copy2(workingdir + "/inputs/" + profile, path + "/Results/" + Configuration.parameters['user_dir'] + "/output/BG/")
                    else:
                        profile = device.find('profile').text
                        #copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                        copy2(workingdir + "/inputs/" + profile, path + "/Results/" + Configuration.parameters['user_dir'] + "/output/BG/")
                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "backgroundLoad":
                                e = eventBackground(c, houseId, 0, profile)
                                Entities.listEvent.append(e)
                for device in user.findall('heatercooler'):
                    deviceId = device.find('id').text
                    if device.find('profile').text.endswith(' '):
                        profile = device.find('profile').text[:-1]
                        copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                    else:
                        profile = device.find('profile').text
                        copy2(path + "/Inputs/" + profile, workingdir + "/inputs")
                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "heaterCooler":
                                e = eventHeaterCooler(c, houseId, 0, profile)
                                Entities.listEvent.append(e)
                for device in user.findall('battery'):
                    deviceId = device.find('id').text
                    for c in Entities.listDevice:
                        if deviceId == c.id and houseId == c.house:
                            if c.type == "battery":
                                aat = device.find('startTime').text
                                adt = device.find('endTime').text
                                creation_time = device.find('creation_time').text
                                soc = device.find('soc').text
                                targetSoc = device.find('targetSoc').text
                                e = eventBattery(c, houseId, soc, creation_time, aat, adt, targetSoc)
                                Entities.listEvent.append(e)
                for cp in user.findall('ChargingPoint'):
                    for device in cp.findall('ecar'):
                        deviceId = device.find('id').text
                        for c in Entities.listDevice:
                            if deviceId == c.id and houseId == c.house:
                                if c.type == "EV":
                                    pat = device.find('pat').text
                                    pdt = device.find('pdt').text
                                    aat = device.find('aat').text
                                    adt = device.find('adt').text
                                    creation_time = device.find('creation_time').text
                                    soc = device.find('soc').text
                                    targetSoc = device.find('targetSoc').text
                                    V2G = device.find('V2G').text
                                    priority = device.find('priority').text
                                    e = eventEcar(c, houseId, soc, creation_time, pat, pdt, aat, adt, targetSoc, V2G,
                                                  priority)
                                    Entities.listEvent.append(e)
        else:
            for device in house.findall('ecar'):
                deviceId = device.find('id').text
                for c in Entities.listDevice:
                    if deviceId == c.id:
                        if c.type == "EV":
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
                            Entities.listEvent.append(e)

####################################################################################
#  Convert Timestamps of a timeseries of an X day in timestamps of simulation day  #
####################################################################################
def adjustTime():
    """ This method Convert Timestamps of a timeseries of an X day in timestamps of simulation day."""

    workingdir = Configuration.parameters['runtime_dir']
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
    timestamp = datetime.timestamp(datetime_object)
    entry = []
    allFilenames = listdir(workingdir+'/inputs')
    csvFilenames = [ filename for filename in allFilenames if filename.endswith( ".csv" ) ]
    print(csvFilenames)
    for file in csvFilenames:
            print(file)
            with open(workingdir + "/inputs/" + file, "r") as f:
                with open(workingdir + "/inputs/temp" + file, "w") as f2:
                    reader = csv.reader(f)
                    writer = csv.writer(f2, delimiter=' ')
                    first = 0
                    for data in reader:
                        entry = []
                        oldtimestamp = datetime.fromtimestamp(int(data[0].split(" ")[0]))
                        if(first==0):
                            oldDay = oldtimestamp.day
                            first =1
                        datetime_new = datetime(year=datetime_object.year, month=datetime_object.month,
                                                day=datetime_object.day, hour=oldtimestamp.hour,
                                                minute=oldtimestamp.minute, second=oldtimestamp.second)
                        seconds = datetime.timestamp(datetime_new)
                        newDay = oldtimestamp.day
                        if(oldDay != newDay):
                            seconds += 86400
                        entry.append(str(int(seconds)))
                        entry.append(data[0].split(" ")[1])
                        writer.writerow(entry)
            os.remove(workingdir + "/inputs/" + file)
            os.rename(workingdir + "/inputs/temp" + file, workingdir + "/inputs/" + file)



################################################################
#  UPLOADINPUTREPOSITORY() enqueue objects in the shared queue #
################################################################
def uploadInInputRepository():
    """ This method enqueue objects in the shared queue."""

    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')

    timestamp = datetime.timestamp(datetime_object)
    for c in Entities.listEvent:
        if c.device.type == "Consumer" or c.device.type == "Producer":
            est_data = datetime.fromtimestamp(int(c.est))
            lst_data = datetime.fromtimestamp(int(c.lst))
            ct_data = datetime.fromtimestamp(int(c.creation_time))
            midsecondsEST = (est_data.hour * 60 * 60) + (est_data.minute * 60) + est_data.second
            midsecondsLST = (lst_data.hour * 60 * 60) + (lst_data.minute * 60) + lst_data.second
            midsecondsCT = (ct_data.hour * 60 * 60) + (ct_data.minute * 60) + ct_data.second
            c.lst = str(int(timestamp + midsecondsLST))
            c.creation_time = str(int(timestamp + midsecondsCT))
            if c.creation_time != '0':
                c.creation_time = str(int(timestamp + midsecondsCT))
            else:
                c.creation_time = str(int(timestamp))
            if c.est != '0':
                c.est = str(int(timestamp + midsecondsEST))
            else:
                c.est = str(int(timestamp))
            if c.device.type == "Consumer":
                Entities.enqueue_event(int(c.creation_time) + 100, c)
            if c.device.type == "Producer":
                Entities.enqueue_event(int(c.creation_time),  c)

        # logging.info("inserito")
        elif c.device.type == "EV":
            logging.debug("new EV")
            book_time = datetime.fromtimestamp(int(c.creation_time))
            planned_arrival_time = datetime.fromtimestamp(int(c.planned_arrival_time))
            planned_departure_time = datetime.fromtimestamp(int(c.planned_departure_time))
            actual_arrival_time = datetime.fromtimestamp(int(c.actual_arrival_time))
            actual_departure_time = datetime.fromtimestamp(int(c.actual_departure_time))
            midseconds_book_time = (book_time.hour * 60 * 60) + (book_time.minute * 60) + book_time.second
            midseconds_planned_arrival_time = (planned_arrival_time.hour * 60 * 60) + \
                                              (planned_arrival_time.minute * 60) + (planned_arrival_time.second)
            midseconds_planned_departure_time = (planned_departure_time.hour * 60 * 60) + \
                                                (planned_departure_time.minute * 60) + planned_departure_time.second
            midseconds_actual_departure_time = (actual_departure_time.hour * 60 * 60) + \
                                               (actual_departure_time.minute * 60) + actual_departure_time.second
            midseconds_actual_arrival_time = (actual_arrival_time.hour * 60 * 60) + \
                                             (actual_arrival_time.minute * 60) + actual_arrival_time.second
            c.creation_time = str(int(timestamp + midseconds_book_time))
            c.planned_arrival_time = str(int(timestamp + midseconds_planned_arrival_time))
            c.planned_departure_time = str(int(timestamp + midseconds_planned_departure_time))
            c.actual_arrival_time = str(int(timestamp + midseconds_actual_arrival_time))
            c.actual_departure_time = str(int(timestamp + midseconds_actual_departure_time))
            c.device.type = "CREATE_EV"
            '''
            logging.info(c.device.id)
            logging.info("timestamp = " + str(timestamp))
            logging.info("BookingTime  = " + str(c.creation_time))
            logging.info("arrival_Time =  " + str(c.actual_arrival_time))
            logging.info("departure_Time = " + str(c.actual_departure_time))
            '''
            Entities.enqueue_event(timestamp, c)

            Entities.enqueue_event(int(c.creation_time),  c)

            Entities.enqueue_event(int(c.actual_arrival_time),  c)

            Entities.enqueue_event(int(c.actual_departure_time),  c)

        elif c.device.type == "heaterCooler":
            c.creation_time = str(int(timestamp))
            Entities.enqueue_event(int(c.creation_time),  c)
        elif c.device.type == "backgroundLoad":
            c.creation_time = str(int(timestamp))
            Entities.enqueue_event(int(c.creation_time),  c)
        elif c.device.type == "battery":
            est_data = datetime.fromtimestamp(int(c.start_time))
            lst_data = datetime.fromtimestamp(int(c.end_time))
            ct_data = datetime.fromtimestamp(int(c.creation_time))
            midsecondsEST = ((est_data.hour) * 60 * 60) + ((est_data.minute) * 60) + (est_data.second)
            midsecondsLST = ((lst_data.hour) * 60 * 60) + ((lst_data.minute) * 60) + (lst_data.second)
            midsecondsCT = ((ct_data.hour) * 60 * 60) + ((ct_data.minute) * 60) + (ct_data.second)
            c.start_time = str(int(timestamp + midsecondsEST))
            c.end_time = str(int(timestamp + midsecondsLST))
            c.creation_time = str(int(timestamp + midsecondsCT))
            Entities.enqueue_event(int(c.creation_time),  c)


###################################################
#  This Method create all simulation directories  #
###################################################
def makeNewSimulation(pathneigh, pathload):
    """
    This Method create all simulation directories.
    Args:
        pathneigh: The neighborhood.xml path.
        pathload: The loads.xml path.
    """
    date = Configuration.parameters['date'] + " 00:00:00"
    datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
    date2 = date.split()
    dir1 = Configuration.parameters['current_sim_dir']

    with open("../tt", "w") as f:
        f.write(str(datetime.timestamp(datetime_object)).split(".")[0])
        f.close()
    newdir = date2[0].replace('/', '_')

    sim_temp = newdir.split("_")
    lock = False
    if len(sim_temp[0]) == 1:
        sim_temp[0] = " 0 " + sim_temp[0]
        lock = True
    if len(sim_temp[1]) == 1:
        sim_temp[1] = "0" + sim_temp[1]
        lock = True

    if lock:
        newdir = sim_temp[0] + "_" + sim_temp[1] + "_" + sim_temp[2]

    dirCount = 1
    while os.path.exists(dir1 + "/Results/" + newdir + "_" + str(dirCount)):
        dirCount += 1
    os.mkdir(dir1 + "/Results/" + newdir + "_" + str(dirCount), 0o755)
    workingdir = Configuration.parameters['runtime_dir']


    os.mkdir(workingdir + "/xml", 0o755)
    os.mkdir(workingdir + "/output", 0o755)

    path = Configuration.parameters['current_sim_dir']

    os.mkdir(workingdir + "/inputs", 0o755)
    os.mkdir(workingdir + "/output/HC/", 0o755)
    os.mkdir(workingdir + "/output/BG/", 0o755)
    os.mkdir(workingdir + "/output/EV/", 0o755)
    os.mkdir(workingdir + "/output/PV/", 0o755)
    os.mkdir(workingdir + "/output/SH/", 0o755)

    if os.path.exists(path + "/output/"):
        shutil.rmtree(path + "/output/")
        os.mkdir(path + "/output/", 0o755)
        os.mkdir(path + "/output/BG/", 0o755)
        os.mkdir(path + "/output/HC/", 0o755)
        os.mkdir(path + "/output/EV/", 0o755)
        os.mkdir(path + "/output/SH/", 0o755)
    else:
        os.mkdir(path + "/output/", 0o755)
        os.mkdir(path + "/output/BG/", 0o755)
        os.mkdir(path + "/output/HC/", 0o755)
        os.mkdir(path + "/output/EV/", 0o755)
        os.mkdir(path + "/output/SH/", 0o755)


    copy2(pathneigh, workingdir + "/xml")

    os.rename(workingdir + "/xml/" + os.path.basename(pathneigh), workingdir + "/xml/neighborhood.xml")
    copy2(pathload, workingdir + "/xml")
    os.rename(workingdir + "/xml/" + os.path.basename(pathload), workingdir + "/xml/loads.xml")
    csvfiles = glob.glob(dir1 + "/Inputs/*.csv")

    for csvfile in csvfiles:
        copy2(csvfile, workingdir + "/inputs")
    logging.info("runtime folders created")

    """for filename in os.listdir(workingdir+"/inputs"):
        src = workingdir+"/inputs/"+filename
        dst= os.path.splitext(filename)
        newFirstText = dst[0][:-1] + str(dirCount)
        dst = workingdir+"/inputs/"+newFirstText+dst[1]
        os.rename(src, dst)"""





######################################################################################################
#  This method copy the scenario to the web directory to allow the scheduler to download the files.  #
######################################################################################################
def copyInscheduler():
    """ This method copy the scenario to the web directory to allow the scheduler to download the files. """
    workingdir = Configuration.parameters['runtime_dir']
    mydir = Configuration.parameters['user_dir']
    webdir = Configuration.parameters['webdir']
    src_files = os.listdir(workingdir + "/inputs/")
    # mydir = .split("/")[-1]
    # print ( myd i r)

    os.mkdir(webdir + "/" + mydir)
    os.mkdir(webdir + "/" + mydir + "/output")

    for file_name in src_files:
        full_file_name = os.path.join(workingdir + "/inputs/", file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(
                full_file_name, webdir + "/" +mydir)

####********************** END METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################


###########################********************** SPADE METHODS SECTION ***************************######################################### # #########
###########################*************** ANY ACTION IS DEFINED BY A METHOD *** * *** * ********################## # ### # ##### # ######################



class ExternalSourceAgent(spade.agent.Agent):
    """This Agent deals to the creation of simulation data from xml files."""
    def __init__(self, address, passw,
                 pathneigh, pathload):
        """
        Args:
            address: Agent Address.
            passw: Agent Password.
            pathneigh: The neighborhood.xml path.
            pathload: The loads.xml path.
        """
        super(ExternalSourceAgent, self).__init__(address, passw)
        self.pathneighbor = pathneigh
        self.pathload2 = pathload


    def simulation_setup(self):
        Entities.sharedQueue.queue.clear()
        Entities.listDevice = []  # IN THIS LIST WILL BE STORED ALL THE LOADS
        Entities.listPanels = []  # IN THIS LIST WILL BE STORED ALL THE PRODUCERS
        Entities.listEvent = []

        makeNewSimulation(self.pathneighbor, self.pathload2)
        adjustTime()

        createDevicesList()
        logging.info("List Created.")

        createEventList()
        logging.info("Information Added.")
        uploadInInputRepository()
        copyInscheduler()

        date = Configuration.parameters['date'] + " 00:00:00"
        datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
        logging.info(datetime_object)
        logging.info("Information Uploaded.")

###########################********************** END SPADE METHODS SECTION ***************************###################################################
###########################*************** ANY ACTION IS DEFINED BY A METHOD ****************###################################################
