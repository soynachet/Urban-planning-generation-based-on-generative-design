from utility import *
import utility
utility = reload(utility)


class Optimization:

    def __init__(
        self, plot, plot_n_goal, green_n_goal, green_per_area_goal, clustering_pick_n, clustering_results,
        opt_keys, opt_values, geo_keys, geo_values, weights, weights_bool
        ):
        self.plot = plot
        self.plot_n_goal = plot_n_goal
        self.green_n_goal = green_n_goal
        self.green_per_area_goal = green_per_area_goal
        self.cpn = int(clustering_pick_n)
        self.cr = clustering_results
        self.opt_keys = opt_keys
        self.opt_values = opt_values
        self.geo_keys = geo_keys
        self.geo_values = geo_values
        self.weights = weights
        self.weights_bool = weights_bool


    @property
    def normalize_values_dic(self):
        return normalize_opt_geo_values_dic_02(self.cr, self.opt_keys, self.opt_values,
                                        self.geo_keys, self.geo_values)
    
    def optimization_value(self):
        return compute_optimization_value(self.plot, self.plot_n_goal, self.green_n_goal, self.green_per_area_goal,
                                         self.cpn, self.normalize_values_dic, self.weights, self.weights_bool)

    