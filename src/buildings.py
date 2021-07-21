import utility
utility = reload(utility)
from utility import *
import Rhino
import Rhino.Geometry as rg



class Buildings:

    def __init__ (self, plot_polylines, street_width, min_building_width, max_building_width, block_factor_min_dis):
        self.plot_polylines = plot_polylines
        self.street_width = street_width
        self.min_building_width = min_building_width
        self.max_building_width = max_building_width
        self.block_factor_min_dis = block_factor_min_dis

        # lists
        self.offset_plots = offset_plot(self.plot_polylines, self.street_width)
    
    def plots_type(self):
        building_types = []
        for plot in self.offset_plots:
            building_types.append(plot_type(plot, self.min_building_width, self.block_factor_min_dis))
        return building_types


