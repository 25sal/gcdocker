FROM ubuntu:20.04


RUN mkdir -p /home/gc/Simulations
RUN mkdir -p /var/www/Simulations/demo
WORKDIR /home/gc
RUN apt-get update
RUN echo 'debconf debconf/frontend select Noninteractive' |  debconf-set-selections
RUN apt-get -y -q install apt-utils 
RUN apt-get -y -q install python3 python3-pip tzdata
# Maybe you will need to reconfigure the timezone as well:
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY users/demo/bin .
RUN chmod +x ./starter.sh
COPY GCSimulator/Simulator/greenchargeSoloDim/bin /usr/local/lib/python3.8/dist-packages/gcsimulator
#CMD [ "python", "./bin/gcsimulator.py" ]
