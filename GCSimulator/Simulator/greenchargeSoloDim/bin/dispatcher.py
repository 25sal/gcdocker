import threading
import time
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime,timedelta
import externalSourceAgent as es
import asyncio
import csv
import os
import scheduler as sche
import yaml
from yaml import Loader
from sys import path
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
    dirPath2 = dir1+"/Inputs/"+file
    f = open(dirPath2)
    csv_f = csv.reader(f)
    data = []
    count=0
    for row in csv_f:
        data.append(row[0].split()[0])
        count+=1
    f.close()
    delta = int(data[-1]) - int(data[0])
    return delta

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
webdir = cfg['config']['webdir']
dir1 = cfg['config']['simulation_dir']

webarray = webdir.split("/")
found = 0
realpath = ""
for element in webarray:
    if(found == 1):
        realpath = realpath +"/"+ element
    if(element == "public_html"):
        found = 1



class MessageFactory():

    def end():
        global jid
        global basejid
        if(protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message="SIMULATION END"
            mex.body = message
            return(mex)
        else:
            mex = Message(to=basejid+"/"+jid)
            message =  """{"message" : {"subject" : "SIMULATION_END"}}"""
            mex.body = message
            mex.metadata = "0"
            return(mex)

    def heatercooler(device, time, protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            name = basejid.split('@')[0]
            url = basejid.split('@')[1]
            mex = Message(to=basejid+"/actormanager")
            message="HC ID ["+str(device.house)+"]:["+str(device.device.id)+"]  SEQ 0 " + "http://"+str(url)+"/~gcdemo/"+realpath+"/" +str(es.mydir)+"/"+ str(device.profile) + " " + str(time)
            mex.body = message
            return(mex)
        else:
            mex = Message(to=basejid+"/"+jid)
            message =  """{"message" : {"subject" : "HC","id" : "[""" + str(device.house) + """]:[""" + str(device.device.id) + """]","profile" : "http://parsec2.unicampania.it/~gcdemo/"""+realpath+"/"+str(es.mydir)+"""/"""+str(device.profile)+""" "}}"""
            mex.body = message
            mex.metadata = time
            return(mex)



    def background(device, time, protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            name = basejid.split('@')[0]
            url = basejid.split('@')[1]
            mex = Message(to=basejid+"/actormanager")
            message="BG ID ["+str(device.house)+"]:["+str(device.device.id)+"]  SEQ 0 " + "http://"+str(url)+"/~gcdemo/"+realpath+"/" +str(es.mydir)+"/"+ str(device.profile) + " " + str(time)
            mex.body = message
            return(mex)
        else:

            mex = Message(to=basejid+"/"+jid)
            message =  """{"message" : {"subject" : "BG","id" : "[""" + str(device.house) + """]:[""" + str(device.device.id) + """]","profile" : "http://parsec2.unicampania.it/~gcdemo/"""+realpath+"/"+str(es.mydir)+"""/"""+str(device.profile)+""" "}}"""
            mex.body = message
            mex.metadata = time
            return(mex)




    def charge_on_demand(device, time, protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message = '"message: {"subject": "EV", "capacity":' +str(device.device.capacity)+', "max_ch_pow_ac":' + str(device.device.max_ch_pow_ac) + ',"max_ch_cc":' +str(device.device.max_ch_pow_cc) + ', "max_all_en":' + str(device.device.max_all_en) + ',"min_all_en:' + str(device.device.min_all_en) + ',"sb_ch:"'+str(device.device.sb_ch)+',"ch_eff:"' + str(device.device.ch_eff) + ',"soc_at_arrival":'+str(device.Soc_at_arrival)+',"planned_departure_time":'+str(device.planned_departure_time)+',"arrival_time:"'+str(device.actual_arrival_time)+', "v2g":'+str(device.v2g)+',"target_soc":'+str(device.target_soc)+'}}'
            mex.body = message

            return(mex)
        else:
            mex = Message(to=basejid+"/"+jid)
            message = """{"message" : {"subject" : "EV", "capacity" : " """ + str(device.device.capacity)+  """ " , "max_ch_pow_ac" : " """ + str(device.device.max_ch_pow_ac) +  """ " , "max_ch_cc" : " """ + str(device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(device.device.max_all_en) + """ " , "min_all_en" : " """ + str(device.device.min_all_en) + """ " , "sb_ch" : " """+str(device.device.sb_ch)+ """ " , "ch_eff" :  " """ + str(device.device.ch_eff) +  """ " , "soc_at_arrival": " """ +str(device.Soc_at_arrival)+ """ " , "planned_departure_time" : " """ +str(device.planned_departure_time)+ """ " , "arrival_time" : " """+str(device.actual_arrival_time)+ """ " , "v2g" : " """ +str(device.v2g)+ """ " , "target_soc" : " """+str(device.target_soc)+""" " }}"""
            mex.body = message
            mex.metadata = time
            return(mex)

    def booking_request(device, time, protocol_version):
        global jid
        global basejid
        if (protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message = "EV ID " + device.device.id + " CAPACITY " + device.device.capacity + " MAX_CH_POW_AC " + device.device.max_ch_pow_ac + " MAX_CH_POW_CC " + device.device.max_ch_pow_cc + " MAX_ALL_EN "  + device.device.max_all_en + " MIN_ALL_EN " + device.device.min_all_en + " SB_CH " + device.device.sb_ch + " CH_EFF " + device.device.ch_eff + " SOC_AT_ARRIVAL " + device.Soc_at_arrival + " PLANNED_DEPARTURE_TIME " + device.planned_departure_time + " ARRIVAL_TIME " + device.actual_arrival_time + " V2G " +  device.v2g + " TARGET_SOC "  + device.target_soc + " " + str(time)
            mex.body = message

            return (mex)

        else:
            mex = Message(to=basejid+"/"+jid)

            message = """{"message" : {"subject" : "EV" , "id" : "[""" + str(device.house) + """]:[""" + str(device.device.id) + """]", "capacity" : " """ + str(device.device.capacity)+  """ " , "max_ch_pow_ac" : " """ + str(device.device.max_ch_pow_ac) +  """ " , "max_ch_pow_cc" : " """ + str(device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(device.device.max_all_en) + """ " , "min_all_en" : " """ + str(device.device.min_all_en) + """ " , "sb_ch" : " """ + str(device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(device.device.ch_eff) +  """ " , "soc_at_arrival": " """ + str(device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(device.planned_departure_time) + """ " , "arrival_time" : " """ + str(device.actual_arrival_time) + """ " , "v2g" : " """ + str(device.v2g) + """ " , "target_soc" : " """ + str(device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return (mex)

    def ev_arrival(device, time, protocol_version):
        global jid
        global basejid
        if (protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message = "EV_ARRIVAL CAPACITY " + device.device.capacity + " MAX_CH_POW_AC " + device.device.max_ch_pow_ac + " MAX_CH_POW_CC " + device.device.max_ch_pow_cc + " MAX_ALL_EN "  + device.device.max_all_en + " MIN_ALL_EN " + device.device.min_all_en + " SB_CH " + device.device.sb_ch + " CH_EFF " + device.device.ch_eff + " SOC_AT_ARRIVAL " + device.Soc_at_arrival + " PLANNED_DEPARTURE_TIME " + device.planned_departure_time + " ARRIVAL_TIME " + device.actual_arrival_time + " V2G " +  device.v2g + " TARGET_SOC "  + device.target_soc
            mex.body = message

            return (mex)

        else:
            mex = Message(to=basejid+"/"+jid)
            message = """{"message" : {"subject" : "EV_ARRIVAL" , "capacity" : " """ + str(device.device.capacity)+  """ " , "max_ch_pow_ac" : " """ + str(device.device.max_ch_pow_ac) +  """ " , "max_ch_pow_cc" : " """ + str(device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(device.device.max_all_en) + """ " , "min_all_en" : " """ + str(device.device.min_all_en) + """ " , "sb_ch" : " """ + str(device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(device.device.ch_eff) +  """ " , "soc_at_arrival": " """ + str(device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(device.planned_departure_time) + """ " , "arrival_time" : " """ + str(device.actual_arrival_time) + """ " , "v2g" : " """ + str(device.v2g) + """ " , "target_soc" : " """ + str(device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return (mex)

    def ev_departure(device, time, protocol_version):
        global jid
        global basejid
        if (protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message = "EV_DEPARTURE CAPACITY " + device.device.capacity + " MAX_CH_POW_AC " + device.device.max_ch_pow_ac + " MAX_CH_POW_CC " + device.device.max_ch_pow_cc + " MAX_ALL_EN "  + device.device.max_all_en + " MIN_ALL_EN " + device.device.min_all_en + " SB_CH " + device.device.sb_ch + " CH_EFF " + device.device.ch_eff + " SOC_AT_ARRIVAL " + device.Soc_at_arrival + " PLANNED_DEPARTURE_TIME " + device.planned_departure_time + " ARRIVAL_TIME " + device.actual_arrival_time + " V2G " +  device.v2g + " TARGET_SOC "  + device.target_soc
            mex.body = message

            return (mex)

        else:
            mex = Message(to=basejid+"/"+jid)
            message = """{"message" : {"subject" : "EV_DEPARTURE" , "capacity" : " """ + str(device.device.capacity)+  """ " , "max_ch_pow_ac" : " """ + str(device.device.max_ch_pow_ac) +  """ " , "max_ch_pow_cc" : " """ + str(device.device.max_ch_pow_cc) + """ " , "max_all_en" : " """ + str(device.device.max_all_en) + """ " , "min_all_en" : " """ + str(device.device.min_all_en) + """ " , "sb_ch" : " """ + str(device.device.sb_ch) + """ " , "ch_eff" :  " """ + str(device.device.ch_eff) +  """ " , "soc_at_arrival": " """ + str(device.Soc_at_arrival) + """ " , "planned_departure_time" : " """ + str(device.planned_departure_time) + """ " , "arrival_time" : " """ + str(device.actual_arrival_time) + """ " , "v2g" : " """ + str(device.v2g) + """ " , "target_soc" : " """ + str(device.target_soc) + """ " }}"""
            mex.body = message
            mex.metadata = time
            return (mex)

    def create_producer(device, time, protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            name = basejid.split('@')[0]
            url = basejid.split('@')[1]
            mex = Message(to=basejid+"/actormanager")
            message="CREATE_PRODUCER PV ["+str(device.house)+"]:["+str(device.device.id)+"]  " +  "http://"+str(url)+"/~gcdemo/"+realpath+"/" +str(es.mydir)+"/"+ str(device.profile) + " " + str(time)
            mex.body = message
            return(mex)
        else:

            mex = Message(to=basejid+"/"+jid)
            message =  """{"message" : {"subject" : "CREATE_PRODUCER","type" : "PV","id" : "[""" + str(device.house) + """]:[""" + str(device.device.id) + """]","profile" : "http://parsec2.unicampania.it/~gcdemo/"""+realpath+"/"+str(es.mydir)+"""/"""+str(device.profile)+""" "}}"""
            mex.body = message
            mex.metadata = time
            return (mex)

    def create_load(device,time, protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            name = basejid.split('@')[0]
            url = basejid.split('@')[1]
            mex = Message(to=basejid+"/actormanager")
            message = "LOAD ID [" + str(device.house) + "]:[" + str(device.device.id) + "]:[1] SEQUENCE 1 EST " + str(device.est) + " LST " + str(device.lst) + " PROFILE " +  "http://"+str(url)+"/~gcdemo/"+realpath+"/" +str(es.mydir)+"/"+ str(device.profile)  + " " + str(time)
            mex.body = message

            return(mex)
        else:


            mex = Message(to=basejid+"/"+jid)
            message= """ {"message" :  {"subject" : "LOAD", "id" : "[""" + str(device.house)+ """]:["""+str(device.device.id)+"""]:[1]", "sequence" : "1", "est" : " """ + str(device.est)+ """ ", "lst" : " """ +str(device.lst)+ """ ","profile" : "http://parsec2.unicampania.it/~gcdemo/"""+realpath+"/"+str(es.mydir)+"""/"""+str(device.profile)+""" "}} """
            mex.body = message
            mex.metadata = time
            return (mex)

    def update_producer(device,time,  protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message="UPDATE_PRODUCER"+str(device.house)+"_run_"+str(device.device.id)+"_1.csv" +" "+ str(time)
            mex.body = message
            return(mex)
        else:
            mex = Message(to=basejid+"/"+jid)
            message="UPDATE_PRODUCER"+str(device.house)+"_run_"+str(device.device.id)+"_1.csv"
            mex.body = message
            mex.metadata = time
            return(mex)

    def delete_load(device,time,  protocol_version):
        global jid
        global basejid
        if(protocol_version == "1.0"):
            mex = Message(to=basejid+"/actormanager")
            message="DELETE_LOAD ["+str(device.house)+"]:["+str(device.device.id)+"] " + str(device.consumption) + " "+ str(device.panel) + " " + str(time)
            mex.body = message
            return(mex)
        else:
            mex = Message(to=basejid+"/"+jid)

            message= """{ "message":  {"subject": "DELETE_LOAD", "id": "[""" + str(device.house) + """]:[""" + str(device.device.id) + """]:[1]" , "energy": " """ + str(device.consumption) +""" ", "producer" : " """ + str(device.panel) + """ " }} """
            mex.body = message
            mex.metadata = time
            return(mex)

def calculate_consum(file):
    dirPath2 = dir1+"/Inputs/"+file
    f = open(dirPath2)
    csv_f = csv.reader(f)
    data = 0
    count=0
    for row in csv_f:
        data = row[0].split()[1]
    f.close()
    #data = float(data)/1000
    return data



class dispatcher(Agent):

    def __init__(self,address,passw):
            super(dispatcher,self).__init__(address,passw)
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
                if msg.body=="start":
                    print("Message received with content: {}".format(msg.body))
                    abilitation = True

                elif msg.body=="stop":
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
            WasEnable=False
            with open("config.yml", 'r') as ymlfile:
               cfg = yaml.load(ymlfile, Loader = Loader)
            protocol_version = cfg['config']['protocol']

            completed = 0
            total = es.sharedQueue.qsize()
            percent = 0
            with open("config.yml", 'r') as ymlfile:
                cfg = yaml.load(ymlfile, Loader = Loader)
            path = cfg['config']['simulation_dir']
            with open(path+"/Simulations/"+es.mydir+"/output/output.txt", "w+") as file:
                while(abilitation and finish):

                    #time.sleep(2)
                    #if(firstTime):
                    #    f=open(path+"/output/output.txt", "w+")
                    #    firstTime=False
                    WasEnable= True
                    next2 = es.sharedQueue.get()

                    nextload=next2[2]
                    actual_time = next2[0]
                    try:
                        providedby = next2[3]
                    except:
                        None

                    with open("./time.txt","w") as f2:
                        f2.write(str(next2[0]))
                        f2.close()
                    completed +=1
                    print(nextload)
                    if( nextload.device.type=="Producer"):
                        message = MessageFactory.create_producer(nextload,next2[0],protocol_version)
                        await self.send(message)
                        msg2 = await self.receive(timeout=3)
                        file.write(message.body +"\n")
                        file.flush()


                    elif(nextload.type=="load" and nextload.device.type=="Consumer"):
                        total +=1
                        message = MessageFactory.create_load(nextload,next2[0],protocol_version)
                        await self.send(message)
                        #msg2 = await self.receive()
                        #time.sleep(4)
                        messageFromScheduler = None
                        if(protocol_version == "1.0"):
                            while(isinstance(messageFromScheduler, type(None))):
                                messageFromScheduler = await self.receive(timeout=20)
                            try:
                                print(messageFromScheduler.body)
                                delta = calculateTime(nextload.profile)
                                newTime = str(int(messageFromScheduler.body.split(" ")[3])+int(delta))
                                #es.sharedQueue.put((newTime,es.count,es.eventDelete(nextload.device,nextload.house,messageFromScheduler.body.split(" ")[2],messageFromScheduler.body.split(" ")[2],newTime,nextload.profile,"delete"),messageFromScheduler.body.split(" ")[4]))

                                mydel = es.eventDelete(nextload.device, nextload.house, newTime, calculate_consum(nextload.profile),messageFromScheduler.body.split(" ")[5])
                                with open("config.yml", 'r') as ymlfile:
                                      cfg = yaml.load(ymlfile, Loader = Loader)
                                date = cfg['config']['date'] + " 00:00:00"
                                path = cfg['config']['simulation_dir']
                                with open(path+"/Simulations/"+es.mydir+"/inputs/"+nextload.profile, "r") as f:
                                      with open(path+"/Simulations/"+es.mydir+"/output/"+nextload.profile, "w") as f2:
                                          reader = csv.reader(f)
                                          writer = csv.writer(f2, delimiter =' ')
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
                                             entry.append(int(str(data[0].split(" ")[0]))-absolute+int(messageFromScheduler.body.split(" ")[3]))
                                             entry.append(str(data[0].split(" ")[1]))
                                             writer.writerow(entry)

                                es.sharedQueue.put((newTime,es.count,mydel))
                                es.count +=1
                                print(es.count)
                                file.write(message.body+"\n")

                                file.write(messageFromScheduler.body +"\r\n")
                                file.flush()
                                #time.sleep(2)

                            except:
                                print("unrecognized Message")
                        else:
                            messageFromScheduler = await self.receive(timeout=20)
                            while(not isinstance(messageFromScheduler, type(None))):
                                print(messageFromScheduler.body)
                                if(messageFromScheduler.body == "AckMessage"):
                                        print("Ack Received")

                                else:
                                    try:
                                        delta = calculateTime(nextload.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3])+int(delta))
                                        #es.sharedQueue.put((newTime,es.count,es.eventDelete(nextload.device,nextload.house,messageFromScheduler.body.split(" ")[2],messageFromScheduler.body.split(" ")[2],newTime,nextload.profile,"delete"),messageFromScheduler.body.split(" ")[4]))

                                        mydel = es.eventDelete(nextload.device, nextload.house, newTime, calculate_consum(nextload.profile),messageFromScheduler.body.split(" ")[5])
                                        with open("config.yml", 'r') as ymlfile:
                                              cfg = yaml.load(ymlfile, Loader = Loader)
                                        date = cfg['config']['date'] + " 00:00:00"
                                        path = cfg['config']['simulation_dir']
                                        with open(path+"/Simulations/"+es.mydir+"/inputs/"+nextload.profile, "r") as f:
                                              with open(path+"/Simulations/"+es.mydir+"/output/"+nextload.profile, "w") as f2:
                                                  reader = csv.reader(f)
                                                  writer = csv.writer(f2, delimiter =' ')
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
                                                     entry.append(int(str(data[0].split(" ")[0]))-absolute+int(messageFromScheduler.body.split(" ")[3]))
                                                     entry.append(str(data[0].split(" ")[1]))
                                                     writer.writerow(entry)

                                        es.sharedQueue.put((newTime,es.count,mydel))
                                        es.count +=1
                                        print(es.count)
                                        file.write(message.body+"\n")

                                        file.write(messageFromScheduler.body +"\r\n")
                                        file.flush()
                                        #time.sleep(2)

                                    except Exception as e:
                                        print(e)
                                messageFromScheduler = await self.receive(timeout=20)

                    elif(nextload.type=="delete"):
                        message = MessageFactory.delete_load(nextload,next2[0],protocol_version)
                        await self.send(message)
                        #msg2 = await self.receive(timeout=3)
                        file.write(message.body+"\n")
                        file.flush()


                    elif(nextload.type=="update"  and nextload.device.type=="Producer"):
                        message = MessageFactory.update_producer(nextload,next2[0],protocol_version)
                        await self.send(message)
                        msg2 = await self.receive(timeout=40)

                    #elif(nextload.type == "EV" and nextload.planned_arrival_time == '0'):
                    elif(nextload.type == "EV" and nextload.device.type == "EV_ARRIVAL"):
                        nextload.device.type = "EV_DEPARTURE"

                        message = MessageFactory.booking_request(nextload,next2[0],protocol_version)
                        await self.send(message)
                        file.write(message.body+"\n")
                        file.flush()
                    #elif(nextload.type == "EV" and nextload.planned_arrival_time != '0' and next2[0] == nextload.creation_time):
                    elif(nextload.type == "EV" and nextload.device.type == "EV_BOOKING"):
                            nextload.device.type = "EV_ARRIVAL"
                            message = MessageFactory.booking_request(nextload,next2[0], protocol_version)
                            await self.send(message)
                            file.write(message.body+"\n")
                            file.flush()
                    #elif (nextload.type == "EV" and nextload.planned_arrival_time != '0' and next2[0] != nextload.creation_time):
                    elif(nextload.type == "EV" and nextload.device.type == "EV_DEPARTURE"):
                        message = MessageFactory.booking_request(nextload, next2[0], protocol_version)
                        await self.send(message)
                        file.write(message.body+"\n")
                        file.flush()
                    elif (nextload.type == "heatercooler" ):
                        message = MessageFactory.heatercooler(nextload, next2[0], protocol_version)
                        await self.send(message)
                        print("inviato")
                        file.write(message.body+"\n")
                        file.flush()
                    elif (nextload.type == "background" ):
                        message = MessageFactory.background(nextload, next2[0], protocol_version)
                        print(protocol_version)
                        await self.send(message)

                        file.write(message.body+"\n")
                        file.flush()


                    if(es.sharedQueue.empty()):

                        if(protocol_version == "2.0"):

                            messageFromScheduler = await self.receive(timeout=10)
                            while(not isinstance(messageFromScheduler, type(None))):
                                if(messageFromScheduler.body == "AckMessage"):
                                        print("Ack Received")
                                else:
                                    try:
                                        #print(messageFromScheduler.body)
                                        delta = calculateTime(nextload.profile)
                                        newTime = str(int(messageFromScheduler.body.split(" ")[3])+int(delta))
                                        #es.sharedQueue.put((newTime,es.count,es.event(nextload.device,nextload.house,messageFromScheduler.body.split(" ")[2],messageFromScheduler.body.split(" ")[2],newTime,nextload.profile,"delete"),messageFromScheduler.body.split(" ")[4]))
                                        mydel = es.eventDelete(nextload.device, nextload.house, newTime, calculate_consum(nextload.profile),messageFromScheduler.body.split(" ")[4])


                                        with open(path+"/Simulations/"+es.mydir+"/inputs/"+nextload.profile, "r") as f:
                                              with open(path+"/Simulations/"+es.mydir+"/output/"+nextload.profile, "w") as f2:
                                                  reader = csv.reader(f)
                                                  writer = csv.writer(f2, delimiter =' ')
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
                                                      entry.append(int(str(data[0].split(" ")[0]))-absolute+int(messageFromScheduler.body.split(" ")[3]))
                                                      entry.append(str(data[0].split(" ")[1]))
                                                      writer.writerow(entry)


                                        es.sharedQueue.put((newTime,es.count,mydel))
                                        es.count +=1
                                        file.write(message.body+"\n")
                                        file.write(messageFromScheduler.body +"\r\n")
                                        file.flush()

                                    except:
                                        print("unrecognized Message")
                                messageFromScheduler = await self.receive(timeout=10)
                    if(es.sharedQueue.empty()):
                        message = MessageFactory.end()
                        file.write(message.body+"\n")

                        file.flush()
                        file.close()
                        finish = False
                        print("Simulazione terminata.")


                if(WasEnable):
                    print("Ho rilevato un segnale di stop")
            if(finish == False):
                message = MessageFactory.end()
                await self.send(message)
                await self.agent.stop()




    async def setup(self):
        global basejid
        start_at = datetime.now() + timedelta(seconds=3)
        print("ReceiverAgent started")
        b = self.disRecvBehav(1, start_at=start_at)
        template = Template()
        template2 = Template()
        template = Template()
        with open("config.yml", 'r') as ymlfile:
               cfg = yaml.load(ymlfile, Loader = Loader)
        protocol_version = cfg['config']['protocol']
        if(protocol_version == "1.0"):
           template2.sender = basejid+"/actormanager"
        else:
           template2.sender = basejid+"/adaptor"
        template.set_metadata("control", "startorstop")
        self.add_behaviour(b, template)
        Behaviour2 = self.consumeEvent(1,start_at=start_at)
        self.add_behaviour(Behaviour2,template2)
