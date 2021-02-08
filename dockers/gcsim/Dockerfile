FROM ubuntu:20.04



WORKDIR /home/gc/bin
RUN apt-get update
RUN echo 'debconf debconf/frontend select Noninteractive' |  debconf-set-selections
RUN apt-get -y -q install apt-utils
RUN apt-get update
run apt-get -y -q install software-properties-common
RUN apt-get -y -q install tzdata
RUN echo "ENTER" | add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get -y -q install python3.7 python3-pip
RUN python3.7 -m pip install spade aiohttp_cors pyyaml ptvsd daemon daemons
# Maybe you will need to reconfigure the timezone as well:
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata
COPY requirements.txt ./
#RUN pip3 install --no-cache-dir -r requirements.txt
RUN mkdir -p /home/gc
RUN mkdir -p /var/www/Simulations/demo
RUN mkdir -p /home/gc/simulator
#COPY users/demo/bin /home/gc/bin
# RUN chmod +x /home/gc/bin/starter.sh
#COPY ./gcsimulator/simulator/greenchargeSoloDim/bin /usr/local/lib/python3.8/dist-packages/gcsimulator
#ENTRYPOINT [ "./starter.sh"]
#CMD ["trivial"]
