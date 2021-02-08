#!/bin/python3
import yaml
import argparse


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='set simulation')
	parser.add_argument('simulation', metavar='SIM_DIR', type=str,
	 help='simulation directory')

	args = parser.parse_args()

	with open('config.yml') as f:
		
		data = yaml.load(f, Loader=yaml.FullLoader)
		data["config"]["simulation"] = args.simulation
		f.close()
		with open('config.yml', 'w') as f:
			yaml.dump(data, f)
		
    
