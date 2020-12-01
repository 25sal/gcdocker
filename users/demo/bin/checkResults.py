import os
import csv
import glob
import xml.etree.ElementTree as ET
import shutil

def doChecks(path, startTime, pathXML):
    try:
        os.remove(path+"/checks/outputParam.csv")
    except:
        pass

    allfiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames if f.endswith('.csv')]
    energyDict = {}
    astDict = {}
    num_of_timeseries = 0
    for file in allfiles:
        num_of_timeseries = num_of_timeseries + 1
        try:
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=' ')
                for row in csv_reader:
                    if(row[1] != '0'):
                        energyDict[file] = row[1]
        except:
            None

    prod_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path+"/PV") for f in filenames if f.endswith('.csv')]
    energyProducerDict = {}
    for file in prod_files:
        try:
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=' ')
                for row in csv_reader:
                    if(row[1] != '0'):
                        energyProducerDict[file] = row[1]
        except:
            None
    
    ev_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path+"/EV") for f in filenames if f.endswith('.csv')]
    energyEVDict = {}
    for file in ev_files:
        try:
            with open(file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=' ')
                for row in csv_reader:
                    if(row[1] != '0'):
                        energyEVDict[file] = row[1]
        except:
            None
    
    totalEnergyConsumption = 0
    for key,energy in energyDict.items():
        totalEnergyConsumption += float(energy)

    totalEnergyCharged = 0
    for key,energy in energyEVDict.items():
        totalEnergyCharged += float(energy)

    totalEnergyProduced = 0
    for key,energy in energyProducerDict.items():
        totalEnergyProduced += float(energy)
    
    totalEnergyConsumption = totalEnergyConsumption - totalEnergyProduced

    file1 = open(path+'/output.txt', 'r') 
    Lines = file1.readlines()
    for line in Lines:
        splittedMessage = line.split(" ")
        if(splittedMessage[0] == "<<<" or splittedMessage[0] == ">>>"):
            if(splittedMessage[1] == "ASSIGNED_START_TIME"):
                astDict[splittedMessage[2]] = splittedMessage[4].rstrip()


    producer_consumer = [f.split("/")[-1] for f in glob.glob(path+"/*.csv")]
    
    PVListResampled = {}
    for key,energy in energyProducerDict.items():
        PVListResampled[key] = generateTimeSeries(key,startTime)

    ConsumerResampled = {}
    for key,energy in energyDict.items():
        if(key not in PVListResampled):
            ConsumerResampled[key] = generateTimeSeries(key,startTime)

    #print(ConsumerResampled)
    totalCon = 0
    totalProd = 0
    for i in range(144):
        tempCon = 0
        tempProd = 0
        for key,energy in ConsumerResampled.items():
            tempCon += energy[i][1]
        for key,energy in PVListResampled.items():
            tempProd += energy[i][1]
        if(tempCon<tempProd):
            totalCon += tempCon
        else:
            totalCon += tempProd
        totalProd += tempProd
    if(totalProd != 0):
        selfC = totalCon/totalProd
    else:
        selfC = 0
    
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
        json_file.write('{id:1,data:[ "Total_Energy_Consumption","'+ str(totalEnergyConsumption)+'","","",""]},')
        json_file.write('{id:2,data:[ "Total_Energy_Production","'+ str(totalEnergyProduced)+'","","",""]},')
        json_file.write('{id:3,data:[ "Assigned Start Time List","'+ str(astDict)+'","","",""]},')
        json_file.write('{id:4,data:[ "Energy_charged","'+ str(totalEnergyCharged)+'","","",""]},')
        json_file.write('{id:5,data:[ "Number_of_Timeseries","'+ str(num_of_timeseries)+'","","",""]},')
        json_file.write('{id:6,data:[ "Self_Consumption","'+ str(selfC)+'","","",""]}')
        json_file.write(']};')
    
    # temporary

    with open(path+"/checks/checks.js", "w") as json_file:
        json_file.write("coherence_checks={rows:[")
        json_file.write('{id:1,data:[ "Total_Energy_Consumption","'+ str(totalEnergyConsumption)+'","","",""]},')
        json_file.write('{id:2,data:[ "Total_Energy_Production","'+ str(totalEnergyProduced)+'","","",""]},')
        json_file.write('{id:3,data:[ "Assigned Start Time List","'+ str(astDict)+'","","",""]},')
        json_file.write('{id:4,data:[ "Energy_charged","'+ str(totalEnergyCharged)+'","","",""]},')
        json_file.write('{id:5,data:[ "Number_of_Timeseries","'+ str(num_of_timeseries)+'","","",""]},')
        json_file.write('{id:6,data:[ "Self_Consumption","'+ str(selfC)+'","","",""]}')
        json_file.write(']};')
                

    print("Total_Energy_Consumption: " + str(totalEnergyConsumption))
    print("Total_Energy_Production: " + str(totalEnergyProduced))
    print("Assigned Start Time List: ") 
    print(astDict)
    print("Number_of_Timeseries: " + str(num_of_timeseries))
    print("Energy_charged: " + str(totalEnergyCharged))
    print("Self_Consumption " + str(selfC))


    tree = ET.parse(pathXML +'/loads.xml')
    neighborhood = tree.getroot()
    peakLoadList = {}
    buildingID = "["
    for elem in neighborhood:
        buildingID = "["
        if 'peakLoad' in elem.attrib:
            buildingID += elem.attrib['id']+"]"
            peakLoadList[buildingID] = elem.attrib['peakLoad']
            buildingID += ":["
            for subelement in elem:
                if 'peakLoad' in subelement.attrib:
                    tempo = buildingID + subelement.attrib['id']+"]"
                    peakLoadList[tempo] = subelement.attrib['peakLoad']
                for subsubelement in subelement:
                    if 'peakLoad' in subsubelement.attrib:
                        tempo = buildingID + subsubelement.attrib['id']+"]"
                        peakLoadList[tempo] = subsubelement.attrib['peakLoad']
    print(peakLoadList)





def generateTimeSeries(file, startTime):
    List = [[None] * 2 for i in range(0,144)]
    for i in range(144):
        List[i][0] = int(startTime) + i*600
    previous = 0
    i = 0
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= ' ')
        data = list(csv_reader)
        row_count = len(data)
        energyTimeSeries = [[None] * 2 for i in range(0,row_count)]


    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter= ' ')
        for row in csv_reader:
            if(float(row[1]) != 0):
                energyTimeSeries[i][1] = float(row[1]) - previous
            else:
                energyTimeSeries[i][1] = 0
            energyTimeSeries[i][0] = float(row[0])
            previous = float(row[1])
            i+=1

    for i in range(0,143):
        line_count = 0
        List[i][1] = 0
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=' ')
            index = 0
            for row in csv_reader:

                if(int(energyTimeSeries[index][0])>=List[i][0] and int(energyTimeSeries[index][0])<List[i+1][0]):
                    List[i][1] += float(energyTimeSeries[index][1])
                    line_count +=1
                index +=1
        if(line_count != 0):
            List[i][1] = List[i][1]/line_count
    List[143][1] = 0
    return List


if __name__ == "__main__":

    doChecks("/home/gc/Simulations/trivial/Results/12_12_15_82/output", 1449878400,"/home/gc/Simulations/trivial/Results/12_12_15_82/xml")




