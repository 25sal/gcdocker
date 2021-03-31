import yaml
import os, sys
import subprocess
sys.path.insert(0, '/home/gc/simulator/bin')
import gcsim as sim
from multiprocessing import Process
import time
from datetime import datetime,date, timedelta

if __name__ == "__main__":
	days = []
	position = 1
	arguments = len(sys.argv) - 1
	while (arguments >= position):
		if(position == 1):
			sdate = date(month = int(sys.argv[position].split('-')[0]), day = int(sys.argv[position].split('-')[1]), year = int(sys.argv[position].split('-')[2]))
		elif(position == 2):
			edate = date(month = int(sys.argv[position].split('-')[0]), day =  int(sys.argv[position].split('-')[1]), year = int(sys.argv[position].split('-')[2]))
		position = position + 1
	delta = edate - sdate  # as timedelta
	for i in range(delta.days + 1):
		day = sdate + timedelta(days=i)
		days.append(day.strftime("%m-%d-%y"))
	print(days)
	for dir in os.listdir("../Simulations/dates/"):
		if(dir in days):
			for dir2 in os.listdir("../Simulations/dates/"+dir):
				newDate = dir.replace('-', '/')
				with open('./config.yml') as f:
					data = yaml.load(f, Loader=yaml.FullLoader)
					data["config"]["date"] = str(newDate)
					data["config"]["simulation"] = dir2
					data["config"]["simulation_dir"] = "/home/gc/Simulations/dates/"+dir
					f.close()
					with open('./config.yml', 'w') as f:
						yaml.dump(data, f)
					p = Process(target=sim.startBycode, args=())
					p.start()
					time.sleep(5)
					active = True
					while(active):
						with open('../simulator/gcdaemon.pid', 'r') as f:
							r = f.readline()
						try:
							os.getpgid(int(r))
						except:
							active = False
					print('Simulazione terminata')
					
    					

    