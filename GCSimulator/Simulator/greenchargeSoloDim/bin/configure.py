import yaml
import os

class Configuration:
    listDevice = []  # IN THIS LIST WILL BE STORED ALL THE LOADS
    listPanels = []  # IN THIS LIST WILL BE STORED ALL THE PRODUCERS
    listEvent = []
    """dir1 = os.path.dirname(os.path.realpath(__file__))
    dir2 = dir1.split("/")
    dir1 = ""
    for i in range(1,len(dir2)-1):
        dir1 = dir1 +"/"+ dir2[i]
    """
    pathneighbor = 0
    pathload2 = 0
    config_file = 'config.yml'
    parameters = None
    mydir = None


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

            '''
            cls.parameters['date'] = cfg['config']['date'] + " 00:00:00"
            cls.parameters['simulation_dir'] = cfg['config']['simulation_dir']
            cls.parameters['simulation'] = cfg['config']['simulation']
            cls.parameters['webdir'] = cfg['config']['webdir']
            cls.parameters["userjid"] = cfg['config']['userjid']
            cls.parameters['xmpp_password'] = cfg['config']['xmpp_password']
            cls.parameters['simulator'] = cfg['config']['simulator']
            '''
            '''
            dir1 = dir1 + "/" + simd

            datetime_object = datetime.strptime(date, '%m/%d/%y %H:%M:%S')
            workingdir = 0
            webdir = cfg['config']['webdir']
            sharedQueue = queue.PriorityQueue()
            '''
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
            while os.path.exists(cls.parameters['current_sim_dir'] + "/Simulations/" + newdir2 + "_" + str(dirCount1)):
                dirCount1 += 1
            workingdir1 = cls.parameters['current_sim_dir'] + "/Simulations/" + newdir2+"_"+str(dirCount1)
            cls.mydir = workingdir1.split("/")[-1]
            cls.dirCount1 = dirCount1
            # fine codice aggiunto

