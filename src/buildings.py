import utility
utility = reload(utility)
from utility import *

class Buildings:

    def __init__ (
        self, plot_polylines, building_width, 
        building_high, block_min_dis_factor, 
        block_line_length_factor, block_length_factor, 
        design_pick, rgbs, color
        ):

        self.plot_polylines = plot_polylines
        self.street_width = building_high * 0.5
        self.building_width = building_width
        self.building_high = building_high
        self.block_min_dis_factor = block_min_dis_factor
        self.block_line_length_factor = block_line_length_factor
        self.block_length_factor = block_length_factor
        self.design_pick = design_pick
        self.rgbs = rgbs
        self.color = color 

        # lists
        self.offset_plots = offset_plot(self.plot_polylines, self.street_width)
    
    def plot_houses(self):
        return houses_in_plots(
            self.plot_polylines, self.street_width, 
            self.building_width, self.building_high, 
            self.block_min_dis_factor, self.block_length_factor, 
            self.block_line_length_factor,  self.design_pick, self.rgbs, self.color
            )


    def plots(self):
        return green_plots(self.plot_polylines, self.street_width, self.rgbs, self.color)

