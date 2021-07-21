import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import ghpythonlib as gh


def offset_curve(polycurve, offset_distance, direction = 1):
    #try:
    plot = rs.coercecurve(polycurve)
    nurb = plot.ToNurbsCurve()
    centroid = rg.AreaMassProperties.Compute(nurb).Centroid
    offseted_crv = rs.OffsetCurve(nurb, centroid, offset_distance * direction, rg.Vector3d.ZAxis)
    offseted_crv = rs.coercecurve(offseted_crv[0]).ToPolyline()
    off_nurb = offseted_crv.ToNurbsCurve()
    intersection_count = rg.Intersect.Intersection.CurveCurve(nurb, off_nurb, offset_distance -1, 0).Count
    if offseted_crv.IsClosedWithinTolerance(0.1) and intersection_count == 0:
        return offseted_crv
    # except:
    #     pass


def offset_plot(plot_polylines, street_width):
    if isinstance(plot_polylines, list):
        offset_plots = [offset_curve(plot, street_width) for plot in plot_polylines]
    else:
        offset_plots = offset_curve(plot_polylines, street_width)
    return offset_plots


def plot_type(polycurve, min_building_width, block_factor_min_dis):
    return offset_curve(polycurve, block_factor_min_dis * min_building_width)



