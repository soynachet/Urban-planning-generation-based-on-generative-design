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
        return brep_from_loft(pol_in_plot, polycurve) 
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

def houses_in_line(line, building_width):


def brep_no_corner(polycurve, building_width):
    lines = polycurve.GetSegments()

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

def scale_curve(curve, curve_length):
    """reduce the extension of the input curve by a porcentage defined by the parameter curve_length"""
    # curve input is actually a line
    curve_length /= 100
    len = curve.Length
    p0 = curve.PointAt(0.5)
    vec = curve.UnitTangent
    p1 = p0 - ((vec * len * curve_length) / 2 )
    p2 = p0 + ((vec * len * curve_length) / 2 )
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

def create_floorplate(building_outline_pol):
    """generate groundfloor floorplate brep"""
    brep = rg.Extrusion.Create(building_outline_pol.ToNurbsCurve(), 0.3, True) # floorplate 30 cm thickness
    return [brep]

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


