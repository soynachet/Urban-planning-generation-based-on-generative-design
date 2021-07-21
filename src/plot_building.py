
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import ghpythonlib as gh

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

def offset_polylines_streets_green(iPolLst, iStreetBreite, building_tiefe ):
    offset_lines = []
    offset_normal_list = []
    pedestrian_areas = []
    green_areas = []
    offset_pol_list = []
    pol_list = []
    plot_type_list = []
    plane_list = []
    for pol_Guid in iPolLst:
        plane = rg.Plane(rg.Point3d.Origin, rg.Vector3d(0,0,1))
        offset_curves_01 = rs.ExplodeCurves(pol_Guid)
        point = rs.coerceline(offset_curves_01[0]).PointAt(0)
        pol = rs.coercecurve(pol_Guid)
        offset_pol = gh.components.OffsetCurve(pol, -iStreetBreite, plane,1)
        plane = rg.Plane(point, rg.Vector3d(0,0,1))
        polycurve_offset_test = gh.components.ClipperComponents.PolylineOffset([pol], iStreetBreite, plane, 0.1, 2,2 ,0.1)
        if polycurve_offset_test[1] != None:
            lines = []
            normal_list = []
            offset_curves = rs.ExplodeCurves(polycurve_offset_test[1])
            for curve in offset_curves:
                line = rs.coerceline(curve)
                p0 = line.PointAt(0)
                p1 = line.PointAt(1)
                vec = p0 - p1
                vec.Unitize()
                normal = rg.Vector3d.CrossProduct(vec,rg.Vector3d(0,0,1))
                lines.append(line)
                normal_list.append(normal)
            offset_lines.append(lines)
            offset_normal_list.append(normal_list)
            offset_pol_list.append(offset_pol)
            pol_list.append(pol)
            plot_type_list.append(define_plot_type(offset_pol, building_tiefe))
            plane_list.append(plane)
            ped = rg.Brep.CreateFromLoft([offset_pol,pol], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)
            pedestrian_areas.append(ped[0])
            green = gh.components.BoundarySurfaces(offset_pol)
            green_areas.append(green)
    return [offset_lines, offset_normal_list, pol_list, offset_pol_list, plot_type_list, plane_list, pedestrian_areas, green_areas]
        
def long_line_cut_offset(lineLst, vecLst, building_tiefe):
    lonLine = lineLst[0]
    index = 0
    for i,line in enumerate(lineLst):
        if line.Length >= lonLine.Length:
            lonLine = line
            index = i
    p0 = lonLine.PointAt(0)
    p1 = lonLine.PointAt(1)
    normal = vecLst[index]
    points = (p0, p1)
    lineLst2 = [line for line in lineLst if line != lonLine]
    close_lines = []
    for line in lineLst2:
        for point in points:
            if line.DistanceTo(point,0.1) <= 0.05:
                close_lines.append(line)
    p01 = p0 + normal * building_tiefe
    p11 = p1 + normal * building_tiefe
    lonLine2 = rg.Line(p01, p11)
    intersection_points = []
    for close_line in close_lines:
        value = rg.Intersect.Intersection.LineLine(close_line, lonLine2)
        p = close_line.PointAt(value[1])
        intersection_points.append(p)
    p010 = intersection_points[0] - normal * building_tiefe
    p111 = intersection_points[1] - normal * building_tiefe
    new_points = [p010, p111]
    for i, point in enumerate(new_points):
        if lonLine.DistanceTo(point, True) >= 0.1:
            new_points[i] = lonLine.PointAt(abs(i-0.2))
    lonLine3 = rg.Line(new_points[0], new_points[1])
    return [lonLine3,normal]

def do_brep(point_list, floor_high):
    line_list = []
    for i in range(0, len(point_list)-1):
        line = rg.Line(point_list[i], point_list[i+1]).ToNurbsCurve()
        line_list.append(line)
    surface = rs.AddPlanarSrf(line_list)
    p0 = point_list[0]
    path = rs.AddLine(p0, rg.Point3d(p0.X , p0.Y, p0.Z + floor_high))
    sol_id = rs.ExtrudeSurface(surface, path)
    solid = rs.coercebrep(sol_id)
    return solid

def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield [pool[i] for i in indices]   
    #yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield [pool[i] for i in indices]        
        #yield tuple(pool[i] for i in indices)

def building_solid(line, orientation, normal, building_tiefe, building_tiefe_nord, fluer_breite, floor_high):
    if orientation == "nord":
        tiefe = building_tiefe_nord
    else:
        tiefe = building_tiefe
    p0 = line.PointAt(0)
    p1 = line.PointAt(1)
    p01 = p0 + normal * (tiefe + fluer_breite)
    p11 = p1 + normal * (tiefe + fluer_breite)
    points_polycurve = [p0, p01, p11, p1, p0]
    solid = do_brep(points_polycurve,floor_high)
    return solid

def det_orientation(line):
    p0 = line.PointAt(0)
    p1 = line.PointAt(1)
    vec = p0 - p1
    vec.Unitize()
    if abs(vec.X) > abs(vec.Y):
        return "nord"
    else:
        return "sued"

def line_units(line, units):
    p0 = line.PointAt(0)
    p1 = line.PointAt(1)
    vec = p1- p0
    vec.Unitize()
    points = [p0]
    for unit in units:
        p0 += unit * vec
        points.append(p0)
    #points.append(p1)
    lines = []
    for i in range(0,len(points)-1):
        lin = rg.Line(points[i], points[i+1])
        lines.append(lin)
    return lines

def det_units(line, raster, u_list):
    line_len = line.Length
    n = int(math.ceil(line_len/u_list[0]))
    n2 = int(math.floor(line_len/u_list[0]))
    combinations = combinations_with_replacement(u_list, n)
    combinations2 = combinations_with_replacement(u_list, n2)
    values = []
    for tup in combinations:
        if (line_len - sum(tup)) >= 0:
            values.append([line_len - sum(tup), tup])
    sort_values = sorted(values, key = itemgetter(0))
    values2 = []
    for tup in combinations2:
        if (line_len - sum(tup)) >= 0:
            values2.append([line_len - sum(tup), tup])
    sort_values2 = sorted(values2, key = itemgetter(0))
    if len(sort_values) != 0:
        if sort_values[0][0] < sort_values2[0][0]:
            return sort_values[0][1]
        else:
            return sort_values2[0][1]
    elif len(sort_values2) != 0:
        return sort_values2[0][1]
    else:
        return []

def plot_type_0(line, normal, raster, building_tiefe, building_tiefe_nord, fluer_breite, unit_list, floor_high, path_curve):
    units = det_units(line, raster, unit_list)
    lines = line_units(line, units)
    solids = []
    for lin in lines:
        if not rg.Intersect.Intersection.CurveLine(path_curve, lin, 0.02, 0.01):
            orientation = det_orientation(lin)
            solid = building_solid(lin, orientation, normal, building_tiefe, building_tiefe_nord, fluer_breite,floor_high)
            solids.append(solid)
    return solids

