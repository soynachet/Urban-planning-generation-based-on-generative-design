import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import random
import ghpythonlib as gh
import sys  
import plot_building as pb


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
    volumen = 0
    for lin in lines:
        lin_curve = lin.ToNurbsCurve()
        if iPathCurveBool == True:
            if not rg.Intersect.Intersection.CurveCurve(path_curve, lin_curve, 0, 0):
                orientation = det_orientation(lin)
                solid = building_solid(lin, orientation, normal, building_tiefe, building_tiefe_nord, fluer_breite,floor_high)
                solids.append(solid)
                vol = abs(gh.components.Volume(solid)[0])
                if iBoolDesigner:
                    designer_lines = iCurveDesigner.GetSegments()
                    close_test = [ True for de_line in designer_lines if de_line.DistanceTo(lin.PointAt(0.5), True) <= 5 ]
                    if True in close_test:
                        vol *= (1 + iProzDesigner*2)
        else:
            orientation = det_orientation(lin)
            solid = building_solid(lin, orientation, normal, building_tiefe, building_tiefe_nord, fluer_breite,floor_high)
            solids.append(solid)
            vol = abs(gh.components.Volume(solid)[0])
            if iBoolDesigner:
                designer_lines = iCurveDesigner.GetSegments()
                close_test = [ True for de_line in designer_lines if de_line.DistanceTo(lin.PointAt(0.5), True) <= 5 ]
                if True in close_test:
                    vol *= (1 + iProzDesigner*2)
            volumen += vol
    return [solids, volumen]

def plot_type_0_b(lines, normal, raster, building_tiefe, building_tiefe_nord, fluer_breite, unit_list, floor_high, path_curve, iPathCurveBool, iBoolDesigner, iCurveDesigner, iProzDesigner):
    solids = []
    volumen = 0
    for lin in lines:
        lin_curve = lin.ToNurbsCurve()
        if iPathCurveBool == True:
            if not rg.Intersect.Intersection.CurveCurve(path_curve, lin_curve, 0, 0):
                orientation = det_orientation(lin)
                solid = building_solid(lin, orientation, normal, building_tiefe, building_tiefe_nord, fluer_breite,floor_high)
                solids.append(solid)
                vol = abs(gh.components.Volume(solid)[0])
                if iBoolDesigner:
                    designer_lines = iCurveDesigner.GetSegments()
                    close_test = [True for de_line in designer_lines if de_line.DistanceTo(lin.PointAt(0.5), True) <= 5 ]
                    if True in close_test:
                        vol *= (1 + iProzDesigner*2)
        else:
            orientation = det_orientation(lin)
            solid = building_solid(lin, orientation, normal, building_tiefe, building_tiefe_nord, fluer_breite,floor_high)
            solids.append(solid)
            vol = abs(gh.components.Volume(solid)[0])
            if iBoolDesigner:
                designer_lines = iCurveDesigner.GetSegments()
                close_test = [ True for de_line in designer_lines if de_line.DistanceTo(lin.PointAt(0.5), True) <= 5 ]
                if True in close_test:
                    vol *= (1 + iProzDesigner*2)
            volumen += vol
    return [solids, volumen]
    
def define_plot_type(polycurve, building_tiefe):
    offset_1 = building_tiefe * 0.7
    offset_2 = building_tiefe * 1.5
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


def angle_vector(vector_list):
    angle_list = []
    for i in range(0, len(vector_list)):
        angle = rg.Vector3d.VectorAngle(vector_list[i-1] * -1, vector_list[i])
        angle_list.append((angle * 180)/ math.pi)
    return angle_list

def polyline_raster(offset_lines, raster):
    points_polyline = []
    vec_raster_list = []
    vec_factor = rg.Vector3d(0,0,0)
    raster_value = 0
    raster_list = []
    vector_list = []
    for i,line in enumerate(offset_lines):
        line_length = line.Length
        number_raster = math.floor(line_length / raster)
        if number_raster != 0:
            p0 = line.PointAt(0)
            if i == 0: points_polyline.append(p0)
            p1 = line.PointAt(1)
            vec = p1 - p0
            vec.Unitize()
            vector_list.append(vec)
            p12 = p0 + vec * raster * number_raster
            vec12 = p12 - p1
            vec_factor += vec12
            p3 = p1 + vec_factor
            points_polyline.append(p3)
            raster_list_line = []
            for i in range(0, int(number_raster)):
                 raster_value += 1
                 raster_list_line.append(raster_value)
            raster_list.append(raster_list_line)
    points_polyline.append(points_polyline[0])
    points_polyline.pop(-2)
    polyline = rg.PolylineCurve(points_polyline)
    angle_list = angle_vector(vector_list)
    return (polyline, raster_list, angle_list, points_polyline)
    
def get_corner_numbers(raster_list, angle_list, raster):
    corner_typ_max_lange = 20
    raster_number = int(math.floor(corner_typ_max_lange / raster))
    eck_numbers = []
    raster_loop = []
    raster_loop.extend(raster_list)
    for i, angle in enumerate(angle_list):
        if angle > 85:# and len(raster_loop) > raster_number and len(raster_loop) > raster_number:
            eck_numbers.append([raster_loop[i-1][-(raster_number): ],raster_loop[i][:raster_number]])
            raster_loop[i-1] = raster_loop[i-1][: -(raster_number)]
            raster_loop[i] = raster_loop[i][raster_number:]          
    return eck_numbers

