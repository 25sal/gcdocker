#!/usr/bin/env python3.7
#
# Copyright (c) 2019-2020 by University of Campania "Luigi Vanvitelli".
# Developers and maintainers: Salvatore Venticinque, Dario Branco.
# This file is part of GreenCharge
# (see https://www.greencharge2020.eu/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import time
from agents import xmppAdaptor as sche, restAdaptor as sche1, setup as es, manager as sm, \
    dispatcher as di
import aiohttp_cors
from utils.config import Configuration
import logging
import ptvsd

ptvsd.enable_attach(address=('0.0.0.0', 5678))
ptvsd.wait_for_attach()
logging.basicConfig(level=logging.INFO)



#####################################################################
#  This Method configure all the API to be exposed to the scheduler #
#  It depends on adotped protocol for the simulation                #
#####################################################################
def adaptor():
    port = Configuration.parameters['adaptor_port']
    jid = Configuration.parameters['adaptor']
    basejid = Configuration.parameters['userjid']

    protocol_version = Configuration.parameters['protocol']
    simulation_dir = Configuration.parameters['simulation_dir']
    logging.debug("simdir:" + simulation_dir)
    hostname = Configuration.parameters['adaptor_address']
    password = Configuration.parameters['xmpp_password']
    if protocol_version == "2.0":
        logging.info("Starting Adaptor")
        adaptor = sche.Adaptor(basejid + "/" + jid, password)
        # scheduler.web.add_get("/gettime", scheduler.get_time, "message.html")
        # scheduler.web.add_post("/postanswer", scheduler.post_answer, "message2.html")
        sc2 = adaptor.start()
        cors = aiohttp_cors.setup(adaptor.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        })

        route = {
            'method': 'GET',
            'path': '/getmessage',
            'handler': adaptor.exposeGetRestAPI,
            'name': 'test'
        }
        route2 = {
            'method': 'POST',
            'path': '/postanswer',
            'handler': adaptor.exposePostRestAPI,
            'name': 'test2'
        }
        route3 = {
            'method': 'GET',
            'path': '/gettime',
            'handler': adaptor.get_time,
            'name': 'test3'
        }
        cors.add(
            adaptor.web.app.router.add_route(method=route3['method'], path=route3['path'], handler=route3['handler'],
                                               name=route3['name']))
        cors.add(
            adaptor.web.app.router.add_route(method=route['method'], path=route['path'], handler=route['handler'],
                                               name=route['name']))
        cors.add(
            adaptor.web.app.router.add_route(method=route2['method'], path=route2['path'], handler=route2['handler'],
                                               name=route2['name']))

        temp=adaptor.web.start(hostname=hostname, port=port)
        temp2=adaptor.web.is_started()
        sc2.result()
    elif protocol_version == "1.0":
        adaptor = sche1.Adaptor(basejid + "/" + jid, password)
        # scheduler.web.add_get("/gettime", scheduler.get_time, "message.html")
        #scheduler.web.add_post("/postanswer", scheduler.post_answer, "message2.html")
        sc2 = adaptor.start()
        cors = aiohttp_cors.setup(adaptor.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
        })

        route = {
            'method': 'POST',
            'path': '/postanswer',
            'handler': adaptor.exposePostRestAPI,
            'name': 'test2'
        }

        cors.add(
            adaptor.web.app.router.add_route(method=route['method'], path=route['path'], handler=route['handler'],
                                               name=route['name']))
        temp=adaptor.web.start(hostname=hostname, port=port)
        temp.result()
        temp2=adaptor.web.is_started()
        sc2.result()

############################################
#  This Method is used to start dispatcher #
############################################
def start_disp():
    simjid = Configuration.parameters['simulator']
    basejid = Configuration.parameters['userjid']
    password = Configuration.parameters['xmpp_password']
    dispatcher = di.Dispatcher(basejid + "/" + simjid, password)
    future = dispatcher.start()
    future.result()
######################################################
#  This Method is used to start externalSource Agent #
######################################################
def setup_simulation():

    basejid = Configuration.parameters['userjid']
    simulation_dir = Configuration.parameters['current_sim_dir']
    password = Configuration.parameters['xmpp_password']
    external = es.ExternalSourceAgent(basejid + "/externalSource", password, simulation_dir + "/xml/buildingNeighborhood.xml",
                                          simulation_dir + "/xml/buildingLoad.xml")
    logging.debug(simulation_dir + "/xml/buildingNeighborhood.xml")
    external.simulation_setup()
    adaptor()




if __name__ == "__main__":

    Configuration.load()
    logging.info("configuration loaded")
    di.MessageFactory.init_parameters()
    setup_simulation()
    logging.info("simulation runtime built")


    setup_jid = Configuration.parameters['userjid'] + "/setupmodule"
    password =  Configuration.parameters['xmpp_password']
    start_disp()
    setupmodule = sm.SetupModule(setup_jid, password)
    setupmodule.start()


    logging.info("waiting for termination")
    while True:
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            break
