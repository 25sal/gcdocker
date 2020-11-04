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
node sched
```

## Run the simulator
```
docker exec -it docker_gcsimulator_1 bash
./starter.sh
```
