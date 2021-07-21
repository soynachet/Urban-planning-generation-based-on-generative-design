import ghpythonlib.components as ghcomp
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

class Plot:
    """input_curve [curve] polycurve to be subdivided
    input_subdivisions [int] subidivide a polycurve n-times
    input_params [list] perpendicular or paralell to the longest line (0,1),
    input_directions [list] the porcentaje of the size of the subdivision (0.0-1.0),
    input_splits [list] to define the subplot that will be subdivided further (0,1)"""
    
    def __init__ (self, input_curve, input_subdivisions, input_params, input_directions, input_splits):
        self.input_subdivisions = input_subdivisions
        self.input_curve = input_curve
        self.input_params = input_params[:self.input_subdivisions]
        self.input_directions = input_directions[:self.input_subdivisions]
        self.input_splits = input_splits[:self.input_subdivisions]
    
    def longestCurv(self, lst):
        longest = lst[0]
        for line in lst:
            if line.GetLength() > longest.GetLength():
                longest = line
        return longest
        
    def farPoint(self, pts,lin):
        farP = pts[0]
        for p in pts:
            if lin.DistanceTo(p,True)> lin.DistanceTo(farP, True):
                farP = p
        return farP
        
    def extendLine(self, lin, farP, prozent, direction):
        p1 = lin.PointAt(0)
        p2 = lin.PointAt(1)
        p12 = lin.PointAt(0.5)
        dir = lin.Direction
        if direction == 0:
            normal = rg.Vector3d(p12) - rg.Vector3d(farP)
            p1 = p1 - prozent * normal + 3*dir
            p2 = p2 - prozent * normal - 3*dir
            linb = rg.Line(p1,p2)
        elif direction == 1:
            normal = rg.Vector3d.CrossProduct(dir, rg.Vector3d(0,0,1))
            p1b = p1 + 2*normal + dir * prozent
            p1c = p1 - 2*normal + dir * prozent
            linb = rg.Line(p1b, p1c)
        return linb
    
    def doPolyline(self, lines):
        edges = ghcomp.BrepEdges(lines)[0]
        surf = ghcomp.BoundarySurfaces(edges)
        edges = ghcomp.BrepEdges(surf)[0]
        points = [rg.Curve.PointAt(edge, 0) for edge in edges]
        pol = ghcomp.PolyLine(points, True)
        return pol
        
    def splitPol(self, iCurve, iParam, iDirection):
        lines = ghcomp.Explode(iCurve, True)[0]
        pts = [ ghcomp.DivideCurve(line,1, True)[0][0] for line in lines ]
        lonCurv = self.longestCurv(lines)
        lonlin = rs.coerceline(lonCurv)
        farP = self.farPoint(pts, lonlin)
        longerLin = self.extendLine(lonlin,farP,iParam,iDirection)
        intersection = ghcomp.SurfaceSplit(ghcomp.BoundarySurfaces(lines), longerLin.ToNurbsCurve())
        pol1 = self.doPolyline(intersection[0])
        pol2 = self.doPolyline(intersection[1])
        return[pol1, pol2]
    
    def subdivide_plot(self):
        param = self.input_params.pop(0)
        dir = self.input_directions.pop(0)
        split = self.input_splits.pop(0)
        edges = self.splitPol(self.input_curve, dir, param)
        dic = {1:0, 0:1}
        reEdge = edges[dic[split]]
        if len(self.input_params) >= 2:
            return [reEdge] + Plot(edges[split], self.input_subdivisions, self.input_params, self.input_directions, self.input_splits).subdivide_plot()
        elif len(self.input_params) == 1:
            return edges
        if len(self.input_params) <= 0:
            return []

def average_area_diff(curves, iAv):
    areaTotal = 0
    areas = []
    for ele in curves:
        area = ghcomp.Area(ele)[0]
        areas.append(area)
        areaTotal += area
    avArea = areaTotal / len(curves)
    diff = 0
    for n in areas:
        diff += (avArea - n)**2
    av_diff = abs(avArea-iAv)
    return [diff, av_diff, avArea]