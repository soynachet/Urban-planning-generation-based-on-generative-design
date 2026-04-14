<<<<<<< HEAD
from utility import *
import utility
utility = reload(utility)


class Cluster:
=======
# -*- coding: utf-8 -*-

from utility import *
import utility

# reload for Grasshopper
try:
    reload
except NameError:
    from importlib import reload

utility = reload(utility)

import csv
import os


class Cluster:

    # ---------------------------------------------------------
    # STATIC STORAGE
    # ---------------------------------------------------------
>>>>>>> e72daf5 (Extend clustering workflow to support internal validity assessment (Table 1))
    plot_areas = []
    plot_perimeters = []
    plot_rotated_bbx_areas = []
    plot_sum_volume_building = []
    plot_roof_areas = []
    plot_roof_heights = []
    plot_dis_building_centroid_to_plot_centroid = []
<<<<<<< HEAD
    plot_dis_building_centroid_to_plot_outline =[]

    def __init__(self, park_pol, park_min_lenght,
                 district_pol, plot_pol, plot_buildings_max_length,
                 plot_buildings_max_area, building_breps, building_brep_min_vol):
=======
    plot_dis_building_centroid_to_plot_outline = []

    # ---------------------------------------------------------
    # INIT
    # ---------------------------------------------------------
    def __init__(self, park_pol, park_min_lenght,
                 district_pol, plot_pol, plot_buildings_max_length,
                 plot_buildings_max_area, building_breps, building_brep_min_vol):

>>>>>>> e72daf5 (Extend clustering workflow to support internal validity assessment (Table 1))
        self.park_pol = park_pol
        self.park_min_lenght = park_min_lenght
        self.district_pol = district_pol
        self.plot_pol = plot_pol
        self.ptml = plot_buildings_max_length
        self.pbma = plot_buildings_max_area
        self.building_breps = building_breps
        self.building_brep_min_vol = building_brep_min_vol

<<<<<<< HEAD
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

=======
    # ---------------------------------------------------------
    # CLEAN GEOMETRY
    # ---------------------------------------------------------
    @property
    def park_polylines_clean(self):
        return park_pol_clean(self.park_pol, self.park_min_lenght)

    @property
    def plot_polylines_clean(self):
        return plot_pol_clean(self.plot_pol, self.ptml, self.pbma)

    @property
    def building_solids_clean(self):
        return building_brep_clean(self.building_breps, self.building_brep_min_vol)

    # ---------------------------------------------------------
    # BASE GEOMETRY DICTIONARY
    # ---------------------------------------------------------
    @property
    def geometry_dictionary(self):
        return create_container_dict(
            self.park_polylines_clean,
            self.district_pol,
            self.plot_polylines_clean,
            self.building_solids_clean
        )

    # ---------------------------------------------------------
    # ORIGINAL STRUCTURE (CLAVE)
    # ---------------------------------------------------------
    def geo_dictionary(self):
        return geometry_lists(
            self.geometry_dictionary,
            self.park_polylines_clean
        )

    # ---------------------------------------------------------
    # FLATTEN
    # ---------------------------------------------------------
    def flatten_dictionary_list(self):
        return geometry_flatten_lists(
            self.geometry_dictionary,
            self.park_polylines_clean
        )

    # ---------------------------------------------------------
    # CLUSTERING / BASELINE
    # ---------------------------------------------------------
    def compute_clustering_values(self, use_clustering=True):

        normalized_values, raw_values, green = normalized_clustering_dict(
            self.geometry_dictionary
        )

        # =========================================================
        # BASELINE MODE (NO CLUSTERING)
        # =========================================================
        if not use_clustering:
            try:
                print("Running BASELINE (no clustering)")

                plots = list(normalized_values.keys())
                if len(plots) == 0:
                    return normalized_values, raw_values, green

                keys = list(normalized_values[plots[0]].keys())

                global_targets = {}
                for k in keys:
                    vals = []
                    for p in plots:
                        if k in normalized_values[p]:
                            vals.append(normalized_values[p][k])

                    if len(vals) > 0:
                        global_targets[k] = sum(vals) / float(len(vals))
                    else:
                        global_targets[k] = 0.0

                # overwrite values
                for p in plots:
                    for k in keys:
                        normalized_values[p][k] = global_targets[k]

            except Exception as e:
                print("Baseline computation failed:", e)

        else:
            print("Running CLUSTER-INFORMED mode")

        # =========================================================
        # SAFE CSV EXPORT
        # =========================================================
        try:
            base_path = os.path.join(os.path.expanduser("~"), "Documents")
            file_path = os.path.join(base_path, "clustering_features_normalized.csv")

            with open(file_path, "w") as f:
                writer = csv.writer(f)

                for plot, values in normalized_values.items():
                    row = [values[k] for k in sorted(values.keys())]
                    writer.writerow(row)

            print("CSV saved at:", file_path)

        except Exception as e:
            print("CSV export failed:", e)

        return normalized_values, raw_values, green
>>>>>>> e72daf5 (Extend clustering workflow to support internal validity assessment (Table 1))
