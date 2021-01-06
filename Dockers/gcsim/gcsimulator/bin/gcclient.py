#!/usr/bin/env python3.7
"""
simulator
=======================================
This  module allows for starting, stopping and checking the status of the simulator and eventually of the optimizer
"""
import argparse
import logging
import subprocess


def start_optimizer(optimizer, policy):
    """

    :param optimizer: the optimizer to start (should be supported dummy, eurecat, oslo)
    :param policy: the optimization policy (Es: cheapest, greenest, earliest)
    :return:  None
    """
    if args.optimizer == 'dummy':
        process = subprocess.Popen(['docker', 'exec', 'docker_gcscheduler_1', '/home/scheduler/scheduler', 'start'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout.decode('utf-8'))



def start_simulator(args):
    """
    It will start the agents based simulator
    :return:
    """
    pass


def start(args):
    """
    It starts  the first simulator and eventually the optimizer
    :param args: command line arguments
    :return:
    """
    logging.info("simulator starting")
    start_simulator()
    if args.optimizer is not None:
        start_optimizer(args.optimizer, args.policy)


def stop_simulator():
    """
    It will stop the simulator component
    :return:
    """
    # docker exec docker_greencharge.simulator_1 /home/gc/bin/starter.sh &
    pass


def stop_optimizer(optimizer):
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
    """
    It stops both the simulator and the optimizer
    :param args:
    :return:
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
                        help='the basename of csv timeseries to be analyzed')
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

