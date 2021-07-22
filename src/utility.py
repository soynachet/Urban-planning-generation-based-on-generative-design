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


def plot_type(polycurve, building_width, building_high, block_min_dis_factor, block_length_factor, block_line_length_factor):
    curve = offset_curve(polycurve, block_min_dis_factor * building_width)
    pol_in_plot = offset_curve(polycurve, building_width)
    if curve:
        #return brep_from_loft(pol_in_plot, polycurve)
        return houses_in_quartier(polycurve, building_width, building_high, block_length_factor, block_line_length_factor)
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
            #non_clashing_houses.append(sublist2[1])
    return non_clashing_houses

 
def houses_in_quartier(polycurve, building_width, building_high, block_length_factor, block_line_length_factor):
    lines = polycurve.GetSegments()
    houses = []
    for line in lines:
        houses.append(houses_in_line(line, building_width, block_length_factor, block_line_length_factor))
    non_clashing_houses = remove_housing_clashes(houses, building_high)
    house_solids = extrude_curves(non_clashing_houses, -building_high)
    return house_solids
    

def compute_all_possible_combinations(goal, coin_lst):
    """The coin change algorithm
    Given list of coins and amount, find all possible combinations"""
    if goal < 0:
        return []
    if goal == 0:
        return [[]]
    all_changes = []
    for last_used_coin in coin_lst:
        combos = compute_all_possible_combinations(goal - last_used_coin, coin_lst)
        for combo in combos:
            combo.append(last_used_coin)
            all_changes.append(combo)
    return all_changes


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

def variance(data):
    """determine the variance between a list of axis"""
    # Number of observations
    n = len(data)
    # Mean of the data
    mean = sum(data) / n
    # Square deviations
    deviations = [(x - mean) ** 2 for x in data]
    # Variance
    variance = sum(deviations) / (n - 1)
    return variance


def sort_by_variance(lst):
    """sorting out first the axis that has less variance"""
    variance_lst = []
    for sublst in lst:
        variance_lst.append(variance(sublst))
    # pair variance_lst and lst elements
    zipped_lists = zip(variance_lst, lst)
    # sort by first element of each pair
    sorted_zipped_lists = sorted(zipped_lists, reverse=False)
    sorted_list = [element for _, element in sorted_zipped_lists]
    #get the first 10 elements
    short_sorted_list = []
    for i, sublst in enumerate(sorted_list):
        if i < 10:
            short_sorted_list.append(sublst)
    return short_sorted_list

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


