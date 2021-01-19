# gcdocker

## Build Simulator image
From main directory:
```
cd Dockers/gcsim
docker build . --tag gcsim
```

## Build Scheduler image
From main directory:
```
cd Dockers/gcscheduler
docker build . --tag gcscheduler
```

## Build prosody, simulator and scheduler containers
```
cd docker-compose up
```

The prosody configuration and the Simulation directory are mapped to the host directories
Currently the simulator container waits for a bash connection

## Run the scheduler
```
docker exec -it docker_gcscheduler_1 bash
./scheduler start
```

## Run the simulator
```
docker exec -it docker_gcsimulator_1 bash
./starter.sh start
```
## Generate Charts
```
docker exec -it docker_gcsimulator_1 bash
cd ../Simulations/[simulation_dir]/[simulation_date]_[simulation_id]
python3 postprocess
```
