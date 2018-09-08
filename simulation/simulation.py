#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import math
import arrow
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

# helper function for simulation, calculate the distance between two arbitrary
# positions.
def distance(position_a, position_b):
    return math.hypot(
        position_a[0] - position_b[0],
        position_a[1] - position_b[1])

# helper function for visualizing the simulated events positions
def plot_2D_poisson_process(points):
    x = points[:, 0]
    y = points[:, 1]
    plt.scatter(x, y, alpha=0.5)
    plt.show()

# helper function for visualizing the simulated time series
def plot_1D_poisson_process(values):
    xs = np.linspace(0, max(values), 10)
    ys = np.zeros((len(xs),))
    ts = np.zeros((len(values),))
    plt.plot(xs, ys)
    plt.plot(values, ts, 'ro', ms=2)
    plt.show()

# helper function for generating 1D poisson process
def simulate_1D_poisson_process(
    T=3600,   # maximum value (usually it is time) for the point process
    lam=250,  # lambda value for poisson distribution if N is none
    N=None):  # number of point will be generated if N is not none
    '''
    Simulate 1D Poisson Process

    For a homogeneous 1D Poisson process with constant rate lambda, the number
    of events n in a time interval T will follow a Poisson distribution:
        n ~ Poisson(lambda).
    And the arrival times t1, ... ,tn will be i.i.d. uniformly through the
    interval:
        ti ~ Uniform(0, T).
    So a homogeneous Poisson process can be easily simulated by first sampling
    n with Poisson distribution and then sampling t{1:n} uniformly.
    '''
    # sample N if N is not specified (None in default)
    _N = N if N is not None else np.random.poisson(size=1, lam=lam)
    ts = [] if _N == 0 else np.random.uniform(0, T, _N)
    # sort the value in ts ascendingly
    ts = np.sort(ts)
    return ts

# helper function for generating 2D poisson process
def simulate_2D_poisson_process(
    cells_shape=[5, 5],        # shape of the cells organized in a square
    lam=10,                    # lambda value for poisson distribution
    width=100., height=100.,   # size of the square
    leftbottom_coords=[0, 0]): # absolute position of the square
    '''
    Simulate 2D Poisson Process

    A framework to generate two-dimensional Poisson Point Processes. First the
    area being studied (part of space which can be in 1D, 2D, 3D, ..., in our
    case is a 2D shape i.e., square) is divided into cells (gridding). Second,
    for each cell a random number n is drawn from a Poisson distribution with
    density of lambda. Then within each cell n points are uniformly distributed.
    The resulting point pattern is a homogeneous point process.
    '''
    # number of sub-regions (cells)
    n_rows  = cells_shape[0]
    n_cols  = cells_shape[1]
    n_cells = n_rows * n_cols

    # a list of numbers of points in each sub region (cell) (N ~ Poisson(lam))
    Ns = np.random.poisson(size=n_cells, lam=lam)
    # points in each of cells which obey uniform distribution
    cells  = [
        [] if N == 0 else np.random.uniform(0, 1.0, [N, 2]) # return empty list if N is 0
        for N in Ns ]
    # coordinates for the points
    coords = np.zeros((0, 2))
    for j in range(n_rows):
        for i in range(n_cols):
            cell_coords = cells[j*n_cols+i]
            if len(cell_coords): # do nothing if cell is empty
                cell_coords[:, 0] += float(i)
                cell_coords[:, 1] += float(n_rows-1-j)
                coords = np.concatenate([coords, cell_coords], axis=0)
    # scale the square to the specified size
    coords[:, 0] *= (width / float(n_cols))
    coords[:, 1] *= (height / float(n_rows))
    # move the points to the absolute position
    coords[:, 0] += leftbottom_coords[0]
    coords[:, 1] += leftbottom_coords[1]
    return coords

class Event(object):
    '''
    Event Object
    '''

    def __init__(self, id, time, position, subr):
        self.id       = id
        self.time     = time
        self.position = position
        self.subr     = subr
        self.served_time  = -1
        self.waiting_time = 0

    def __str__(self):
        return 'Event [%d]: occrred at %f' % (self.id, self.time)

class Server(object):
    '''
    Server Object
    '''

    def __init__(self, id,
        start_time=0., start_position=[50., 50.],
        speed=50., proc_time=0.1):
        self.id             = id
        self.start_time     = start_time
        self.start_position = start_position
        self.speed          = speed
        self.proc_time      = proc_time
        # history
        self.served_events  = []
        self.idle_times     = []
        # status
        self.cur_time       = start_time
        self.cur_position   = start_position

    def serve_event(self, event):
        # server has to wait until the new event occours.
        # otherwise event has to wait until the server finish the previous jobs.
        if self.cur_time <= event.time:
            self.idle_times.append(event.time - self.cur_time)
            self.cur_time = event.time
        # after (event waiting server / server waiting event)
        # server start to serve current event
        dist        = distance(event.position, self.cur_position)
        travel_time = dist / self.speed
        served_time = self.cur_time + travel_time
        finish_time = served_time + self.proc_time
        self.served_events.append(event.id)
        event.waiting_time = served_time - event.time
        event.served_time  = served_time
        self.cur_time      = finish_time
        self.cur_position  = event.position

    def __str__(self):
        return 'Server [%d]: total idle time %f, number of idles %d' % \
            (self.id, sum(self.idle_times), len(self.idle_times))

