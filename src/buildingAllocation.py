import utility
utility = reload(utility)
from utility import *

class Building:

    def __init__ (
        self, plot_polylines, building_width, 
        building_high, street_width, block_min_dis_factor,
        block_line_length_factor, block_length_factor, 
        design_pick, rgbs, color
        ):

        self.plot_polylines = plot_polylines
        self.building_width = building_width
        self.building_high = building_high
        self.street_width = street_width
        self.block_min_dis_factor = block_min_dis_factor
        self.block_line_length_factor = block_line_length_factor
        self.block_length_factor = block_length_factor
        self.design_pick = design_pick
        self.rgbs = rgbs
        self.color = color 

        # lists
        self.offset_plots = offset_plot(self.plot_polylines, self.building_high)
    
    @property
    def houses_in_subplots(self):
        return houses_in_plots(
            self.plot_polylines, 
            self.building_width, self.building_high, self.street_width,
            self.block_min_dis_factor, self.block_length_factor, 
            self.block_line_length_factor,  self.design_pick, self.rgbs, self.color
            )

    def compute_optimization_values(self):
        return clustering_values_geometry_compute(self.houses_in_subplots)
    
