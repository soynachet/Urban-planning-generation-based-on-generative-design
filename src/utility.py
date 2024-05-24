import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math
from operator import itemgetter
from itertools import combinations_with_replacement
import System
import ghpythonlib.components as ghcomp


def offset_curve(polycurve, offset_distance, direction = 1):
    if polycurve:
        nurb = polycurve.ToNurbsCurve()
        centroid = rg.AreaMassProperties.Compute(nurb).Centroid
        offseted_crv = rs.OffsetCurve(nurb, centroid, offset_distance * direction, rg.Vector3d.ZAxis)
        if offseted_crv:
            offseted_crv = rs.coercecurve(offseted_crv[0]).ToPolyline()
            off_nurb = offseted_crv.ToNurbsCurve()
            intersection_count = rg.Intersect.Intersection.CurveCurve(nurb, off_nurb, offset_distance -1, 0).Count
            if offseted_crv.IsClosedWithinTolerance(0.1) and intersection_count == 0:
                return offseted_crv


def offset_plot(plot_polylines, building_high):
    if isinstance(plot_polylines, list):
        offset_plots = [offset_curve(rs.coercecurve(plot), b_high * 0.5) for plot, b_high in zip(plot_polylines, building_high)]
    else:
        offset_plots = offset_curve(rs.coercecurve(plot_polylines), building_high[0] * 0.5)
    return offset_plots


def coerce_curve(polycurve):
    return rs.coercecurve(polycurve)


def houses_in_plots(plot_polylines, building_width, building_high, block_min_dis_factor, block_length_factor, block_line_length_factor, design_pick, rgbs, color):
    buildings = []
    solids = []
    for plot, pick, b_len_factor, b_line_length_factor, b_width, b_high in zip(plot_polylines, design_pick, block_length_factor, block_line_length_factor, building_width, building_high):
        houses = houses_in_plot(plot, b_high * 0.5, b_width, b_high, block_min_dis_factor, b_len_factor, b_line_length_factor, pick)
        if isinstance(houses, list):
            if len(houses) > 0:
                if isinstance(houses[0], rg.NurbsCurve):
                    buildings.append(houses)
                else:
                    solids.append(houses)
    no_none_buildings = remove_nones(buildings)
    no_clash_breps = remove_housing_clashes_dif_plots(no_none_buildings, min(building_high), min(building_width))
    for sublst in solids:
        for solid in sublst:
            no_clash_breps.extend(solid)
    opt_values = plot_opt_lst(plot_polylines, no_clash_breps, min(building_high) * 0.5)
    #opt_values = []
    #means_lst = opt_values
    #means_lst = average_list(opt_values)
    if color:
        rgb = System.Drawing.Color.FromArgb(rgbs[0]+50,rgbs[1]+50, rgbs[2]+50)
        color_breps = visualize_apartments(no_clash_breps, rgb)
        return color_breps, opt_values
    else:
        return no_clash_breps, opt_values


