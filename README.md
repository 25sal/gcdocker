# gcdocker

## Build Simulator image
```
cd docker
docker build . --tag gcsim
```

## Build prosody and simulator containers
```
cd docker-compose up
```

The prosody configuration and the Simulation directory are mapped to the host directories
Currently the simulator container waits for a bash connection

## Run the simulator
```
docker exec -it docker_gcsimulator_1 bash
./starter.sh
```
