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

"""
Simulator
=======================================
This  module allows for starting, stopping and checking the status of the simulator and eventually of the optimizer
"""

import argparse
import logging
import subprocess


def start_optimizer(optimizer, policy):
    """
    Args:
        optimizer: the optimizer to start (should be supported dummy, eurecat, oslo)
        policy: the optimization policy (Es: cheapest, greenest, earliest)

    Returns:
        None
    """

    if args.optimizer == 'dummy':
        process = subprocess.Popen(['docker', 'exec', 'docker_gcscheduler_1', '/home/scheduler/scheduler', 'start'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout.decode('utf-8'))

def start_simulator(args):
    """It will start the agents based simulator :return:

    Args:
        args:
    """
    pass


def start(args):
    """It starts the first simulator and eventually the optimizer :param args:
    command line arguments :return:

    Args:
        args:
    """
    logging.info("simulator starting")
    start_simulator()
    if args.optimizer is not None:
        start_optimizer(args.optimizer, args.policy)


def stop_simulator():
    """It will stop the simulator component :return:"""
    # docker exec docker_greencharge.simulator_1 /home/gc/bin/starter.sh start
    pass


def stop_optimizer(optimizer):
    """
    Args:
        optimizer:
    """
    logging.info("stopping optimizer")
    if args.optimizer == 'dummy':
        # docker exec docker_gcscheduler_1
        process = subprocess.Popen(['docker', 'exec', 'docker_gcscheduler_1', '/home/scheduler/scheduler', 'stop'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout.decode('utf-8'))
    pass


def stop(args):
    """It stops both the simulator and the optimizer :param args: :return:

    Args:
        args:
    """
    logging.info("stop  simulator")
    if args.optimizer is not None:
        stop_optimizer(args.optimizer)

    stop_simulator()


def status():
    pass


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(description='simulator client')
    parser.add_argument('cmd', metavar='CMD',  choices=['start', 'stop', 'status'],
                        help='the daemon command')
    parser.add_argument('--optimizer', dest='optimizer', choices=['eurecat', 'oslo', 'dummy'], help='start the scheduler')
    parser.add_argument('--policy', dest='policy', choices=['green', 'cheapest', 'earliest'], default='green',
                        help='set the optimization policy')
    args = parser.parse_args()
    if args.cmd == 'start':
        start(args)
    elif args.cmd == 'stop':
        stop(args)
    elif args.cmd == 'status':
        stop(args)
