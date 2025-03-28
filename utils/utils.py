import gmsh
import numpy
import warnings; warnings.filterwarnings("ignore")

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

def Rectangle(x,y, w, h, lc=0.1):
    '''
    Funkcia pre vytorenie pravouholnika
    x,y - stred
    w,h - sirka, vyska
    
    p0---------l0------>--p1 
    ^                     |
    |                     |
    l3        (x,y)       l1
    |                     |
    |                     v
    p3--<------l2---------p2
    
    return [p0, p1, p2, p3], [l0, l1, l2, l3], c
    '''
    p0 = gmsh.model.geo.addPoint(x-w/2, y+h/2, 0, lc)
    p1 = gmsh.model.geo.addPoint(x+w/2, y+h/2, 0, lc)
    p2 = gmsh.model.geo.addPoint(x+w/2, y-h/2, 0, lc)
    p3 = gmsh.model.geo.addPoint(x-w/2, y-h/2, 0, lc)
    
    l0 = gmsh.model.geo.addLine(p0,p1)
    l1 = gmsh.model.geo.addLine(p1,p2)
    l2 = gmsh.model.geo.addLine(p2,p3)
    l3 = gmsh.model.geo.addLine(p3,p0)
    
    c = gmsh.model.geo.addCurveLoop([p0, p1, p2, p3])
    
    return ([p0,p1,p2,p3], [l0, l1,l2, l3], c)

def Point(x,y, lc=0.1):
    '''
    Vytvorenie bodu
    '''
    return gmsh.model.geo.addPoint(x, y, 0, lc)
    
def Line(pa, pb):
    '''
    Vytvorenie usecky
    '''
    return gmsh.model.geo.addLine(pa,pb)

