from utility import *
import utility
utility = reload(utility)


class Cluster:

    def __init__(self, plot_parks):
        self.plot_parks = plot_parks

    def test(self):
        return plot_parks_reduce(plot_parks)
