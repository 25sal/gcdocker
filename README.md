# gcdocker
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
