import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import ghpythonlib as gh


def offset_curve(polycurve, offset_distance, direction = 1):
    try:
        nurb = polycurve.ToNurbsCurve()
        centroid = rg.AreaMassProperties.Compute(nurb).Centroid
        offseted_crv = rs.OffsetCurve(nurb, centroid, offset_distance * direction, rg.Vector3d.ZAxis)
        offseted_crv = rs.coercecurve(offseted_crv[0]).ToPolyline()
        off_nurb = offseted_crv.ToNurbsCurve()
        intersection_count = rg.Intersect.Intersection.CurveCurve(nurb, off_nurb, offset_distance -1, 0).Count
        if offseted_crv.IsClosedWithinTolerance(0.1) and intersection_count == 0:
            return offseted_crv
    except:
        pass


def offset_plot(plot_polylines, street_width):
    if isinstance(plot_polylines, list):
        offset_plots = [offset_curve(rs.coercecurve(plot), street_width) for plot in plot_polylines]
    else:
        offset_plots = offset_curve(rs.coercecurve(plot_polylines), street_width)
    return offset_plots


def plot_type(polycurve, building_width, block_factor_min_dis):
    curve = offset_curve(polycurve, block_factor_min_dis * building_width)
    pol_in_plot = offset_curve(polycurve, building_width)
    if curve:
        #return rg.Brep.CreateFromLoft([pol_in_plot.ToNurbsCurve(), polycurve.ToNurbsCurve()], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)[0]
        polycurve.DeleteShortSegments(building_width)
        breps = brep_no_corner(polycurve, building_width)
        return breps
    else:
        pass
        #return polycurve


def radians_to_degrees(angle):
    return angle * 180 / math.pi

def degrees_to_radians(angle):
    return angle * math.pi /180


def brep_from_loft(polycurve1, polycurve2):
    if polycurve1 and polycurve2:
        return rg.Brep.CreateFromLoft([polycurve1.ToNurbsCurve(), polycurve2.ToNurbsCurve()], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)[0]
    else:
        return []

def brep_no_corner(polycurve, building_width):
    lines = polycurve.GetSegments()
    tangents = [line.UnitTangent for line in lines]
    lengths = [line.Length for line in lines]
    angles = []
    for i in range(0, len(lines)):
        if i < len(lines) - 1:
            angles.append(rg.Vector3d.VectorAngle(tangents[i], tangents[i+1]))
        else:
            angles.append(rg.Vector3d.VectorAngle(tangents[i], tangents[-1]))

   	points = [[]]

    for i in range(0, len(lines)):
        if i != len(lines):
            if int(round(radians_to_degrees(angles[i])/3, 0)) == 30:
                if lines[i].PointAt(0) not in points[-1]:
                    points[-1].append(lines[i].PointAt(0))
                if lines[i].PointAt(1) not in points[-1]:
                    points[-1].append(lines[i].PointAt(1))
                if lines[i+1].PointAt(0) not in points[-1]:
                    points[-1].append(lines[i+1].PointAt(0))
                if lines[i+1].PointAt(1) not in points[-1]:
                    points[-1].append(lines[i+1].PointAt(1))
            else:
                points.append([])
                if lines[i].PointAt(0) not in points[-2]:
                    points[-1].append(lines[i].PointAt(0))
                #if lines[i].PointAt(1) not in points[-2]:
                    points[-1].append(lines[i].PointAt(1))
        if i == len(lines):
            if int(round(radians_to_degrees(angles[i])/3, 0)) == 30:
                points = points[:len(points)-1]
                points[0].append(lines[i].PointAt(0))
                points[0].append(lines[i].PointAt(1))
            else:
                points.append([])
                if lines[i].PointAt(0) not in points[-2]:
                    points[-1].append(lines[i].PointAt(0))
                #if lines[i].PointAt(1) not in points[-2]:
                    points[-1].append(lines[i].PointAt(1))                


    polylines = []
    for sublst in points:
        if len(sublst)  > 0:
            pol = rg.Polyline(sublst)
            polylines.append(pol)#.ToNurbsCurve())
    
    breps = []
    for pol in polylines:
        offset_pol = offset_curve(pol, building_width)
        brep = brep_from_loft(pol,offset_pol)
        breps.append(brep)

    return polylines


def flatten_lst(lst):
    flat_list = []
    for sublist in lst:
        if isinstance(sublist, list):
            for item in sublist:
                flat_list.append(item)
        else:
            flat_list.append(sublist)
    return flat_list