def houses_in_plot(polycurve, street_width, building_width, building_high, block_min_dis_factor, block_length_factor, block_line_length_factor, pick):
    polycurve = coerce_curve(polycurve)
    curve = offset_curve(polycurve, block_min_dis_factor * building_width)
    offset_pol = offset_curve(polycurve, street_width)
    if curve:
        return house_picker(pick, offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
    else:
        return house_picker(pick, offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)


def house_picker(pick, offset_pol, building_width, building_high, block_length_factor, block_line_length_factor):
    if pick == 1:
        return houses_in_quartier(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
    if pick == 2:
        return block_in_quartier(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
    if pick == 3:
        #return block_in_quartier_fat(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
        return family_houses(offset_pol, building_width*2.5, building_high, block_length_factor/3, block_line_length_factor)
    if pick == 4:
        return family_houses(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
    if pick == 5:
        return several_parallel_blocks(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor, 0)
    if pick == 6:
        return several_parallel_blocks(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor, 1)
    if pick == 7:
        return several_parallel_blocks(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor, 2)
    if pick == 8:
        return garden_plot()
    if pick == 0 and offset_curve(offset_pol, 1.5 * building_width):
        return block_houses(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)
    else:
        return houses_in_quartier(offset_pol, building_width, building_high, block_length_factor, block_line_length_factor)

def block_houses(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    if polycurve:
        polycur = polycurve.ToNurbsCurve()
        blok_len = building_width * block_length_factor *1.5
        curve = offset_curve(polycur, building_width)
        curve_check = offset_curve(polycur, 1.5 * building_width)
        if curve_check:
            nr_curve = curve.ToNurbsCurve()
            unset = rg.Point3d.Unset
            brep = rg.Brep.CreateFromLoft([polycur,nr_curve], unset, unset, rg.LoftType.Straight, False)[0]
            curves = nr_curve.DivideByLength(blok_len, True)

            points = [nr_curve.PointAt(c) for c in curves]
            tan_lst = [nr_curve.TangentAt(c) for c in curves]
            normal_lst = [rg.Vector3d.CrossProduct(tan, rg.Vector3d(0,0,1)) for tan in tan_lst]
            spilt_curves = [rg.Line(p1, p1 - n * building_width).ToNurbsCurve() for p1, n in zip(points[1:], normal_lst[1:])]
            edges = brep.Faces[0].Split(spilt_curves, 2).Faces
            faces = [edges.Item[i] for i in range(0, edges.Count)]
            ex_curve = rg.Line(rg.Point3d(0,0,0), rg.Point3d(0,0,building_high)).ToNurbsCurve()
            face_ext = [face.CreateExtrusion(ex_curve, True) for face in faces]
            solids = [rg.Brep.CreateSolid([ext], 1) for ext in face_ext]
            return solids


def family_houses(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    if polycurve:
        # offset plot polycurve
        polycurve = offset_curve(polycurve, 3 * block_length_factor)
        if polycurve:
            lines = polycurve.GetSegments()
            houses = []
            block_length_factor *= 1.1
            building_high *= 0.6
            for line in lines:
                houses.append(houses_in_line(line, building_width, block_length_factor, block_line_length_factor,"even"))
            non_clashing_houses = remove_housing_clashes(houses, building_high)
            return non_clashing_houses

def houses_in_quartier(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    if polycurve:
        lines = polycurve.GetSegments()
        houses = []
        for line in lines:
            houses.append(houses_in_line(line, building_width, block_length_factor, block_line_length_factor))
        non_clashing_houses = remove_housing_clashes(houses, building_high)
        return non_clashing_houses

def block_in_quartier(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    if polycurve:
        lines = polycurve.GetSegments()
        lines_length = [line.Length for line in lines]
        ziped_list = zip(lines_length, lines)
        ziped_list.sort()
        ziped_list.reverse()
        line = ziped_list[1][1]
        block_length_factor *= 1.5
        building_width *= 1.5
        house_pols = houses_in_line(line, building_width, block_length_factor, block_line_length_factor)
        non_clashing_houses = remove_clashing_housing_in_quartier(house_pols, lines)
        return non_clashing_houses

def block_in_quartier_fat(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    if polycurve:
        lines = polycurve.GetSegments()
        lines_length = [line.Length for line in lines]
        ziped_list = zip(lines_length, lines)
        ziped_list.sort()
        ziped_list.reverse()
        line = ziped_list[0][1]
        building_width *= 3
        block_length_factor /= 3
        house_pols = houses_in_line(line, building_width, block_length_factor, block_line_length_factor, "even")
        non_clashing_houses = remove_clashing_housing_in_quartier(house_pols, lines)
        return non_clashing_houses


def garden_plot():
    return None

def several_parallel_blocks(polycurve, building_width, building_high, block_length_factor, block_line_length_factor, polycurve_side):
    if polycurve:
        lines = polycurve.GetSegments()
        lines_length = [line.Length for line in lines]
        ziped_list = zip(lines_length, lines)
        ziped_list.sort()
        ziped_list.reverse()
        line = ziped_list[polycurve_side][1]
        p0 = line.PointAt(0)
        p1 = line.PointAt(1)
        tan = line.UnitTangent
        normal = rg.Vector3d.CrossProduct(rg.Vector3d(0,0,1), tan)
        distance_buildings_1 = 14 *\
            block_line_length_factor * building_high / 10 + building_width
        distance_buildings_2 = 14 * \
            (1+block_line_length_factor) * building_high / 10
        line_2a = rg.Line(p0 + normal * distance_buildings_1, p1 + normal * distance_buildings_1)
        line_2b = rg.Line(p0 - normal * distance_buildings_1,
                          p1 - normal * distance_buildings_1)
        line_3a = rg.Line(line_2a.PointAt(0) + normal * distance_buildings_2, 
                          line_2a.PointAt(1) + normal * distance_buildings_2)
        line_3b = rg.Line(line_2b.PointAt(0) - normal * distance_buildings_2,
                          line_2b.PointAt(1) - normal * distance_buildings_2)
        line_4a = rg.Line(line_3a.PointAt(0) + normal * distance_buildings_1,
                          line_3a.PointAt(1) + normal * distance_buildings_1)
        line_4b = rg.Line(line_3b.PointAt(0) - normal * distance_buildings_1,
                          line_3b.PointAt(1) - normal * distance_buildings_1)
        line_5a = rg.Line(line_4a.PointAt(0) + normal * distance_buildings_2,
                          line_4a.PointAt(1) + normal * distance_buildings_2)
        line_5b = rg.Line(line_4b.PointAt(0) - normal * distance_buildings_2,
                          line_4b.PointAt(1) - normal * distance_buildings_2)
        house_lines = [line, line_2b, line_2a, line_3a, line_3b, line_4a, line_4b, line_5a, line_5b]
        houses = []
        for lin in house_lines:
            house_pols = houses_in_line(lin, building_width, block_length_factor, block_line_length_factor)
            houses.append(house_pols)
        non_clashing_houses = remove_clashing_housing_in_quartier_2(
            houses, lines, polycurve)
        return non_clashing_houses


def houses_in_line(line, building_width, block_length_factor, block_line_length_factor, even = "all"):
    scaled_line = scale_curve(line, block_line_length_factor)
    length = scaled_line.Length
    tangent = scaled_line.UnitTangent
    normal = rg.Vector3d.CrossProduct(tangent, rg.Vector3d(0,0,1))
    p0 = scaled_line.PointAt(0)
    block_length_factor *= 1.2
    houses_nr = int(math.floor(length / (building_width * block_length_factor)))
    house_pols = [length, line]
    if houses_nr > 0:
        house_length = length / houses_nr
        for i in range(0, houses_nr):
            house = house_pol(p0, tangent, normal, house_length, building_width)
            p0 += tangent * house_length
            if even == "all":
                house_pols.append(house)
            elif even == "even":
                if i % 2 == 0:
                    house_pols.append(house)
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
                        if rg.Intersect.Intersection.CurveCurve(house_curve, house_curve2, building_high * 0.9, 0.01).Count > 0:
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
    house_pols = flatten_lst(house_pols)
    if len(house_pols) > 2:
        for house in house_pols[2:]:
            if isinstance(house, rg.Curve):
                clashing = False
                for line in lines:
                    if house_pols[1].PointAt(0.5) != line.PointAt(0.5):
                        if rg.Intersect.Intersection.CurveCurve(house, line.ToNurbsCurve(), 0, 0).Count > 0:
                            clashing = True
                if clashing == False:
                    non_clashing_houses.append(house)
    return non_clashing_houses


def remove_clashing_housing_in_quartier_2(house_pols, lines, polycurve):
    non_clashing_houses = []
    house_pols = flatten_lst(house_pols)
    if len(house_pols) > 2:
        for house in house_pols[2:]:
            if isinstance(house, rg.Curve):
                clashing = False
                for line in lines:
                    if house_pols[1].PointAt(0.5) != line.PointAt(0.5):
                        if rg.Intersect.Intersection.CurveCurve(house, line.ToNurbsCurve(), 0, 0).Count > 0:
                            clashing = True
                if clashing == False:
                    # determine if pol is inside or oustide
                    bbx_pt = house.GetBoundingBox(rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1))).Center
                    point_far_house = bbx_pt + rg.Vector3d(1, 0, 0) * 1000
                    in_out_line = rg.Line(bbx_pt, point_far_house)
                    inter_count = rg.Intersect.Intersection.CurveCurve(
                        polycurve.ToNurbsCurve(), in_out_line.ToNurbsCurve(), 0, 0).Count
                    if inter_count % 2 != 0:
                        non_clashing_houses.append(house)
    return non_clashing_houses




def define_high_houses(non_clashing_houses, building_high, building_width):
    distances = []
    for i, pol_1 in enumerate(non_clashing_houses):
        line_distances = []
        for j, pol_2 in enumerate(non_clashing_houses):
            if i != j:
                points = pol_1.ClosestPoints(pol_2)
                dis = points[1].DistanceTo(points[2])
                line_distances.append(dis)
        line_distances.sort()
        if len(line_distances) > 0:
            distances.append([pol_1, line_distances[0]])
        else:
            distances.append([pol_1, 0.0])
    pol_dis_lst = []
    for sublst in distances:
        if sublst[1] < 0.1 * building_width:
            pol_dis_lst.append([sublst[0], building_high + 2])
        if sublst[1] >= 0.1 * building_width and sublst[1] < 1 * building_width:
            pol_dis_lst.append([sublst[0], building_high - 2])
        elif sublst[1] >= 1 * building_width:
            pol_dis_lst.append([sublst[0], building_high + 4])
    return pol_dis_lst


def remove_housing_clashes_dif_plots(houses, building_high, building_width):
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
    pol_dis_lst = define_high_houses(non_clashing_houses, building_high, building_width)
    house_solids = extrude_curves(pol_dis_lst)        
    return house_solids
 

def green_plots(polycurve, building_high, rgbs, color):
    patchs = []
    non_none_pol = remove_nones(polycurve)
    for guid, b_high in zip(non_none_pol, building_high):
        curve = rs.coercecurve(guid)
        offset_pol = offset_curve(curve, b_high * 0.5)
        #patchs.append(offset_pol)
        if offset_pol:
            patch = rg.Extrusion.Create(offset_pol.ToNurbsCurve(), 0.2, True)
            patchs.append(patch)
    if color:
        rgb = System.Drawing.Color.FromArgb(rgbs[0]+10,rgbs[1]+10, rgbs[2]+10)
        return visualize_apartments(patchs, rgb)
    else:
        return patchs


def point_in_curve(points, pol):
    results = []
    for p in points:
        z_val = pol.PointAt(0).Z
        line = rg.Line(rg.Point3d(p.X, p.Y, z_val), rg.Point3d(0,0,z_val)).ToNurbsCurve()
        count = rg.Intersect.Intersection.CurveCurve(pol.ToNurbsCurve(), line, 0, 0).Count
        if count % 2 != 0 and count != 0:
            results.append(2)
        else:
            results.append(0)
    return results


def perimeter_len(pol):
    per = 0
    lines = pol.GetSegments()
    lenghts = []
    for line in lines:
        len = line.Length
        per += len
        lenghts.append(len)
    lenghts.sort(reverse=True)
    return per, lenghts[0]


def plot_opt_lst(offset_plots, no_clash_breps, street_width):
    try:
        offset_pol = [offset_curve(coerce_curve(plot), street_width) for plot in offset_plots]
        brep_points = [rg.VolumeMassProperties.Compute(brep).Centroid for brep in no_clash_breps if brep]
        relationships = []
        for pol in offset_pol:
            if pol:
                relationships.append(point_in_curve(brep_points, pol))

        areas = []
        surf_perimeter = []
        surf_longest_segment = []
        centroids = []
        
        for plot in offset_pol:
            if plot:
                areaMass = rg.AreaMassProperties.Compute(plot.ToNurbsCurve())
                if areaMass:
                    areas.append(areaMass.Area)
                    per_len = perimeter_len(plot)
                    surf_perimeter.append(per_len[0])
                    surf_longest_segment.append(per_len[1])
                    centroids.append(areaMass.Centroid)
        
        plot_geo_lst = []
        plot_only_geo_list = []
        for a, p, l, c, o in zip(areas, surf_perimeter, surf_longest_segment, centroids, offset_plots):
            plot_geo_lst.append([a, p, l, c, o])
            plot_only_geo_list.append([a])

        for i in range(0, len(relationships)):
            for j in range(0, len(relationships[i])):
                brep = no_clash_breps[j]
                if relationships[i][j] == 2:
                    plot_geo_lst[i].append(brep)
                    plot_only_geo_list[i].append(brep)

        plot_info_lst = []
        for sublst in plot_geo_lst:
            area = 0
            outline_len = 0
            longest_outline = 0
            vol = 0
            av_vol_centroid_dis = 0
            av_vol_centroid_outline_dis = 0
            av_vol = 0
            if len(sublst) == 5:
                area = sublst[0]
                outline_len = sublst[1]
                longest_outline = sublst[2]
            if len(sublst) > 5:
                area = sublst[0]
                outline_len = sublst[1]
                longest_outline = sublst[2]
                cen = rs.coerce3dpoint(sublst[3])
                cen_2p = rg.Point2d(cen.X, cen.Y)
                for brep in sublst[5:]:
                    brep = rs.coercebrep(brep)
                    volume_prop =  rg.VolumeMassProperties.Compute(brep)
                    volumen = volume_prop.Volume
                    centroid = volume_prop.Centroid
                    centroid_2p = rg.Point2d(centroid.X, centroid.Y)
                    if volumen:
                        vol += volumen
                    if centroid:
                        av_vol_centroid_dis += cen_2p.DistanceTo(centroid_2p)
                        out_curve = rs.coercecurve(sublst[4])
                        dis_param = out_curve.ClosestPoint(centroid, 0)
                        p1 = out_curve.PointAt(dis_param[1])
                        av_vol_centroid_outline_dis += p1.DistanceTo(centroid)
                av_vol_centroid_outline_dis /= (len(sublst)-5)        
                av_vol_centroid_outline_dis += 5
                av_vol_centroid_dis /= (len(sublst)-5)
                av_vol = vol / (len(sublst)-5)
            plot_info_lst.append([area, outline_len, longest_outline, vol, av_vol_centroid_dis, av_vol_centroid_outline_dis, av_vol])
    
        return plot_info_lst
    except:
        plot_info_lst = []
        for a in offset_plots:
            plot_info_lst.append([1,1,1,1,1,1,1])
        return plot_info_lst

def mean(lst):
    return sum(lst) / len(lst)
    

def average_list(lst):
    transpose = zip(*lst)
    transpose_average = [mean(sublst) for sublst in transpose]
    return transpose_average


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


def extrude_curves(pol_dis_lst):
    breps = []
    for sublst in pol_dis_lst:
        breps.append(rg.Extrusion.Create(sublst[0], -sublst[1], True))
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
    if not isinstance(ext, rg.Brep):
        bfaces = ext.ToBrep(True).Faces
    else:
        bfaces = ext.Faces
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
        #geo += brep.GetWireframe()  # wire-frame curves
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


def park_pol_clean(park_pol, park_min_lenght):
    bigger_parks = []
    for park in park_pol:
        if park.Length > park_min_lenght:
            bigger_parks.append(park)
    return bigger_parks

def plot_pol_clean(plot_bulidings, ptml, pbma):
    pol_big = []
    for pol in plot_bulidings:
        length = pol.Length
        if length > ptml:
            area_mass = rg.AreaMassProperties.Compute(pol.ToNurbsCurve(), 0.001)
            if area_mass:
                area = area_mass.Area
                if area > pbma:
                    pol_big.append(pol)
    #centroids = [pol.CenterPoint() for pol in pol_big]
    return pol_big

def building_brep_clean(building_breps, building_brep_min_vol):
    buildings = []
    for building in building_breps:
        vol = building.GetVolume()
        if vol > building_brep_min_vol:
            #centroid = building.GetBoundingBox(rg.Plane(rg.Point3d(0, 0, 0), rg.Vector3d(0, 0, 1))).Center
            buildings.append(building)
            #centroids.append(centroid)
    #centroids = [rg.Point3d(c.X, c.Y, 0) for c in centroids]
    return buildings


def compute_center_point(geo):
    if isinstance(geo, rg.Polyline):
        bbx_pt= geo.CenterPoint()
    elif isinstance(geo, rg.Brep):
        bbx_pt = geo.GetBoundingBox(
            rg.Plane(rg.Point3d(0, 0, 0), rg.Vector3d(0, 0, 1))).Center
        bbx_pt = rg.Point3d(bbx_pt.X, bbx_pt.Y, 0)
    return bbx_pt

def is_inside_point_distance_check(crv, point_insider, diagonal):
    is_inside = False
    closest_point = crv.ClosestPoint(point_insider)
    #print closest_point, diagonal
    if closest_point[0] == True:
        curv_pt = crv.PointAt(closest_point[1])
        distance = curv_pt.DistanceTo(point_insider)
        if distance < diagonal:
            is_inside = True
    return is_inside

def is_inside_bool(container_crv, center_point):
    is_inside = False
    point_far = center_point + rg.Vector3d(1, 0, 0) * 1000
    intersect_line = rg.Line(center_point, point_far)
    inter_count = rg.Intersect.Intersection.CurveCurve(
        container_crv, intersect_line.ToNurbsCurve(), 0, 0).Count
    #container_crv = container.ToNurbsCurve()
    if inter_count % 2 != 0:
        is_inside = True
        # if container_crv.Contains(bbx_pt):
        #     is_inside = True
    return is_inside


def create_container_dict(park_pol, district_pol, plot_pol, building_breps):
    # Building withing plots dictionary
    plot_pol_bbx_diagonals = [rg.BoundingBox(
        plot).Diagonal.Length for plot in plot_pol]
    building_breps_center_points = [
        compute_center_point(brep) for brep in building_breps]
    plot_crv = [plot.ToNurbsCurve() for plot in plot_pol]

    plot_building_dict = {}
    for plot, crv, diagonal in zip(plot_pol, plot_crv, plot_pol_bbx_diagonals):
        plot_building_dict[plot] = []
        for building, center_point in zip(building_breps, building_breps_center_points):
            inside_bool_distances = is_inside_point_distance_check(
                crv, center_point, diagonal)
            if inside_bool_distances == True:
                inside_bool = is_inside_bool(crv, center_point)
                if inside_bool == True:
                    plot_building_dict[plot].append(building)
                    #building_breps_02.remove(building)
    plot_building_dict_clean = {i: j for i,
                                j in plot_building_dict.items() if j != []}

    # Plots within districts dictionary
    district_pol_bbx_diagonals = [rg.BoundingBox(
        district).Diagonal.Length for district in district_pol]
    district_crv = [district.ToNurbsCurve() for district in district_pol]
    plot_pol_clean = [
        plot for plot in plot_pol if plot in plot_building_dict_clean]
    plot_pol_center_points = [compute_center_point(
        plot) for plot in plot_pol_clean]

    district_plot_dict = {}
    for district, crv, diagonal in zip(district_pol, district_crv, district_pol_bbx_diagonals):
        district_plot_dict[district] = []
        for plot, center_point in zip(plot_pol_clean, plot_pol_center_points):
            inside_bool_distances = is_inside_point_distance_check(
                crv, center_point, diagonal)
            if inside_bool_distances == True:
                inside_bool = is_inside_bool(crv, center_point)
                if inside_bool == True:
                    district_plot_dict[district].append(plot)
                    # plot_pol_02.remove(plot)
    district_plot_dict_clean = {i: j for i,
                                j in district_plot_dict.items() if j != []}
                                
    return district_plot_dict_clean, plot_building_dict_clean


def geometry_flatten_lists(container_dictionaries):
    """ for testing outputs visualization"""
    dic_1 = container_dictionaries[0]
    dic_2 = container_dictionaries[1]
    geo_flatten_lst = []
    for k, v_lst in dic_1.items():
        k_list = [k]
        for v in v_lst:
            k_list.append(v)
            breps = dic_2[v]
            for brep in breps:
                k_list.append(brep)
        geo_flatten_lst.append(k_list)
    return geo_flatten_lst


def geometry_lists(container_dictionaries, parks):
    dic_1 = container_dictionaries[0]
    dic_2 = container_dictionaries[1]
    # dic_1_extended = {}
    # for k, v_lst in dic_1.items():
    #     dic_1_extended[k] = {}
    #     for v in v_lst:
    #         dic_1_extended[k][v] = dic_2[v]
    return dic_1, dic_2, parks


def clustering_values_compute(container_dictionaries):
    # geometry dictionaries
    district_plot_dict = container_dictionaries[0]
    plot_building_dict = container_dictionaries[1]
    plots_pol = plot_building_dict.keys()

    ### clustering values ###
    # pa = plot_area
    # pp = plot_perimeter
    # prba = plot_rotated_bbx_minimal_area
    # papb = plot_proportion_plot_area_/_plot_rotated_minimal_bbx_area
    # psvb = plot_sum_volume_building
    # pram = plot_roof_areas_mean
    # prhm = plot_roof_heights_mean
    # prav = plot_roof_areas_variance
    # prhv = plot_roof_heights_variance
    # pbn = plot_building_number
    # ccm = plot_dis_building_centroid_to_plot_centroid_mean
    # com = plot_dis_building_centroid_to_plot_outline_mean
    # ccv = plot_dis_building_centroid_to_plot_centroid_variance
    # cov = plot_dis_building_centroid_to_plot_outline_variance

    # fullfill first three lists
    clustering_dic = {}
    for plot in plots_pol:
        clustering_dic[plot] = {"pa": None, "pp": None, "prba": None, "papb": None, "psvb": None,
                                "pram": None, "prhm": None, "prav": None, "prhv": None, 
                                "pbn": None, "ccm": None, "com": None, "ccv": None, "cov": None}
        pa = rg.AreaMassProperties.Compute(plot.ToNurbsCurve(), 0.001).Area
        pp = plot.Length
        clustering_dic[plot]["pa"] = rg.AreaMassProperties.Compute(
            plot.ToNurbsCurve(), 0.001).Area
        clustering_dic[plot]["pp"] = plot.Length
        clustering_dic[plot]["prba"] = min_rotated_bbx_area(plot)
        clustering_dic[plot]["papb"] = min_rotated_bbx_area(plot)

        breps_in_plot = plot_building_dict[plot]
        vol_sum = 0
        height_lst = []
        roof_area_lst = []
        centroid_centroid_lst = []
        centroid_outline_lst = []
        brep_centroids = []
        for brep in breps_in_plot:
            vol = brep.GetVolume()
            vol_sum += vol
            height, roof_area, brep_centroid = brep_face_values(brep)
            height_lst.append(height)
            roof_area_lst.append(roof_area)
            brep_centroids.append(brep_centroid)
        clustering_dic[plot]["psvb"] = vol_sum
        clustering_dic[plot]["pbn"] = len(breps_in_plot)
        clustering_dic[plot]["pram"] = mean(roof_area_lst)
        clustering_dic[plot]["prhm"]= mean(height_lst)
        clustering_dic[plot]["prav"] = variance(roof_area_lst)
        clustering_dic[plot]["prhv"]= variance(height_lst)

        ccm, com, ccv, cov = brep_centroid_values(
            breps_in_plot, plot, brep_centroids)
        clustering_dic[plot]["ccm"] = ccm
        clustering_dic[plot]["com"] = com
        clustering_dic[plot]["ccv"] = ccv
        clustering_dic[plot]["cov"] = cov

    return clustering_dic


def normalized_clustering_dict(container_dictionaries):
    clustering_values = clustering_values_compute(container_dictionaries)
    to_normalize_dic = {}
    for k, v in clustering_values.items():
        for vk, vv in v.items():
            if vk not in to_normalize_dic:
                to_normalize_dic[vk] = []
            else:
                to_normalize_dic[vk].append(vv)
    n_dic = {}
    for k, v in to_normalize_dic.items():
        n_dic[k] = {"base": min(v), "range": max(v) - min(v)}
    # to normalize apply: (x-base)/range
    normalized_clustering_values = {}
    for k, v in clustering_values.items():
        normalized_clustering_values[k] = {}
        for vk, vv in v.items():
            normalized_clustering_values[k][vk] = (vv - n_dic[vk]["base"]) / n_dic[vk]["range"]
    return normalized_clustering_values


def min_rotated_bbx_area(plot):
    bbx_lst = []
    rotation_angles = [0, 10, 20, 30, 40, 50, 60, 70, 80]
    rotation_angles_rad = [math.radians(angle) for angle in rotation_angles]
    area_min_list = []
    bbx = rg.BoundingBox(plot)
    area_lst = []
    for angle in rotation_angles_rad:
        # brep_02 = brep
        plot_02 = plot.ToNurbsCurve()
        plot_rotate = plot_02.Rotate(
            angle, rg.Vector3d(0, 0, 1), bbx.Center)
        bbx_02 = plot_02.GetBoundingBox(True)
        area = bbx_02.Area
        area_lst.append(area)
    return min(area_lst)

def brep_face_values(brep):
    heights = []
    roof_area = None
    centroid_to_centroid = None
    centroid_to_outline = None
    prop_lst = []
    brep_centroids = []
    for f in brep.Faces:
        prop = rg.AreaMassProperties.Compute(f)
        centroid = prop.Centroid
        height = centroid.Z
        heights.append(height)
        prop_lst.append(prop)
        brep_centroids.append(centroid)
    max_height = max(heights)
    brep_centroid = None
    for prop in prop_lst:
        if prop.Centroid.Z == max_height:
            roof_area = prop.Area
            brep_centroid = prop.Centroid
    return max_height, roof_area, brep_centroid

def brep_centroid_values(breps, plot, brep_centroids):
    plot_centroid = plot.CenterPoint()
    brep_centroids_z0 = [rg.Point3d(pt.X, pt.Y, 0) for pt in brep_centroids]
    plot_centroid_z0 = rg.Point3d(plot_centroid.X, plot_centroid.Y, 0)
    plot_crv = plot.ToNurbsCurve()
    centroid_to_centroid_lst = []
    centroid_to_outline_lst = []
    for bc in brep_centroids_z0:
        dis_cc = bc.DistanceTo(plot_centroid_z0)
        centroid_to_centroid_lst.append(dis_cc)

        closest_point = plot_crv.ClosestPoint(bc)
        curv_pt = plot_crv.PointAt(closest_point[1])
        dis_co = curv_pt.DistanceTo(bc)
        centroid_to_outline_lst.append(dis_co)
    ccm = mean(centroid_to_centroid_lst)
    com = mean(centroid_to_outline_lst)
    ccv = variance(centroid_to_centroid_lst)
    cov = variance(centroid_to_outline_lst)
    return ccm, com, ccv, cov

def variance(data):
  n = len(data)
  mean = sum(data) / n
  deviations = [(x - mean) ** 2 for x in data]
  variance = sum(deviations) / n
  return variance


# # normalize values
# def normalize(lst):
#     base = min(lst)
#     range = max(lst) - base
#     normalized = [(x-base)/range for x in lst]
#     return normalized
