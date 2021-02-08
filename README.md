# GreenCharge Simulator
The  GreenCharge  simulator reproduces in a virtual environment the events that occur in a real energy smart neighborhood (ESN) using a collection of real misured data [[1]](#aversa2020). It is based on the original  CoSSMic  simulator [[2]](#amato2018), and allows to extend the evaluation capability in real pilots, which are limited in the heterogeneity and number of devices and in the duration of operating trials.  
The simulator is based on the discrete-event simulation (DES) model where the system appears as a discrete sequence of events in time.  


The Container based deployment configuration allows for an easy deploy of the simulation platform on the user’s workstation, independently from the Operating System. The software architecture is shown in Figure 
![Contaner based deployment](https://25sal.github.io/gcdocker/docs/images/docker_arc.png)

Using both a virtual or a real network many containerized components interoperate through a loosely coupled integration. The blue box represents the simulation engine and its  Graphical User Interface (GUI). The two components use a volume to access simulation input and output data such as configuration of scenarios, time-series and  results.
The XMPP server provides a peer-to-peer communication overlay for multi-agents  distributed implementation. A volume is used to save user-credentials, as the simulator can be used by multiple users who can run their simulations in parallel, in one or in multiple containers.
An optimization model can be integrated as Energy Management Systems (EMS) that  runs in its own container and  uses the Simulator interface to receive simulation events and to return the optimal energy schedule. In particular, the GreenCharge project will evaluate two different EMS innovative technological solutions, developed by the University of Oslo and by the Eurecat partner. Here we investigate an alternative solution that is used also to demonstrate how the simulation platform works.

<a name="aversa2020">[1]</a> R. Aversa, D. Branco, B. Di Martino, and S. Venticinque.  Greenchargesimulation  tool.Advances in Intelligent Systems and Computing,  1150AISC:1343–1351, 2020.

<a name="amato2018">[2]</a> A. Amato, R. Aversa, B. Di Martino, M. Scialdone, and S. Venticinque. Asimulation approach for the optimization of solar powered smart migro-grids.Advances in Intelligent Systems and Computing, 611:844–853, 2018.

## Documentation
* [User Guide](https://25sal.github.io/gcdocker/docs/user_guide/index.html)
* [API documentation](https://25sal.github.io/gcdocker/docs/gcsim/api/index.html)


## Build

### Build Simulator image
From main directory:
```
cd Dockers/gcsim
docker build . --tag gcsim
```

### Build Scheduler image
From main directory:
```
cd Dockers/gcscheduler
docker build . --tag gcscheduler
```

### Instantiate and run prosody, simulator and scheduler containers
```
cd docker-compose up
```

The prosody configuration and the Simulation directory are mapped to the host directories
Currently the simulator container waits for a bash connection

## Run the Simulator
### Start the scheduler
```
docker exec -it docker_gcscheduler_1 bash
./scheduler start
```

### Start the simulator
```
docker exec -it docker_gcsimulator_1 bash
./starter.sh start
```
### Generate the report
```
docker exec -it docker_gcsimulator_1 bash
cd ../Simulations/[simulation_dir]/[simulation_date]_[simulation_id]
python3 postprocess
```
