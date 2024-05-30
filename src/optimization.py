from utility import *
import utility
utility = reload(utility)


class Optimization:

    def __init__(
        self, clustering_pick_n, clustering_results,
        opt_keys, opt_values, geo_keys, geo_values, weights
    ):

        self.cpn = clustering_pick_n
        self.cr = clustering_results
        self.opt_keys = opt_keys
        self.opt_values = opt_values
        self.geo_keys = geo_keys
        self.geo_values = geo_values
        self.weights = weights

    def optimization_value(self):
        return compute_optimization_value(self.cpn, self.cr, self.opt_keys, 
                self.opt_values, self.geo_keys, self.geo_values, self.weights)