#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

import math
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point

def plot_2D_poisson_process(points):
    x = points[:, 0]
    y = points[:, 1]
    plt.scatter(x, y, alpha=0.5)
    plt.show()

def plot_1D_poisson_process(values):
    xs = np.linspace(0, max(values), 10)
    ys = np.zeros((len(xs),))
    ts = np.zeros((len(values),))
    plt.plot(xs, ys)
    plt.plot(values, ts, 'ro', ms=2)
    plt.show()

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
        self.waiting_time = 0

    def __str__(self):
        return 'Event [%d]: total waiting time %f' % \
            (self.id, self.waiting_time)

class Server(object):
    '''
    Server Object
    '''

    def __init__(self, id,
        start_time=0., start_position=[50., 50.],
        speed=0.5, proc_time=1800.):
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
        if self.cur_time <= event.time:
            self.idle_times.append(event.time - self.cur_time)
            self.cur_time = event.time
        # event has to wait until the server finish the previous jobs.
        else:
            event.waiting_time = self.cur_time - event.time
        # after (event waiting server / server waiting event)
        # server start to serve current event
        distance = math.hypot(
            event.position[0] - self.cur_position[0],
            event.position[1] - self.cur_position[1])
        travel_time = distance / self.speed
        finish_time = self.cur_time + travel_time + self.proc_time
        self.served_events.append(event.id)
        self.cur_time     = finish_time
        self.cur_position = event.position

    def __str__(self):
        return 'Server [%d]: total idle time %f, number of idles %d, served events: %s' % \
            (self.id, sum(self.idle_times), len(self.idle_times), self.served_events)

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
        # positions for each of the events
        self.positions  = simulate_2D_poisson_process(
            cells_shape=cells_shape, lam=lam,
            width=width, height=height, leftbottom_coords=abs_coord)
        # times for each of the events
        self.times      = simulate_1D_poisson_process(T=T, N=len(self.positions))
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
        for id in self.event_ids:
            subr = self.events[id].subr
            if len(subr) == 0:
                continue
            elif len(subr) == 1:
                self.servers[subr[0]].serve_event(self.events[id])
            elif len(subr) == 2:
                self.servers[max(subr)].serve_event(self.events[id])
        # for debugging
        for event in self.events:
            print(event)
        for server in self.servers:
            print(server)

    def _check_event_subr(self, position):
        subr = [ id
            for id, subregion in zip(range(self.n_subr), self.subregions)
            if subregion.contains(Point(position))]
        return subr



if __name__ == '__main__':

    sim = Simulation(lam=2)
    sim.start_service()
    plot_2D_poisson_process(sim.positions)
    plot_1D_poisson_process(sim.times)
