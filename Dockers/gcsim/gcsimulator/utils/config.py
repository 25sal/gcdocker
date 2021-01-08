import yaml
import os



######################################################################################
# This class manages scenario's configuration and static data written in config.yml. #
######################################################################################
class Configuration:
    listDevice = []  # IN THIS LIST WILL BE STORED ALL THE LOADS
    listPanels = []  # IN THIS LIST WILL BE STORED ALL THE PRODUCERS
    listEvent = []
    pathneighbor = 0
    pathload2 = 0
    config_file = '/home/gc/bin/config.yml'
    parameters = None
    mydir = None
    messageToWait = None

    @classmethod
    def set_config_file(cls, config_file='config.yml'):
        cls.config_file = config_file

    @classmethod
    def load(cls):
        if cls.config_file is None:
            raise Exception("Config File is not set")
        with open(cls.config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.Loader)
            cls.parameters = cfg['config']
            cls.parameters['current_sim_dir'] = cls.parameters['simulation_dir'] + '/' + cls.parameters['simulation']
            cls.parameters['webdir'] = cfg['config']['webdir']
            if(cls.parameters['forcedwait'] == False):
                cls.messageToWait = ['load']
            else:
                cls.messageToWait = ['load','heatercooler', 'background', 'LoadUpdate', 'EV']

            mydir = 0
            # codice aggiunto perchè non funzionava la directory web nel dispatcher
            date3 = cls.parameters['date'] .split()
            newdir2 = date3[0].replace('/','_')
            sim_temp2 = newdir2.split("_")
            lock1 = False
            if len(sim_temp2[0]) == 1:
                sim_temp2[0] =  "0" + sim_temp2[0]
                lock1 = True
            if len(sim_temp2[1]) == 1:
                sim_temp2[1] = "0" + sim_temp2[1]
                lock1 = True
            if lock1:
                newdir2 = sim_temp2[0] + "_" + sim_temp2[1] + "_" + sim_temp2[2]
            dirCount1 = 1
            while os.path.exists(cls.parameters['current_sim_dir'] + "/Results/" + newdir2 + "_" + str(dirCount1)):
                dirCount1 += 1
            cls.parameters['runtime_dir'] = cls.parameters['current_sim_dir'] + "/Results/" + newdir2+"_"+str(dirCount1)
            temp =  cls.parameters['runtime_dir'].split("/")
            cls.parameters['user_dir'] = temp[-1]
            cls.dirCount1 = dirCount1
            # fine codice aggiunto

