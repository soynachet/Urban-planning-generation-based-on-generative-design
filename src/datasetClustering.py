from utility import *
import utility
utility = reload(utility)


class Cluster:
    plot_areas = []
    plot_perimeters = []
    plot_rotated_bbx_areas = []
    plot_sum_volume_building = []
    plot_roof_areas = []
    plot_roof_heights = []
    plot_dis_building_centroid_to_plot_centroid = []
    plot_dis_building_centroid_to_plot_outline =[]

    def __init__(self, park_pol, park_min_lenght,
                 district_pol, plot_pol, plot_buildings_max_length,
                 plot_buildings_max_area, building_breps, building_brep_min_vol):
        self.park_pol = park_pol
        self.park_min_lenght = park_min_lenght
        self.district_pol = district_pol
        self.plot_pol = plot_pol
        self.ptml = plot_buildings_max_length
        self.pbma = plot_buildings_max_area
        self.building_breps = building_breps
        self.building_brep_min_vol = building_brep_min_vol

    @property
    def park_polylines_clean(self):
        return park_pol_clean(self.park_pol, self.park_min_lenght)
 
    @property
    def plot_polylines_clean(self):
        return plot_pol_clean(self.plot_pol, self.ptml, self.pbma)
    
    @property
    def building_solids_clean(self):
        return building_brep_clean(self.building_breps, self.building_brep_min_vol)
    
    @property
    def geometry_dictionary(self):
        """Within districts there are plots and within plots there are buildings
        container calculation what it is within what"""
        return create_container_dict(
            self.park_polylines_clean, self.district_pol, self.plot_polylines_clean, self.building_solids_clean)
    
    def flatten_dictionary_list(self):
        """ dict to list for output visualization"""
        return geometry_flatten_lists(self.geometry_dictionary, self.park_polylines_clean)

    def geo_dictionary(self):
        """ dict to list for output visualization"""
        return geometry_lists(self.geometry_dictionary, self.park_polylines_clean)

    def compute_clustering_values(self):
        return normalized_clustering_dict(self.geometry_dictionary)

