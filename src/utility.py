import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import ghpythonlib as gh


def offset_curves(polycurve, offset_distance, direction = 1):
    offLst =[]
    for plot in polycurve:
        try:
            plot = rs.coercecurve(plot)
            nurb = plot.ToNurbsCurve()
            centroid = rg.AreaMassProperties.Compute(nurb).Centroid
            offseted_crv = rs.OffsetCurve(nurb, centroid, offset_distance * direction, rg.Vector3d.ZAxis)
            offseted_crv = rs.coercecurve(offseted_crv[0]).ToPolyline()
            off_nurb = offseted_crv.ToNurbsCurve()
            intersection_count = rg.Intersect.Intersection.CurveCurve(nurb, off_nurb, offset_distance -1, 0).Count
            #offLst.append(intersection_count)
            if offseted_crv.IsClosedWithinTolerance(0.1) and intersection_count == 0:
                offLst.append(offseted_crv)
        except:
           pass
    return offLst


def define_plot_type(polycurve, building_tiefe):
    offset_1 = building_tiefe * 0.6
    offset_2 = building_tiefe * 1.15
    polycurve_offset_1 = gh.components.ClipperComponents.PolylineOffset([polycurve], offset_1, rg.Plane.WorldXY, 0.1, 2,2 ,0.1)
    polycurve_offset_2 = gh.components.ClipperComponents.PolylineOffset([polycurve], offset_2, rg.Plane.WorldXY, 0.1, 2,2 ,0.1)
    plot_type = 0
    if polycurve_offset_2[1]:
        plot_type = 2
    elif polycurve_offset_1[1]:
        plot_type = 1
    return plot_type


