from utility import *
import Rhino
import Rhino.Geometry as rg

class Buildings:

    def __init__ (self, plot_polylines, street_width, building_depth):
        self.plot_polylines = plot_polylines
        self.street_width = street_width
        self.building_depth = building_depth

    
    def offset_plot(self):
        return offset_curves(self.plot_polylines, self.street_width)


    def plots_type(self):
        building_types = []
        for plot in self.plot_polylines:
            building_types.append(define_plot_type(plot, self.building_depth))
        return building_types


