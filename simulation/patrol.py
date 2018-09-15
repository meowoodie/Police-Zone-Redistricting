#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gas Station Refueling example

Covers:

- Resources: Resource
- Resources: Container
- Waiting for other processes

Scenario:
  A gas station has a limited number of gas pumps that share a common
  fuel reservoir. Cars randomly arrive at the gas station, request one
  of the fuel pumps and start refueling from that reservoir.

  A gas station control process observes the gas station's fuel level
  and calls a tank truck for refueling if the station's level drops
  below a threshold.

"""

import math
import simpy
import arrow
import random
import itertools
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

RANDOM_SEED  = 42
POLICE_SPEED = 10.
waiting_times = []

def print_police_stats(police):
    print('--------------------------------------')
    print('%d of %d slots are allocated.' % (police.count, police.capacity))
    print('  Users:', police.users)
    print('  Queued events:', police.queue)
    print('--------------------------------------')

def policing_policy(location, polices):
    '''

    '''
    assigned_polices = [ police
        for police in polices
        if police['region'].contains(Point(location)) ]
    police = assigned_polices[np.argmin([ len(police['resource'].queue) for police in assigned_polices ])]
    return police

def event_generator(env, polices, event_lam, service_lam,
                    region=[(0., 0.), (100., 0.), (100., 100.), (0., 100.)]):
    '''
    Generate new events that occurs at specific arrival rate.
    '''

    for i in itertools.count():
        yield env.timeout(random.expovariate(event_lam))
        # generate the random location within the specified polygon for the event
        region   = np.array(region)
        location = [ random.uniform(region[:, 0].min(), region[:, 0].max()),
                     random.uniform(region[:, 1].min(), region[:, 1].max()) ]
        # strategy of choosing police
        # police   = polices[np.argmin([ len(police.queue) for police in polices ])]
        police = policing_policy(location, polices)
        env.process(event('event %d' % i, env, police, service_lam, location))

def event(name, env, police, lam, location):
    '''
    Event

    An event requests a police to settle the case. An event will be waiting for
    an available police to arrive the scene, and take some time (exponential
    random variable) to settle the case.
    '''

    init_time = env.now
    # print('[%.1f] Event <%s> has been initiated at %s.' % (init_time, name, location))

    with police['resource'].request() as req:
        # wait for access of the police
        # req = AnyOf(env, reqs)
        yield req
        disp_time = env.now
        # print('[%.1f] <%s> has been waited %.1f for police response.' % (disp_time, name, disp_time - init_time))
        waiting_times.append(disp_time - init_time)

        # calculating the distance between police and the event
        # as well as the travel duration
        distance        = np.linalg.norm(np.array(police['location']) - np.array(location))
        travel_duration = distance / POLICE_SPEED
        # wait until the police commute to the location of the event
        yield env.timeout(travel_duration)
        # update police position
        police['location'] = location
        arrv_time = env.now
        # print('[%.1f] (%s) arrived the <%s> scene in %.1f seconds.' % (arrv_time, police['name'], name, arrv_time - disp_time))

        # calculating the service duration
        service_duration = random.expovariate(lam)
        # wait until the police settle the case
        yield env.timeout(service_duration)
        done_time = env.now
        # print('[%.1f] <%s> finished service in %.1f seconds.' % (done_time, name, done_time - arrv_time))

# # Setup and start the simulation
random.seed(RANDOM_SEED)

if __name__ == '__main__':

    abs_coord   = [0, 0]
    height      = 100.
    width       = 100.
    n_epoches   = 1000

    overlap_ratio_list    = np.linspace(0., 99., 100) / width
    avg_waiting_time_list = []
    max_waiting_time_list = []
    for epoch in range(n_epoches):
        print('[%s] Simulation epoch %d' % (arrow.now(), epoch))
        avg_waiting_times = []
        max_waiting_times = []
        for overlap_width in np.linspace(0., 99., 100):

            subr_radius = (width / 2. + overlap_width / 2.) / 2.
            servers_position   = [(subr_radius, 50.), (100. - subr_radius, 50.)]
            subregion_polygons = [
                [(0., 0.), (2 * subr_radius, 0.),
                 (2 * subr_radius, height), (0., height)],
                [(width - 2 * subr_radius, 0.), (width, 0.),
                 (width, height), (width - 2 * subr_radius, height)]]

            # Create environment and start processes
            env = simpy.Environment()
            # Create polices
            police1 = {
                'name':     'police 0',
                'location': servers_position[0],
                'region':   Polygon(subregion_polygons[0]),
                'resource': simpy.Resource(env, capacity=1)
            }
            police2 = {
                'name':     'police 1',
                'location': servers_position[1],
                'region':   Polygon(subregion_polygons[1]),
                'resource': simpy.Resource(env, capacity=1)
            }
            waiting_times = []
            # Create process for generating events iteratively
            env.process(event_generator(env, [ police1, police2 ], event_lam=.3, service_lam=1.))
            # Execute
            env.run(until=100)

            overlap_ratio    = overlap_width / 100.
            avg_waiting_time = np.mean(waiting_times)

            avg_waiting_times.append(avg_waiting_time)
        avg_waiting_time_list.append(avg_waiting_times)
    avg_waiting_time_list = np.array(avg_waiting_time_list).mean(axis=0)

    plt.plot(overlap_ratio_list, avg_waiting_time_list)
    plt.ylabel('average waiting time')
    plt.xlabel('overlap ratio')
    plt.show()
