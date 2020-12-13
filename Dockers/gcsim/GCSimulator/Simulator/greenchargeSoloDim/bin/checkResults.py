import os
import csv
import glob
import xml.etree.ElementTree as ET
import shutil
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np


class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.data = [[0] for i in range(0,288)]

    def addChild(self, name):
        node = Node(name)
        self.children.append(node)
        return node
    
    def addData(self, dataList):
        for i in range (0,288):
            self.data[i] += dataList[i]


class Checker:
    energyDict = {}
    astDict = {}
    num_of_timeseries = 0
    energyProducerDict = {}
    energyEVDict = {}
    totalEnergyConsumption = 0
    totalEnergyCharged = 0
    totalEnergyProduced = 0
    powerPeakListFiles = {}
    energyChargedWithIdAsKey = {}
    PVListResampled = {}
    ConsumerResampled = {}
    SelfConsumedEnergy = 0
    totalProd = 0
    selfC = 0
    peakLoadList = {}
    aatList = {}
    adtList = {}
    socList = {}
    estlstList = {}
    listOfPeaks = {}
    root = '.'
    reachedLimits = {}
    ast_lst_constraint = {}
    estlstList = {}
    capacityList = {}
    maxCHList = {}
    minCHList = {}
    energy_respected_to_capacity = {}
    energy_charged_respect_to_Connection = {}
    SelfConsumedEnergyRespectToPVProduction = ''
    idTofilenameEV = {}
    chargingPowerLowerThanMaxChPowConstraint = {}


    def doChecks(self,path, startTime, pathXML):
        try:
            os.remove(path+"/checks/outputParam.csv")
        except:
            pass
        allfiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames if f.endswith('.csv')]
        self.readConsumptionProduction(allfiles, self.energyDict)
        prod_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path+"/PV") for f in filenames if f.endswith('.csv')]
        self.readConsumptionProduction(prod_files, self.energyProducerDict)   
        ev_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path+"/EV") for f in filenames if f.endswith('.csv')]
        self.readConsumptionProduction(ev_files, self.energyEVDict)
        for key,energy in self.energyDict.items():
            self.totalEnergyConsumption += float(energy)
        for key,energy in self.energyEVDict.items():
            self.totalEnergyCharged += float(energy)
        for key,energy in self.energyProducerDict.items():
            self.totalEnergyProduced += float(energy)
        self.totalEnergyConsumption = self.totalEnergyConsumption - self.totalEnergyProduced
        self.workWithOutputTXT(path)
        for key,value in self.powerPeakListFiles.items():
            self.powerPeakListFiles[key] = generatePowerTimeSeries(value,startTime)
        for key,energy in self.energyProducerDict.items():
            self.PVListResampled[key] = generateEnergyTimeSeries(key,startTime)
        for key,energy in self.energyDict.items():
            if(key not in self.PVListResampled):
                self.ConsumerResampled[key] = generateEnergyTimeSeries(key,startTime)
        self.calculateSelfConsumption()
        self.readLoadXML(pathXML, startTime)
        sumForPowerPeak(self.root, self.powerPeakListFiles)
        findPeak(self.root, self.listOfPeaks)
        self.checkPowerPeakConstraint()
        self.readNeighborhoodXML(pathXML, startTime)
        self.checkEnergyRespectToCapacityConstraint()
        self.checkEnergyRespectToConnectionTime()
        self.checkSelfConsumedEnergyRespectToProduction()
        self.checkChargingPowerLowerThanMaxChPowConstraint(startTime)

        self.writeOutput(path)


    def checkChargingPowerLowerThanMaxChPowConstraint(self, startTime):
        for key, filename in self.idTofilenameEV.items():
            powerProfile = generatePowerTimeSeries(filename,startTime)
            respected = 1
            for element in powerProfile:
                if(float(element)>float(self.maxCHList[key][0])):
                    respected = 0
            if(respected == 0):
                self.chargingPowerLowerThanMaxChPowConstraint[key] = 'NotRespected'
            else:
                self.chargingPowerLowerThanMaxChPowConstraint[key] = 'Respected'


    def checkSelfConsumedEnergyRespectToProduction(self):
        if(self.SelfConsumedEnergy <= self.totalProd):
            self.SelfConsumedEnergyRespectToPVProduction = 'Respected'
        else:
            self.SelfConsumedEnergyRespectToPVProduction = 'Not Respected'



    def checkEnergyRespectToCapacityConstraint(self):
        for key,capacity in self.capacityList.items():
            if(float(self.energyChargedWithIdAsKey[key]) + (float(self.socList[key][0])*float(capacity[0]))/100 < float(capacity[0])):
                self.energy_respected_to_capacity[key] = 'Respected'
            else:
                self.energy_respected_to_capacity[key] = 'Not Respected'

    def checkEnergyRespectToConnectionTime(self):
        for key,capacity in self.adtList.items():
            if((float(self.adtList[key][0]) - (float(self.aatList[key][0])))*float(self.maxCHList[key][0]) > float(self.energyChargedWithIdAsKey[key])):
                self.energy_charged_respect_to_Connection[key] = 'Respected'
            else:
                self.energy_charged_respect_to_Connection[key] = 'Not Respected'

    def checkPowerPeakConstraint(self):
        for key,peak in self.peakLoadList.items():
            if(float(self.listOfPeaks[key][0])*1000 > float(peak)):
                self.reachedLimits[key] = 'reached'
            else:
                self.reachedLimits[key] = 'not reached'

    def checkASTConstraint(self):
        for key,ast in self.astDict.items():
            if(float(ast)<float(self.estlstList[key][1]) and float(ast)>float(self.estlstList[key][0])):
                self.ast_lst_constraint[key] = 'Respected'
            else:
                self.ast_lst_constraint[key] = 'not Respected'    

    def readNeighborhoodXML(self, pathXML, startTime):
        tree = ET.parse(pathXML +'/neighborhood.xml')
        neighborhood = tree.getroot()
        buildingID = "["
        for elem in neighborhood:
            buildingID = "["
            root = Node("root")
            if 'peakLoad' in elem.attrib:
                buildingID += elem.attrib['id']+"]"
                buildingID += ":["
                for subelement in elem:
                    if 'peakLoad' in subelement.attrib:
                        tempo = buildingID + subelement.attrib['id']+"]"
                    for subsubelement in subelement:
                        if 'peakLoad' in subsubelement.attrib:
                            tempo = buildingID + subsubelement.attrib['id']+"]"
                        for ecar in subsubelement:
                            if(ecar.tag == "ecar"):
                                tempo = '[' + ecar.find("id").text+']'
                                self.capacityList[tempo] = [float(ecar.find("capacity").text)]
                                self.maxCHList[tempo] = [float(ecar.find("maxchpowac").text)]
                                self.minCHList[tempo] = [float(ecar.find("maxchpowac").text)] #DA CAMBIARE IN MIN 


    def readLoadXML(self, pathXML, startTime):
        tree = ET.parse(pathXML +'/loads.xml')
        neighborhood = tree.getroot()
        buildingID = "["
        for elem in neighborhood:
            buildingID = "["
            self.root = Node("root")
            elemNode = self.root.addChild("["+elem.attrib['id']+"]")
            if 'peakLoad' in elem.attrib:
                buildingID += elem.attrib['id']+"]"
                self.peakLoadList[buildingID] = elem.attrib['peakLoad']
                buildingID += ":["
                for subelement in elem:
                    if 'peakLoad' in subelement.attrib:
                        tempo = buildingID + subelement.attrib['id']+"]"
                        self.peakLoadList[tempo] = subelement.attrib['peakLoad']
                        elemNode.addChild(tempo)
                    for subsubelement in subelement:
                        if 'peakLoad' in subsubelement.attrib:
                            tempo = buildingID + subsubelement.attrib['id']+"]"
                            self.peakLoadList[tempo] = subsubelement.attrib['peakLoad']
                            elemNode.addChild(tempo)
                        elif(subsubelement.tag == "device"):
                            tempo = buildingID + subsubelement.find("id").text+']'
                            if(subsubelement.find("est").text != "0" and subsubelement.find("lst").text != "0"):
                                self.estlstList[tempo] = [int(subsubelement.find("est").text) + int(startTime), int(subsubelement.find("lst").text) + int(startTime)]
                        for ecar in subsubelement:
                            if(ecar.tag == "ecar"):
                                tempo = '[' + ecar.find("id").text+']'
                                self.aatList[tempo] = [float(ecar.find("aat").text)]
                                self.adtList[tempo] = [float(ecar.find("adt").text)]
                                self.socList[tempo] = [float(ecar.find("soc").text)] #DA CAMBIARE IN MIN   


    def calculateSelfConsumption(self):
        for i in range(288):
            tempCon = 0
            tempProd = 0
            for key,energy in self.ConsumerResampled.items():
                tempCon += energy[i]
            for key,energy in self.PVListResampled.items():
                tempProd += energy[i]
            if(tempCon<tempProd):
                self.SelfConsumedEnergy += tempCon
            else:
                self.SelfConsumedEnergy += tempProd
            self.totalProd += tempProd
        if(self.totalProd != 0):
            self.selfC = self.SelfConsumedEnergy/self.totalProd
        else:
            self.selfC = 0


    def readConsumptionProduction(self, allfiles, dictionary):
            for file in allfiles:
                self.num_of_timeseries = self.num_of_timeseries + 1
                try:
                    with open(file) as csv_file:
                        csv_reader = csv.reader(csv_file, delimiter=' ')
                        for row in csv_reader:
                            if(row[1] != '0'):
                                dictionary[file] = row[1]
                except:
                    None
            try:
                del dictionary["outputParam.csv"]
            except KeyError:
                pass

    def workWithOutputTXT(self, path):
        file1 = open(path+'/output.txt', 'r') 
        Lines = file1.readlines()
        for line in Lines:
            splittedMessage = line.split(" ")
            if(splittedMessage[0] == "<<<" or splittedMessage[0] == ">>>"):
                if(splittedMessage[1] == "ASSIGNED_START_TIME"):
                    self.astDict[splittedMessage[2]] = splittedMessage[4].rstrip()
                if(splittedMessage[1] == "LOAD"):
                    idList = splittedMessage[2].split(':')
                    idList.pop()
                    id = ''
                    first = 1
                    for value in idList:
                        if(first == 1):
                            id = value
                            first = 0
                        else:
                            id = id + ':' + value
                    csv_name = path+'/'+splittedMessage[6].split('/')[-1]
                    self.powerPeakListFiles[id] = csv_name
                if(splittedMessage[1] == "EV"):
                    id = splittedMessage[6]
                    csv_name = path+'/EV/'+ splittedMessage[3]+'.csv'
                    self.powerPeakListFiles[id] = csv_name
                    longId =  splittedMessage[2]
                    self.energyChargedWithIdAsKey[longId] = self.energyEVDict[csv_name]
                    self.idTofilenameEV[longId] = csv_name

    def writeOutput(self, path):
        try:
            os.mkdir(path+"/checks")
        except:
            pass
        '''
        with open(path+"/checks/outputParam.csv", "w") as csv_file:
                    param_writer = csv.writer(csv_file, delimiter=' ', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    param_writer.writerow(["Total_Energy_Consumption", str(totalEnergyConsumption)])
                    param_writer.writerow(["Total_Energy_Production", str(totalEnergyProduced)])
                    param_writer.writerow(["Assigned Start Time List", str(astDict)])
                    param_writer.writerow(["Number_of_Timeseries", str(num_of_timeseries)])
                    param_writer.writerow(["Energy_charged", str(totalEnergyCharged)])
                    param_writer.writerow(["Self_Consumption", str(selfC)])
        '''

        with open(path+"/checks/parameters.js", "w") as json_file:
            json_file.write("data={rows:[")
            json_file.write('{id:1,data:[ "Total_Energy_Consumption","'+ str(self.totalEnergyConsumption)+'","","",""]},')
            json_file.write('{id:2,data:[ "Total_Energy_Production","'+ str(self.totalEnergyProduced)+'","","",""]},')
            json_file.write('{id:3,data:[ "Assigned Start Time List","'+ str(self.astDict)+'","","",""]},')
            json_file.write('{id:4,data:[ "Energy_charged","'+ str(self.totalEnergyCharged)+'","","",""]},')
            json_file.write('{id:5,data:[ "Number_of_Timeseries","'+ str(self.num_of_timeseries)+'","","",""]},')
            json_file.write('{id:6,data:[ "Self_Consumption","'+ str(self.selfC)+'","","",""]}')
            json_file.write(']};')
        
        # temporary

        with open(path+"/checks/checks.js", "w") as json_file:
            json_file.write("coherence_checks={rows:[")
            json_file.write('{id:1,data:[ "Total_Energy_Consumption","'+ str(self.totalEnergyConsumption)+'","","",""]},')
            json_file.write('{id:2,data:[ "Total_Energy_Production","'+ str(self.totalEnergyProduced)+'","","",""]},')
            json_file.write('{id:3,data:[ "Assigned Start Time List","'+ str(self.astDict)+'","","",""]},')
            json_file.write('{id:4,data:[ "Energy_charged","'+ str(self.totalEnergyCharged)+'","","",""]},')
            json_file.write('{id:5,data:[ "Number_of_Timeseries","'+ str(self.num_of_timeseries)+'","","",""]},')
            json_file.write('{id:6,data:[ "Self_Consumption","'+ str(self.selfC)+'","","",""]}')
            json_file.write(']};')

        with open(path+"/checks/outputParam.csv", "w") as csv_file:
                param_writer = csv.writer(csv_file, delimiter=' ', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                param_writer.writerow(["Total_Energy_Consumption", str(self.totalEnergyConsumption)])
                param_writer.writerow(["Total_Energy_Production", str(self.totalEnergyProduced)])
                param_writer.writerow(["Number_of_Timeseries", str(self.num_of_timeseries)])
                param_writer.writerow(["Energy_charged", str(self.totalEnergyCharged)])
                param_writer.writerow(["Self_Consumption", str(self.selfC)])
                param_writer.writerow(["Assigned Start Time List", str(self.astDict)])
                param_writer.writerow(["ast_lst_List", str(self.estlstList)])
                param_writer.writerow(["AstLstContraintRespected", str(self.ast_lst_constraint)])
                param_writer.writerow(["PowerPeaksReached", str(self.listOfPeaks)])
                param_writer.writerow(["PowerPeaksLimits", str(self.peakLoadList)])
                param_writer.writerow(["PowerPeaksLimitsReached", str(self.reachedLimits)])
                param_writer.writerow(["Energy_Charged_respect_to_capacity", str(self.energy_respected_to_capacity)])
                param_writer.writerow(["Energy_Charged_respect_to_Connection", str(self.energy_charged_respect_to_Connection)])
                param_writer.writerow(["Energy_AutoConsumed_Respect_To_Energy_Produced", str(self.SelfConsumedEnergyRespectToPVProduction)])
                param_writer.writerow(["Charging_Power_Lower_than_Maximum", str(self.chargingPowerLowerThanMaxChPowConstraint)])

                


def findPeak(node, listOfPeaks):
    max = 0
    for i in range(0,287):
        if(node.data[i]>max):
            max = node.data[i]
    if(node.name != 'root'):
        listOfPeaks[node.name] = max

    for nodechild in node.children:
        findPeak(nodechild, listOfPeaks)


def printChilds(node):
    print(node.name)
    for i in range(0,287):
        print(node.data[i])
    for childNode in node.children:
        printChilds(childNode)


def sumForPowerPeak(node, dictConsumer):
    for nodechild in node.children:
        powerList = sumForPowerPeak(nodechild, dictConsumer)
        for i in range(0,287):
            node.data[i] += powerList[i]
    for key,consumer in dictConsumer.items():
        if(key == node.name):
            for i in range(0,287):
                node.data[i] += consumer[i]
    return node.data


def generateEnergyTimeSeries(file, startTime):
    endTime = startTime + 86400
    with open(file, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter= " ") 
        count = 0  
        x = []     #lista dei tempi della timeseries
        y = []     #lista dei valori della timeseries
        lastSample = 0
        lastValue = 0     #Questo mi serve per tenermi in memoria il valore di energia precedente alla riga che sto leggendo, cosi posso farmi il delta per la trasformazione in potenza
        for row in csv_reader:              #per tutte le righe
            if(count != 0):  #salto la prima riga della ts
                if(float(row[1]) != 0):
                    x.append(float(row[0]))     #aggiunto il tempo alla lista dei tempi 
                    y.append((float(row[1])-lastValue))
                else:
                    x.append(float(row[0]))     #aggiunto il tempo alla lista dei tempi 
                    y.append((float(row[1])))
            else:
                if(startTime < float(row[0])):     #faccio in modo che se il primo tempo della timeseries é piú grande del minimo del periodo di interesse ci piazzo uno zero, cosi dopo non ho problemi quando vado a ricampionare 
                    x.append(startTime) 
                    y.append(0)   
                else:
                    x.append(float(row[0]))     #aggiunto il tempo alla lista dei tempi 
                    y.append(float(row[1]))     #aggiungo alla lista dei valori la potenza 
            lastSample = float(row[0]) 
            lastValue = float(row[1])   #aggiorno l'energia precedente
            count += 1  #aggiorno il count quando ho finito la riga
    if(endTime > lastSample):   #stesso discorso di prima, se l'ultimo tempo della timeseries é piú piccolo del massimo tempo di interesse metto uno zero per non aver problemi dopo
        y.append(0)    
        x.append(endTime)
    f = interpolate.interp1d(x,y)   #faccio l'interpolazione lineare
    xnew = np.arange(startTime,endTime, 300)   #mi creo il vettore dei tempi con un sample ogni 5 minuti (300 secondi)
    ynew = f(xnew)
    return ynew

def generatePowerTimeSeries(file, startTime):
    endTime = startTime + 86400
    with open(file, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter= " ") 
        count = 0  
        x = []     #lista dei tempi della timeseries
        y = []     #lista dei valori della timeseries
        lastSample = 0      #Questo mi serve per tenermi in memoria il tempo precedente alla riga che sto leggendo, cosi posso farmi il delta per la trasformazione in potenza
        lastValue = 0     #Questo mi serve per tenermi in memoria il valore di energia precedente alla riga che sto leggendo, cosi posso farmi il delta per la trasformazione in potenza
        for row in csv_reader:              #per tutte le righe
            if(count != 0):  #salto la prima riga della ts perché devo convertire in potenza 
                x.append(float(row[0]))     #aggiunto il tempo alla lista dei tempi 
                y.append((float(row[1])-lastValue)/(float(row[0])-lastSample))
            else:
                if(startTime < float(row[0])):     #faccio in modo che se il primo tempo della timeseries é piú grande del minimo del periodo di interesse ci piazzo uno zero, cosi dopo non ho problemi quando vado a ricampionare 
                    x.append(startTime) 
                    y.append(0)    #aggiungo alla lista dei valori la potenza 
            lastSample = float(row[0])  #aggiorno il tempo precedente
            lastValue = float(row[1])   #aggiorno l'energia precedente
            count += 1  #aggiorno il count quando ho finito la riga
    if(endTime > lastSample):   #stesso discorso di prima, se l'ultimo tempo della timeseries é piú piccolo del massimo tempo di interesse metto uno zero per non aver problemi dopo
        y.append(0)    
        x.append(endTime)
    f = interpolate.interp1d(x,y)   #faccio l'interpolazione lineare
    xnew = np.arange(startTime,endTime, 300)   #mi creo il vettore dei tempi con un sample ogni 5 minuti (300 secondi)
    ynew = f(xnew)    # genero la nuova serie di potenze ricampionatew
    return ynew


if __name__ == "__main__":

    checker = Checker()
    checker.doChecks("/home/gc/Simulations/trivial/Results/12_12_15_20/output", 1449878400,"/home/gc/Simulations/trivial/Results/12_12_15_20/xml")
    
  