class Simulation(object):
    '''
    Simulation
    '''

    def __init__(self, lam=10, T=86400,
        abs_coord=[0, 0], width=180., height=100., cells_shape=[5, 9], # parameters for defining the entire region.
        servers_position=[(50, 50), (130, 50)],                        # start position for each of the servers.
        subregion_polygons=[                                           # polygon for each of the subregion.
            [(0., 0.), (100., 0.), (100., 100.), (0., 100.)],
            [(80., 0.), (180., 0.), (180., 100.), (80., 100.)]]):
        '''
        The entire region should cover all the area of each of the sub-regions.
        The region is defined by a absolute leftbottom point, its width and its
        height. However, a sub-region is defined by a specific polygon.

        Each server takes charge of one specific sub-region according to their
        ids (index of the list), which means first server in the list serve the
        first sub-region, and so on so forth.
        '''
        self.n_subr     = len(subregion_polygons)
        self.subregions = [ Polygon(polygon) for polygon in subregion_polygons ]
        print('[%s] initializing random events ...' % arrow.now())
        # positions for each of the events
        self.positions  = simulate_2D_poisson_process(
            cells_shape=cells_shape, lam=lam,
            width=width, height=height, leftbottom_coords=abs_coord)
        # times for each of the events
        self.times      = simulate_1D_poisson_process(T=T, N=len(self.positions))
        print('[%s] %d events have been created.' % (arrow.now(), len(self.positions)))
        print('[%s] creating events and servers objects ...' % arrow.now())
        # ids for each of the events
        self.event_ids  = [ id for id in range(len(self.positions))]
        # subregions that each of the events belongs to
        self.event_subr = [ self._check_event_subr(position) for position in self.positions ]
        # event objects
        self.events = [
            Event(id, self.times[id], self.positions[id], self.event_subr[id])
            for id in self.event_ids ]
        # server objects
        self.servers    = [
            Server(id, start_position=position)
            for id, position in zip(range(self.n_subr), servers_position) ]

    def start_service(self):
        '''
        Start Service

        Each event in turn will be assigned to corresponding server by a given
        policy. In general, the event tends to look for the nearest idle server
        to complete the job. Once the assignment was established, the server will
        move to the location of the event, and start service, then move the next
        assigned event after the completion of current job, so on so forth.
        '''
        print('[%s] start service simulation ...' % arrow.now())
        for event in self.events:
            if len(event.subr) > 0:
                # check availability of each server in the order of priority,
                # dispatch the available server with the hightest priority.
                available_servers = [
                    self.servers[server_id]
                    for server_id in event.subr
                    if event.time > self.servers[server_id].cur_time ]
                # if there is no available server, then assign the event to the
                # nearest unavailable server.
                if len(available_servers) == 0:
                    available_servers = [
                        self.servers[server_id]
                        for server_id in event.subr ]
                # find the nearest server to the current event.
                dists = [
                    distance(event.position, server.cur_position)
                    for server in available_servers ]
                available_servers[np.argmin(dists)].serve_event(event)
            else:
                # the event is not belong to any sub-region
                # or no server takes charge of this event.
                continue

    def get_avg_waiting_time(self):
        # get average waiting time of events in terms of each server.
        avg_waiting_times = []
        for server in self.servers:
            served_events    = [ self.events[event_id] for event_id in server.served_events ]
            waiting_times    = [ event.waiting_time for event in served_events ]
            avg_waiting_time = np.array(waiting_times).mean()
            avg_waiting_times.append(avg_waiting_time)
        return avg_waiting_times

    def print_service_history(self):
        # print the service history for each of the servers.
        for server in self.servers:
            served_events = [ self.events[event_id] for event_id in server.served_events ]
            print('Server [%d]' % server.id)
            for event in served_events:
                print('Event [%d] in sub-regions %s served at %f, have been waiting for %f.' %\
                      (event.id, event.subr, event.served_time, event.waiting_time))

    def _check_event_subr(self, position):
        # return the sub-region id of each event belongs to.
        subr = [ id
            for id, subregion in zip(range(self.n_subr), self.subregions)
            if subregion.contains(Point(position))]
        return subr



if __name__ == '__main__':


    width       = 180.
    height      = 100.
    cells_shape = [100, 180]
    servers_position   = [(50, 50), (130, 50)]
    subregion_polygons = [
        [(0., 0.), (100., 0.), (100., 100.), (0., 100.)],
        [(80., 0.), (180., 0.), (180., 100.), (80., 100.)]]


    overlap_ratio_list    = []
    avg_waiting_time_list = []
    for overlap_width in np.linspace(0, 99, 100):
        lam = 10
        T   = 1000

        abs_coord   = [0, 0]
        height      = 100.
        width       = 200. - overlap_width
        cells_shape = [5, 5]
        servers_position   = [(50., 50.), (150. - overlap_width, 50.)]
        subregion_polygons = [
            [(0., 0.), (100., 0.), (100., 100.), (0., 100.)],
            [(100. - overlap_width, 0.), (200. - overlap_width, 0.),
             (200. - overlap_width, 100.), (100. - overlap_width, 100.)]]

        sim = Simulation(
            lam=lam, T=T, abs_coord=abs_coord,
            height=height, width=width, cells_shape=cells_shape,
            servers_position=servers_position,
            subregion_polygons=subregion_polygons)
        sim.start_service()
        # sim.print_service_history()
        overlap_ratio    = overlap_width / 100.
        avg_waiting_time = np.mean(sim.get_avg_waiting_time())

        overlap_ratio_list.append(overlap_ratio)
        avg_waiting_time_list.append(avg_waiting_time)

    plt.plot(overlap_ratio_list, avg_waiting_time_list)
    plt.ylabel('average waiting time')
    plt.xlabel('overlap ratio')
    plt.show()

    # plot_1D_poisson_process(sim.times)