def corner_polygone(line_list, normal_list, raster_list, corner_number_lists):
    line_tupple =[]
    for line, normal_list, raster_sublist in zip(line_list, normal_list, raster_list):
        for corner_sublist in corner_number_lists:
            for num_list in corner_sublist:
                line_tupple.append(num_list)
                if min(num_list) in raster_sublist:
                    min_value = min(num_list)
                    max_value = max(num_list)
                    remap_min_value = ((min_value - min(raster_sublist)) * (1 - 0)) / (max(raster_sublist) - min(raster_sublist))
                    remap_max_value = ((max_value - min(raster_sublist)) * (1 - 0)) / (max(raster_sublist) - min(raster_sublist))
                    p0 = line.PointAt(remap_min_value)
                    p1 = line.PointAt(remap_max_value)
                    corner_line = rg.Line(p0, p1)
                    line_tupple.append(corner_line)
    return line_tupple
                   
                 
def plot_type_1(line_list, normal_list, polyline, plane, raster):
    pol_raster_values = polyline_raster(line_list, raster)
    pol_raster = pol_raster_values[0]
    raster_list = pol_raster_values[1]
    angle_list = pol_raster_values[2]
    corner_number_lists = get_corner_numbers(raster_list, angle_list, raster)
    corner_polygones = corner_polygone(line_list, normal_list, raster_list, corner_number_lists)
    pol_raster_offset = gh.components.ClipperComponents.PolylineOffset([pol_raster], building_tiefe, plane, 0.1, 2,2 ,0.1)
    
    return corner_polygones #[pol_raster, pol_raster_offset[1]]

def angle_between_lines(line1, line2):
    p10 = line1.PointAt(0)
    p11 = line1.PointAt(1)
    vec1 = p11 - p10
    vec1.Unitize()
    p20 = line2.PointAt(0)
    p21 = line2.PointAt(1)
    vec2 = p21 - p20
    vec2.Unitize()
    angle_rad = rg.Vector3d.VectorAngle(vec1* -1, vec2)
    angle = (angle_rad * 180)/ math.pi
    return angle

def do_rectangle(lin, tiefe):
    line = rs.coerceline(lin)
    p1 = line.PointAt(0)
    p2 = line.PointAt(1)
    tangent = p2 - p1
    tangent.Unitize()
    normal = rg.Vector3d.CrossProduct(tangent, rg.Vector3d(0,0,1))
    p1b = p1 + tiefe * normal
    p2b = p2 + tiefe * normal
    polycurve = rg.PolylineCurve([p1, p1b, p2b, p2, p1])
    return polycurve

def do_polygone(sub_crv, tiefe):
    # offset lines
    point_polyline = []
    lines = []
    tiefe = -tiefe
    anzahl_crv = len(sub_crv)
    for i, crv_Id in enumerate(sub_crv):
        line = rs.coerceline(crv_Id)
        length = line.Length
        p1 = line.PointAt(0)
        p2 = line.PointAt(1)
        tangent = p1 - p2
        tangent.Unitize()
        normal = rg.Vector3d.CrossProduct(tangent, rg.Vector3d(0,0,1))
        if i == 0:
            p1_t = p1 + tiefe * normal
            p2_t = p2 + tiefe * normal - length * tangent
            point_polyline.append(p1)

        elif i == len(sub_crv)-1:
            p1_t = p1 + tiefe * normal + length * tangent
            p2_t = p2 + tiefe * normal
            point_polyline.append(p1)
            point_polyline.append(p2)

        else:
            p1_t = p1 + tiefe * normal + length * tangent
            p2_t = p2 + tiefe * normal - length * tangent
            point_polyline.append(p1)
        line_out = rg.Line(p1_t, p2_t)
        
        lines.append(line_out)

    point_polyline_1 = point_polyline
    point_polyline.reverse()
    #Do poliline
    for i in range(0, len(lines)-1):
        p1 = lines[i].PointAt(0)
        p2 = lines[i].PointAt(1)
        intersection = rg.Intersect.Intersection.LineLine(lines[i], lines[i+1])
        p3 = lines[i].PointAt(intersection[1])
        if i == 0:
            point_polyline_1.append(p1)
            point_polyline_1.append(p3)
        else:
            point_polyline_1.append(p3)
    if anzahl_crv != 0:
        point_polyline_1.append(lines[-1].PointAt(1))
        point_polyline_1.append(point_polyline[0])
    
    polyline = rg.PolylineCurve(point_polyline_1)
    return polyline

def do_lines(line_list):
    points = []
    for i in range(len(line_list)-1):
        if i == 0:
            value = rg.Intersect.Intersection.LineLine(line_list[i], line_list[i+1])
            p0 = line_list[i].PointAt(0)
            p1 = line_list[i].PointAt(value[1])
            points.append(p0)
            points.append(p1)
        elif i > 0:
            value = rg.Intersect.Intersection.LineLine(line_list[i], line_list[i+1])
            p1 = line_list[i].PointAt(value[1])
            points.append(p1)
    points.append(line_list[-1].PointAt(1))
    lines = []
    for i in range(len(points)-1):
        lines.append(rg.Line(points[i], points[i+1]))
    return lines
            