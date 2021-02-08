
FROM ubuntu:20.04

WORKDIR /home/scheduler
RUN apt-get update
RUN echo 'debconf debconf/frontend select Noninteractive' |  debconf-set-selections
RUN apt-get -y -q install apt-utils 
RUN apt-get -y -q install tzdata nodejs nano
# Maybe you will need to reconfigure the timezone as well:
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata
#COPY requirements.txt ./
#RUN pip3 install --no-cache-dir -r requirements.txt
RUN mkdir -p /home/scheduler
#RUN mkdir -p /var/www/Simulations/demo
#COPY users/demo/bin /home/gc/bin
#RUN chmod +x ./starter.sh
#COPY gcsimulator/simulator/greenchargeSoloDim/bin /usr/local/lib/python3.8/dist-packages/gcsimulator
#ENTRYPOINT [ "./starter.sh"]
#CMD ["trivial"]