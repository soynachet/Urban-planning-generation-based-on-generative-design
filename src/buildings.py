import utility
utility = reload(utility)
from utility import *
import Rhino
import Rhino.Geometry as rg

class Buildings:

    def __init__ (self, plot_polylines, building_width, building_high, block_min_dis_factor, block_line_length_factor, block_length_factor):
        self.plot_polylines = plot_polylines
        self.street_width = building_high * 0.4
        self.building_width = building_width
        self.building_high = building_high
        self.block_min_dis_factor = block_min_dis_factor
        self.block_line_length_factor = block_line_length_factor
        self.block_length_factor = block_length_factor

        # lists
        self.offset_plots = offset_plot(self.plot_polylines, self.street_width)
    
    def plots_type(self):
        building_types = []
        for plot in self.offset_plots:
            building_types.append(plot_type(plot, self.building_width, self.building_high, self.block_min_dis_factor, self.block_length_factor, self.block_line_length_factor))
        return building_types


