import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import System
import ghpythonlib.components as ghcomp


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


def coerce_curve(polycurve):
    return rs.coercecurve(polycurve)


def houses_in_plot(polycurve, street_width, building_width, building_high, block_min_dis_factor, block_length_factor, block_line_length_factor):
    polycurve = coerce_curve(polycurve)
    curve = offset_curve(polycurve, block_min_dis_factor * building_width)
    offset_pol = offset_curve(polycurve, street_width)
    try:
        if curve:
            return houses_in_quartier(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
        else:
            return block_in_quartier(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
    except:
        pass


def houses_in_plots(offset_plots, street_width, building_width, building_high, block_min_dis_factor, block_length_factor, block_line_length_factor, rgbs, color):
    buildings = []
    for plot in offset_plots:
        buildings.append(houses_in_plot(plot, street_width, building_width, building_high, block_min_dis_factor, block_length_factor, block_line_length_factor))
    no_none_buildings = remove_nones(buildings)
    no_clash_breps = remove_housing_clashes_dif_plots(no_none_buildings, building_high)
    opt_values = []# plot_opt_lst(offset_plots, no_clash_breps, street_width)
    if color:
        rgb = System.Drawing.Color.FromArgb(rgbs[0]+50,rgbs[1]+50, rgbs[2]+50)
        color_breps = visualize_apartments(no_clash_breps, rgb)
        return color_breps, opt_values
    else:
        return no_clash_breps, opt_values


def green_plots(polycurve, street_width, rgbs, color):
    patchs = []
    non_none_pol = remove_nones(polycurve)
    for guid in non_none_pol:
        curve = rs.coercecurve(guid)
        offset_pol = offset_curve(curve, street_width)
        #patchs.append(offset_pol)
        if offset_pol:
            patch = rg.Extrusion.Create(offset_pol.ToNurbsCurve(), 0.2, True)
            patchs.append(patch)
    if color:
        rgb = System.Drawing.Color.FromArgb(rgbs[0]+10,rgbs[1]+10, rgbs[2]+10)
        return visualize_apartments(patchs, rgb)
    else:
        return patchs


def plot_opt_lst(offset_plots, no_clash_breps, street_width):

    """area = 0
    outline_len = 0
    longest_outline = 0
    vol = 0
    av_vol_centroid_dis = 0"""

    offset_pol = [offset_curve(coerce_curve(plot), street_width) for plot in offset_plots]
    brep_points = [rg.VolumeMassProperties.Compute(brep).Centroid for brep in no_clash_breps]
    relationships = ghcomp.PointInCurve(brep_points, offset_pol)[0]
    plot_values = []
    for plot in offset_pol:
        if plot:
            areaMass = rg.AreaMassProperties.Compute(offset_pol)
            area = areaMass.Area
            outline_len = ghcomp.Length(offset_pol)
            longest_outline = ghcomp.SegmentLengths(offset_pol)[2]
            #centroid = areaMass.Centroid
        else:
            area = 0
            outline_len = 0
            longest_outline = 0

        plot_values.append(area)


    areas = []
    surf_perimeter = []
    surf_longest_segment = []
    centroids = []
    
    for plot in offset_pol:
        if plot:
            areaMass = rg.AreaMassProperties.Compute(offset_pol)
            areas.append(areaMass.Area)
            surf_perimeter.append(ghcomp.Length(offset_pol))
            surf_longest_segment.append(ghcomp.SegmentLengths(offset_pol)[2])
            centroids.append(areaMass.Centroid)
    
    plot_geo_lst = []
    plot_only_geo_list = []
    for s, p, l, c in zip(areas, surf_perimeter, surf_longest_segment, centroids):
        plot_geo_lst.append([s, p, l, c])
        plot_only_geo_list.append([s])        

    for i in range(0, len(relationships)):
        brep = no_clash_breps[i]
        for j in range(0, len(relationships[i])):
            if relationships[i][j] == 2:
                plot_geo_lst[j].append(brep)
                plot_only_geo_list[j].append(brep)


    plot_info_lst = []
    for sublst in plot_geo_lst:
        area = 0
        outline_len = 0
        longest_outline = 0
        vol = 0
        av_vol_centroid_dis = 0
        #try:
        if len(sublst) == 4:
            area = sublst[0]
            outline_len = sublst[1]
            longest_outline = sublst[2]
        if len(sublst) > 4:
            area = sublst[0]
            outline_len = sublst[1]
            longest_outline = sublst[2]
            cen = rs.coerce3dpoint(sublst[3])
            cen_2p = rg.Point2d(cen.X, cen.Y)
            for brep in sublst[4:]:
                brep = rs.coercebrep(brep)
                volume_prop =  rg.VolumeMassProperties.Compute(brep)
                volumen = volume_prop.Volume
                centroid = volume_prop.Centroid
                centroid_2p = rg.Point2d(centroid.X, centroid.Y)
                if volumen:
                    vol += volumen
                if centroid:
                    av_vol_centroid_dis += cen_2p.DistanceTo(centroid_2p)
            av_vol_centroid_dis /= (len(sublst)-4)
    #    except:
    #        pass
        plot_info_lst.append([area, outline_len, longest_outline, vol, av_vol_centroid_dis])

    geometries = []
    data_lst = []
    for i, geo in enumerate(plot_only_geo_list):
        if len(geo) > 1:
            geometries.append(geo)
            data_lst.append(plot_info_lst[i])


    return plot_values



def radians_to_degrees(angle):
    return angle * 180 / math.pi


def degrees_to_radians(angle):
    return angle * math.pi /180


def remove_nones(buildings):
    no_none_buildings = []
    if isinstance(buildings, list):
        if len(buildings) > 0:
            for sublist in buildings:
                if sublist != None:
                    no_none_buildings.append(sublist)
    return no_none_buildings

def brep_from_loft(polycurve1, polycurve2):
    if polycurve1 and polycurve2:
        return rg.Brep.CreateFromLoft([polycurve1.ToNurbsCurve(), polycurve2.ToNurbsCurve()], rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Straight, False)[0]
    else:
        return []


def house_pol(p0, tangent, normal, house_length, building_width):
    p1 = p0 + tangent * house_length
    p2 = p1 + normal * building_width
    p3 = p0 + normal * building_width
    return rg.Polyline([p0,p1,p2,p3,p0]).ToNurbsCurve()


def houses_in_line(line, building_width, block_length_factor, block_line_length_factor):
    scaled_line = scale_curve(line, block_line_length_factor)
    length = scaled_line.Length
    tangent = scaled_line.UnitTangent
    normal = rg.Vector3d.CrossProduct(tangent, rg.Vector3d(0,0,1))
    p0 = scaled_line.PointAt(0)
    houses_nr = int(math.floor(length / (building_width * block_length_factor)))
    house_pols = [length, line]
    if houses_nr > 0:
        house_length = length / houses_nr
        for i in range(0, houses_nr):
            house = house_pol(p0, tangent, normal, house_length, building_width)
            house_pols.append(house)
            p0 += tangent * house_length
    return house_pols


def remove_housing_clashes(houses, building_high):
    houses.sort()
    houses.reverse()
    non_clashing_houses = []
    for i, sublist in enumerate(houses):
        for house_curve in sublist[2:]:
            clashing = False
            for j, sublist2 in enumerate(houses):
                if i != j and i > j:
                    for house_curve2 in sublist2[2:]:
                        if rg.Intersect.Intersection.CurveCurve(house_curve, house_curve2, building_high * 0.4, 0.01).Count > 0:
                            clashing = True
            for k, sublist3 in enumerate(houses):
                if i != k:
                    if rg.Intersect.Intersection.CurveLine(house_curve, sublist3[1], 0, 0).Count > 0:
                        clashing = True
            if clashing == False:
                non_clashing_houses.append(house_curve)
    return non_clashing_houses


def remove_clashing_housing_in_quartier(house_pols, lines):
    non_clashing_houses = []
    if len(house_pols) > 2:
        for house in house_pols[2:]:
            clashing = False
            for line in lines:
                if house_pols[1].PointAt(0.5) != line.PointAt(0.5):
                    if rg.Intersect.Intersection.CurveCurve(house, line.ToNurbsCurve()).Count > 0:
                        clashing = True
            if clashing == False:
                non_clashing_houses.append(house)
    return non_clashing_houses


def remove_housing_clashes_dif_plots(houses, building_high):
    non_clashing_houses = []
    if len(houses) > 0:
        for i, sublist in enumerate(houses):
            if isinstance(sublist, list):
                for house_curve in sublist:
                    clashing = False
                    for j, sublist2 in enumerate(houses):
                        if i != j and i > j:
                            for house_curve2 in sublist2:
                                if rg.Intersect.Intersection.CurveCurve(house_curve, house_curve2, building_high * 0.4, 0.01).Count > 0:
                                    clashing = True
                    if clashing == False:
                        non_clashing_houses.append(house_curve)
            house_solids = extrude_curves(non_clashing_houses, -building_high)        
    return house_solids
 

def houses_in_quartier(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    lines = polycurve.GetSegments()
    houses = []
    for line in lines:
        houses.append(houses_in_line(line, building_width, block_length_factor, block_line_length_factor))
    non_clashing_houses = remove_housing_clashes(houses, building_high)
    return non_clashing_houses
    

def block_in_quartier(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    lines = polycurve.GetSegments()
    lines_length = [line.Length for line in lines]
    ziped_list = zip(lines_length, lines)
    ziped_list.sort()
    ziped_list.reverse()
    line = ziped_list[0][1]
    house_pols = houses_in_line(line, building_width, block_length_factor, block_line_length_factor)
    non_clashing_houses = remove_clashing_housing_in_quartier(house_pols, lines)
    return non_clashing_houses


def scale_curve(curve, curve_length_factor):
    """reduce the extension of the input curve by a porcentage defined by the parameter curve_length"""
    # curve input is actually a line
    len = curve.Length
    p0 = curve.PointAt(0.5)
    vec = curve.UnitTangent
    p1 = p0 - ((vec * len * curve_length_factor) / 2 )
    p2 = p0 + ((vec * len * curve_length_factor) / 2 )
    new_curve = rg.Line(p1, p2)
    return new_curve


def extrude_curves(houses, building_high):
    breps = []
    for house_curve in houses:
        breps.append(rg.Extrusion.Create(house_curve, building_high, True))
    return breps


def create_colors():
    """Assign color to apartment based on tag"""
    colors = {}
    color_slab = System.Drawing.Color.FromArgb(255, 171, 74)
    color_column = System.Drawing.Color.FromArgb(255, 250, 74)
    color_core = System.Drawing.Color.FromArgb(160, 160, 160)
    colors = {'slab' : color_slab, 'column': color_column, 'core' : color_core}
    return colors


def extrusion_to_colored_mesh(ext, color):
    """Convert extrusion object to colored monotone mesh with specific color"""
    bfaces = ext.ToBrep(True).Faces
    msh_lst = []
    for i in range(bfaces.Count):
        f = bfaces[i].DuplicateFace(False)
        msh = rg.Mesh.CreateFromBrep(f, rg.MeshingParameters.Coarse)[0]
        # msh = rc.Geometry.Mesh.CreateFromBrep(f, rc.Geometry.MeshingParameters.Default)[0]
        msh_lst.append(msh)
    meshes = rg.Mesh()
    meshes.Append(msh_lst)
    meshes.VertexColors.CreateMonotoneMesh(color)  # color
    return meshes


def visualize_apartments(breps, color):
    """Visualize apartment extrusion objects with corresponding color"""
    geo = []
    for brep in breps:
        colorMsh = extrusion_to_colored_mesh(brep, color)
        geo.append(colorMsh)  # colored meshes
        geo += brep.GetWireframe()  # wire-frame curves
    return geo


def flatten_lst(lst):
    flat_list = []
    for sublist in lst:
        if isinstance(sublist, list):
            for item in sublist:
                flat_list.append(item)
        else:
            flat_list.append(sublist)
    return flat_list


