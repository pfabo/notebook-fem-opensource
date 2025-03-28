#!/usr/bin/env python
'''
Objektova verzia 2D kniznice pre gmsh.
Manipulacia so zakladnymi grafickymi entitami.

Ver
210309  - uprava pre lc
210310  - opravy chyb
210311  - premenovanie tried (Shape->Model, Figure->Shape), oprava chyb
250322  - uprava generovania funkcie Plot pre použitie s CM v notebooku,
          Plot nezapisuje do suboru, ale vracia string
250323  - doplneny vyber komponenty z globalnej databazy podla jeho mena 

TODO 
- vytvorenie kopie objektu
- doplnenie objektu Spline, Ellipse
- uprava obluku
- boolean operacie

'''

import gmsh
import copy
from numpy import *

def iName(s):
    '''
    Vrati referenciu na entitu podla jej mena v globalnej databaze
    '''
    keys = Model.items.keys()
    for k in keys:
        if k.name == s:
            return k

def NM(s):
    '''
    Skratena forma iName
    '''
    return iName(s)

            
class Model:
    
    # konverzny slovnik medzi refrenciami na objekty a ich znacenim v gmsh spolu s parametrami
    items = {}                  # item_ref: [item_type, item_id, parameters ...]
    
    # item type
    NONAME          =   0
    POINT           =  10
    LINE            =  20
    POLYLINE        =  21
    ARC             =  30
    RECTANGLE       = 100
    RECTANGLE_ROUND = 101
    RECTANGLE_BEVEL = 102
    CIRCLE          = 120
    POLYGON         = 140
    LOOP            = 900
            
    lc = 0.1                    # default hustota mriezky
    lastResult      = None      # vysledok poslednej operacie - ref. na objekt 
    
    def __init__(self, modelName=''):
        '''
        '''
        gmsh.model.add(modelName)
        
    def deletePoint(self, refPoint):
        '''
        Odstranenie bodu.
        Je mozne odstaranit len samostatny bod.
        Zmaze objekt Point
        TODO - kontrola, ci bod nie je sucastou inej usecky - vypis
        TODO - kontrola typu
        '''
        pass
        
    def deleteLine(self, refLine):
        '''
        Odstranenie usecky.
        Je mozne odstranit len usecku ktora nie je sucastou inej slucky.
        Zmaze objekt Line
        TODO - kontrola, ci usecka nie je sucastou slucky - vypis
        TODO - kontrola typu
        '''
        pass
    
    def deleteLoop(self, refLoop):
        '''
        TODO - kontrola typu
        '''
        pass
        
    #def rotate(refLoop, angle, centre=None):
    #        '''
    #        Roracia utvaru
    #        
    #        angle  - rad, rotation angle
    #        centre - (x,y) - centre of rotation, None - centre of rectange
    #        '''
    #        if centre == None:
    #            centre = (refLoop.x, refLoop.y)
    #        
    #        
    #        lines = []
    #        for i in refLoop.lines:
    #            lines.append( (1, i.l[0]) ) 
    #            
    #        gmsh.model.geo.rotate(lines, centre[0], centre[1], 0, 0, 0, 1, angle)
    #        gmsh.model.geo.synchronize()
    #        # update point coordinates
    #        #xyz = gmsh.model.getValue(0, self.pnw, [])
    
    def splitLine(line, pn, name=''):
            '''
            p - novy bod
            
            1. kontrola, ci je usecka sucastou sluciek
               vytvorenie zoznamu objektov, ktrore slucku vytvaraju
            2. zmazanie sluciek, vyradenie z items{}
            3. rozdelenie usecky
               zmazanie povodnej usecky
               doplnenie bodu
               vytvorenie novych useciek s povodnym smerom
            4. priadenie referencie k povodnej usecke
               update zoznamov useciek v objektoch
               vytvorenie novuch sluciek
               
            vrati novu pridanu usecku
            '''
            
            # kontrola typu line
            # kontrola typu pn
            idx_old = line.l[0]

            
            pp = line.points
            #print(pp[0], pn)
            l1 = Line(pp[0], pn)
            l2 = Line(pn, pp[1], name)

            # zmazanie povodnej usecky v gmsh
            gmsh.model.geo.remove([ (1, line.l[0]) ])
            
            # vyradenie zmazanej usecky z databazy
            for k in Model.items.keys():
                if Model.items[k][0] == Model.LINE:
                    if line in Model.items[k][2]:   # polozka lines
                        del Model.items[k]
                        break

            # update parametrov povodnej usecky 
            line.end = pn
            line.x   = l1.x
            line.y   = l1.y
            line.l   = l1.l
            line.p   = l1.p
            line.points = l1.points
            #print('line =', line)
            '''
            # vyhladanie objektov, v ktorych sa vyskytuje povodna usecka
            for k in Model.items.keys():
                if line in Model.items[k][2]:   # polozka lines
                    # najdena line, k-referencia na objekt
                    #print('obj type ', Model.items[k][0])
                    if idx_old in k.l:
                        idx = k.l.index(idx_old)
                        #print('line idx ', idx)
                        k.l[idx] = l1.l[0]
                        k.l.insert(idx+1, l2.l[0])
                        #k.lines
                        k.lines[idx] = l1
                        k.lines.insert(idx+1, l2)
                        k.updateLoop()
            '''
            return l2
            
        # def joinLines(self, line2)
        #   zmazanie spolocneho bodu dvoch useciek a vytvorenie jednej usecky 
    
    def name(s):
        '''
        vrati item podla mena
        '''
        keys = Model.items.keys()
        for k in keys:
            if k.name == s:
                return k
    
        
    class Shape:
        '''
        Trieda Shape reprezentuje supertriedu pre uzatvorene tvary s orientovanymi hranami.
        Pre tvary su definovane zakladne transformacie.
        '''
        
        def __init__(self): 
                                   # nastavenie default atributov
            self.points = []       # zoznam (py) referencii na body tvaru
            self.lines  = []       # zoznam (py) referencii na linie/obluky tvaru
            self.invert = False    # priznak otocenia smeru pri definicii krivky
            self.x      = 0        # poloha geometrickeho stredu, pouzita pri rotacii
            self.y      = 0        #        a translacii utvaru
            self.name   = ''       # textove oznacenie (TODO - odvodit z mena premennej)
            self.type   = Model.NONAME
            self.shared = False    # priznak zdielania s inym utvarom (pre delete a pod.)  
            
        def add_point(self, x, y, name='', lc=None):
            '''
            Pridanie / vytvorenie noveho bodu.
            Skontroluje existenciu bodu na danej pozicii,
            ak neexistuje, vytvori novy, inak vrati referenciu na existujuci bod a 
            nastavi flag shared
             '''
            keys = Model.items.keys()
            for k in keys:
                if Model.items[k][0] == Model.POINT:
                    if (x,y) == Model.items[k][4]:      # kontrola polohy
                        k.shared = True                 # bod existuje
                        return k                        # referencia na existujuci bod
            return Point(x, y, name, lc)                # referencia na novy bod
            
        def add_line(self, p0, p1, name=''):
            '''
            Pridanie novej usecky
            Skontroluje existenciu usecky, kontrola v oboch smeroch,
            ak neexistuje, vytvori novu, inak vrati referenciu na existujucu.
            nastavi flag shared
            '''
            keys = Model.items.keys()
            for k in keys:
                if Model.items[k][0] == Model.LINE:
                    if [p0, p1] == Model.items[k][1] or [p1,p0] == Model.items[k][1]:   # line existuje
                        k.shared = True                 
                        return k                        # referencia na existujucu usecku, bez zmeny jej vlastnosti
            return Line(p0, p1, name)                   # referencia na novu usecku
            
            
        
        def translate(self, dx, dy):
            '''
            Posun utvaru
            
            dx, dy - translation offset
            '''
            lines = []
            for i in self.lines:
                #print(i.l)
                lines.append( (1, i.l[0]) ) 
                
            gmsh.model.geo.translate(lines, dx, dy, 0)
            gmsh.model.geo.synchronize()
            # TODO - update suradnic bodov
            
        def rotate(self, angle, rot_centre=None):
            '''
            Roracia utvaru
            
            angle  - rad, rotation angle
            centre - (x,y) - centre of rotation, None - centre of rectange
            '''
            centre = (self.x, self.y)
            if rot_centre == None:
                pass
            if isinstance(rot_centre, (tuple)):
                centre = rot_centre
            if isinstance(rot_centre, (Model.Point)):
                centre = (rot_centre.x, rot_centre.y)
            else:
                print('Warning: Neznamy typ pre stred rotacie')
            
            lines = []
            for i in self.lines:
                lines.append( (1, i.l[0]) ) 
                
            gmsh.model.geo.rotate(lines, centre[0], centre[1], 0, 0, 0, 1, angle)
            gmsh.model.geo.synchronize()
            # update point coordinates
            #xyz = gmsh.model.getValue(0, self.pnw, [])
            
        def dilate(self, kx, ky, centre=None):
            '''
            kx,ky - dilatacne parametre
            '''
            if centre == None:
                centre = (self.x, self.y)
            
            lines = []
            for i in self.lines:
                lines.append( (1, i.l[0]) ) 
            
            gmsh.model.geo.dilate(lines, self.x, self.y, 0, kx, ky, 0)
            gmsh.model.geo.synchronize()
            # TODO
            # update suradnic bodov
            
        def create_loop(self, parts):
            '''
            Vytvorenie slucky z nadvezujucich ciar, ktorymi su
            - line
            - polyline
            - arc
            - TODO spline
            Vrati gsmh refrenciu na slucku self.c. 
            Nastavuje pre objek, ktory metodu vyvolal atributy self.lines, self.l, self.c 
            
            Metoda kontroluje 
            - nadveznost spojovacich bodov - koncovy z predch. useku, startovaci z nasledujuceho 
            - uzavretost krivky
            - orientaciu jednotlivych usekov krivky, urcujucim smerom orientacie je smer prveho useku
            '''
            i = 0;                              # pocitadlo cyklu
            n = len(parts)
            for q in parts:                     # inicializacia priznaku otocenia smeru krivky
                q.invert = False                # docasny flag reprezentujuci opacny smer ciary
            
            
            #for i in parts:
            #    print('create loop', i.l)
            
            #return
            #while True:                         # cyklus cez vsetky elementy - TODO for
            for i in range(n-1):
                #print('vyber', i)
                prev_line = parts[i]
                next_line = parts[i+1]
                
                prev_points = parts[i].points
                if parts[i].type == Model.LINE:
                    ps = prev_points[0]
                    pe = prev_points[1]
                elif parts[i].type == Model.POLYLINE:
                    ps = prev_points[0]
                    pe = prev_points[-1]
                elif parts[i].type == Model.ARC:
                    ps = prev_points[0]
                    pe = prev_points[2]
                else:
                    print('Neznamy typ krivky - first')
                    return None
                
                next_points = parts[i+1].points
                if parts[i+1].type == Model.LINE:
                    if next_line.invert == False:
                        ns = next_points[0]
                        ne = next_points[1]
                    else:
                        ne = next_points[0]
                        ns = next_points[1]
                elif parts[i+1].type == Model.POLYLINE:
                    if next_line.invert == False:
                        ns = next_points[0]
                        ne = next_points[-1]
                    else:
                        ne = next_points[0]
                        ns = next_points[-1]
                elif parts[i+1].type == Model.ARC:
                    if next_line.invert == False:
                        ns = next_points[0]
                        ne = next_points[2]
                    else:
                        ne = next_points[0]
                        ns = next_points[2]
                else:
                    print('Neznamy typ krivky - first')
                    return None
                
                #print('ps, ns', ps, ns)
                #print(ps.p, pe.p, '->', ns.p, ne.p)
                # 1. [p.s, p.e] -> [n.s, n.e]    - priama nadveznost
                if pe == ns:
                    prev_line.invert = False
                    next_line.invert = False
                # 2. [p.s, p.e] -> [n.e, n.s]    - invertovany next
                elif pe == ne:
                    prev_line.invert = False
                    next_line.invert = True
                # 3. [p.e, p.s] -> [n.s, n.e]    - invertovany prev
                elif ps == ns:
                    prev_line.invert = True
                    next_line.invert = False
                # 4. [p.e, p.s] -> [n.e, n.s]    - invertovany prev, next
                elif ps == ne:
                    prev_line.invert = True
                    next_line.invert = True
                else:
                    print('Error: Krivky nemaju spolocny bod')
                    return None
                
                #i=i+1
                #if i == (n-1):          # kontrola ukoncenia 
                #    break
            # generovanie zoznamu kriviek slucky
            self.l = []
            self.lines = []
            for q in parts:
                if q.invert == False:
                    for w in q.lines:
                        self.lines.append(w)
                        self.l.append(w.l[0])
                else:
                    inv = q.lines[::-1]
                    for w in inv:
                        self.lines.append(w)
                        self.l.append(-w.l[0])
            #print('lines =', self.l)

            self.c = gmsh.model.geo.addCurveLoop(self.l)
            gmsh.model.geo.synchronize()
            return self.c
            
            
    #-------------------------------------------------------------------
    class Point(Shape):
        '''
        Elementarny bod modelu
        '''
        def __init__(self, x, y, name='', lc=None):
            super().__init__()
            self.x = x
            self.y = y
            self.name = name
            self.type = Model.POINT
            self.lc = Model.lc
            
            if lc != None:
                self.lc = lc
            
            self.p = gmsh.model.geo.addPoint(x, y, 0, self.lc)
            Model.items[self] = [self.type,     # typ 
                                    [self],     # list-points
                                    [],         # list-lines
                                    None,       # loop ref
                                    name]       # name
            self.points = [self]
            self.lines = []
            self.l = []
            self.c = 0
        
        def translate(self, dx, dy):
            '''
            posun bodu
            '''
            gmsh.model.geo.translate([(0, self.p)], dx, dy, 0)
            gmsh.model.geo.synchronize()
            # TODO - update suradnic
        
        def rotate(self, angle, centre=None):
            '''
            rotacia bodu okolo zvolenej osi 
            '''
            if centre == None:
                centre = (0,0)
            gmsh.model.geo.rotate([(0,self.p)], centre[0], centre[1], 0, 0, 0, 1, angle)
            gmsh.model.geo.synchronize()
            # update point coordinates
            #xyz = gmsh.model.getValue(0, self.pnw, [])
            
        def dilate(self, kx, ky):
            pass
        
        # numericke operacie so suradnicami
        def __add__(self, s):
            '''
            Implementacia operatora pre Point() + (x,y)
            '''
            
            if isinstance(s, type(self) ):      # Point()+Point()
                Model.lastResult = Model.Point(self.x + s.x, self.y+s.y)
                return Model.lastResult
             
            if isinstance(s, tuple):            # Point + (x,y)
                Model.lastResult = Model.Point(self.x + s[0], self.y+s[1] ) 
                return Model.lastResult
                
            print('Error: wrong type in Point() +', s)
            print('       use Point() + (x,y) or Point() + Point()')
            return None
            
        def __radd__(self, s):
            '''
            Implementacia operatora pre (x,y) + Point()
            '''
            if isinstance(s, type(self) ):      # Point()+Point()
                Model.lastResult = Model.Point(self.x + s.x, self.y+s.y)
                return Model.lastResult
             
            if isinstance(s, tuple):            # Point + (x,y)
                Model.lastResult = Model.Point(self.x + s[0], self.y+s[1] ) 
                return Model.lastResult
                
            print('Error: wrong type in Point() +', s)
            print('       use Point() + (x,y) or Point() + Point()')
            return None
        
    
    #-------------------------------------------------------------------
    class Line(Shape):
        '''
        Usecka definovana pociatocnym a koncovym bodom.
        '''
        
        def __init__(self, p0, p1, name=''):
            '''
            p0 - referencia na pociatocny bod
            p1 - referencia na koncovy bod
            '''
            super().__init__()
            self.x = (p0.x + p1.x) / 2  
            self.y = (p0.y + p1.y) / 2  
            self.start = self.st = p0
            self.end   = self.en = p1
            self.name = name
            
            self.type = Model.LINE
            
            self.l = [gmsh.model.geo.addLine(p0.p,p1.p)]
            
            self.points = [p0, p1]
            self.lines  = [self]
            self.p = [p0.p, p1.p]
            
            Model.items[self] = [self.type,   # Model.LINE
                                 self.points, # [p0, p1]
                                 self.lines,  # [self]
                                 None,
                                 name]         # self.name

        #
        # def length(self)
        #   vrati dlzku usecky
    
    #-------------------------------------------------------------------
    class CircleArc(Shape):
        '''
        Kruhovy obluk
        '''
        
        def __init__(self, pb, pc, pe, name=''):
            super().__init__()
            self.start  = self.st = pb
            self.end    = self.en = pe
            self.center = self.ct = pc
            self.type = Model.ARC
            self.name = name
            
            self.points = [ pb, pc, pe]
            self.p = [ pb.p, pc.p, pe.p]
            self.l = [gmsh.model.geo.addCircleArc(pb.p, pc.p, pe.p)]
            
            self.lines  = [self]
            Model.items[self] = [self.type,
                                    self.points,
                                    [self], 
                                    None,
                                    self.name]
            
    
    #-------------------------------------------------------------------
    class Rectangle(Shape):
        '''
        Vytvorenie pravouholnika. Pri konstrukcii sa vytvoria body a usecky,
        k prvkom objektu je mozne pristupovat pomocou symbolickych mien.
        
        Zadanim parametrov (x, y, w, h, name, lc)
            x,y - stred obdlznika
            w,h - sirka, vyska
        
        Zadanie dvojicou suradnic ((x1, y1), (x2, y2), name, lc)
            (x1, y1)
            (x2, y2)
            
        Zadanie dvojicou bodov (p1, p2, name, lc)
            p1
            p2
        '''
        
        def __init__(self, *args, **kvargs):
            '''
            '''
            super().__init__()
            
            if 'lc' in kvargs:           # kontrola parametra 'lc'
                self.lc = kvargs['lc']   # lc je v slovniku, s hodnotou aleno None
                if self.lc==None:
                    self.lc = Model.lc   # default hodnota
            else:                        # lc nie je v slovniku 
                self.lc = Model.lc       # default hodnota
                
            if 'name' in kvargs:         # kontrola parametra 'name'
                self.name = kvargs['name']
            else:
                self.name = ''
            
            self.type = Model.RECTANGLE
                
            if isinstance(args[0], (int, float)) and  \
               isinstance(args[1], (int, float)) and  \
               isinstance(args[2], (int, float)) and  \
               isinstance(args[3], (int, float)):
                   
                self.x = x = args[0]           
                self.y = y = args[1]
                self.width  = w = args[2]
                self.height = h = args[3]
                
                if abs(w) == 0:
                    print('Warning: Rectange width = 0')
                if abs(h) == 0:
                    print('Warning: Rectange height = 0')
                    
                self.nw = self.add_point(x-w/2, y+h/2,   'nw', self.lc)  
                self.ne = self.add_point(x+w/2, y+h/2,   'nw', self.lc)  
                self.se = self.add_point(x+w/2, y-h/2,   'se', self.lc)  
                self.sw = self.add_point(x-w/2, y-h/2,   'sw', self.lc) 
                
            elif isinstance(args[0], (tuple)) and  \
                 isinstance(args[1], (tuple)):
                (x1, y1) = args[0]
                (x2, y2) = args[1]
                self.x = x = (x1 + x2) / 2
                self.y = y = (y1 + y2) / 2
                self.w = w = (x2 - x1)
                self.h = h = (y2 - y1) 
                
                if abs(w) == 0:
                    print('Warning: Rectange width = 0')
                if abs(h) == 0:
                    print('Warning: Rectange height = 0')
                    
                self.nw = self.add_point(x-w/2, y+h/2,   'nw', self.lc)  
                self.ne = self.add_point(x+w/2, y+h/2,   'nw', self.lc)  
                self.se = self.add_point(x+w/2, y-h/2,   'se', self.lc)  
                self.sw = self.add_point(x-w/2, y-h/2,   'sw', self.lc) 
                
            elif isinstance(args[0], (Model.Point)) and  \
                 isinstance(args[1], (Model.Point)):
                x1 = args[0].x
                y1 = args[0].y
                x2 = args[1].x
                y2 = args[1].y
                self.x = x = (x1 + x2) / 2
                self.y = y = (y1 + y2) / 2
                self.w = w = (x2 - x1)
                self.h = h = (y2 - y1) 
                
                if abs(w) == 0:
                    print('Warning: Rectange width = 0')
                if abs(h) == 0:
                    print('Warning: Rectange height = 0')
                
                self.nw = self.ca = args[0]; self.ca.name = 'ca' 
                self.se = self.cb = args[1]; self.cb.name = 'cb' 
                #self.sw = Model.Point(x-w/2, y+h/2,   'nw', self.lc)  
                #elf.ne = Model.Point(x+w/2, y-h/2,   'se', self.lc)
                
                self.sw = self.cc = self.add_point(x-w/2, y+h/2, 'cc', self.lc)  
                self.ne = self.cd = self.add_point(x+w/2, y-h/2, 'cd', self.lc)
                    
            else:
                print('Error: chybne parametre konstruktora ')
                print('     ', args)
            

            
            self.points = [self.nw, self.ne, self.se, self.sw]
            self.p = [self.nw.p, self.ne.p, self.se.p, self.sw.p]
            
            #self.n = Model.Line(self.nw, self.ne, 'n')
            #self.e = Model.Line(self.ne, self.se, 'e')
            #self.s = Model.Line(self.se, self.sw, 's')
            #self.w = Model.Line(self.sw, self.nw, 'w')
            
            self.n = self.add_line(self.nw, self.ne, 'n')
            self.e = self.add_line(self.ne, self.se, 'e')
            self.s = self.add_line(self.se, self.sw, 's')
            self.w = self.add_line(self.sw, self.nw, 'w')
            
            self.lines = [self.n, self.e, self.s, self.w]
            self.l = [self.n.l, self.e.l, self.s.l, self.w.l]
    
            self.c = self.create_loop(self.lines)
            Model.items[self] = [self.type,
                                    self.points,
                                    self.lines,
                                    self.c, 
                                    self.name]
            
                                    
        def updateLoop(self):
            '''
            '''
            gmsh.model.geo.remove([ (2, self.c) ])
            self.c, _, _ = self.create_loop(self.lines)
            Model.items[self] = [self.type, 
                                    self.points,
                                    self.lines,
                                    self.c, 
                                    self.name]
            

    #-------------------------------------------------------------------
    class Polyline(Shape):
        '''
        Vytvorenie lomenej ciary alebo uzatvoreneho utvaru zo zadanych bodov
            PolyLine([p1, p2 ... pn], ...)     p1, p2 .. ref na existujuce objekty Point()
        alebo
            PolyLine([p1, (dx1, dy1), ...])    (dx, dy) .. offset noveho bodu voci predchadzajucemu 
                                                prva polozka zoznamu je Point()
                                                
        TODO addPoint, addLine
        '''
        def __init__(self, nodes, closed=False, name=''):
            '''
            points - pole bodov
            closed - False - vytvori len liniu
                     True  - vytvorui uzatvoreny utvar
            TODO - suradnice stredu prepocitat z min/max poloh uzlov
            '''
            super().__init__()
            
            if len(nodes) < 3:
                print('Error: Minimalny pocet uzlov Polyline je 3')
                
            # kontrola zoznamu uzlov
            if isinstance(nodes[0], Model.Point ) is False:
                print('Error: Prvym uzlom zoznamu musi byt Point()')
            
            temp_nodes = [nodes[0]]
            temp_x = nodes[0].x
            temp_y = nodes[0].y
            for q in nodes[1:]:
                if isinstance(q, Model.Point ) is True:
                    temp_nodes.append(q)
                    temp_x = q.x
                    temp_y = q.y
                elif isinstance(q, tuple) is True:
                    temp_x = temp_x + q[0]
                    temp_y = temp_y + q[1]
                    # TODO - kontrola existencie noveho bodu
                    temp_nodes.append(Point(temp_x, temp_y, str(nodes.index(q)) ) )
                else:
                    print('Error: Neznamy typ v zozname Polyline')
                
            nodes = temp_nodes
                
            self.x = (nodes[0].x + nodes[-1].x) / 2  
            self.y = (nodes[0].y + nodes[-1].y) / 2  
            self.start = self.st = nodes[0]
            self.end   = self.en = nodes[-1]
            self.type = Model.POLYLINE
            
            self.points = nodes
            self.c = None
            self.name = name

            # vyber klucov z databazy
            llist = []
            for q in Model.items.keys():
                if Model.items[q][0] == Model.LINE:
                    llist.append(q)
                              
            # vytvorenie useciek zo zadanych bodov
            for i in range(len(nodes)-1): 
                # kontrola existencie usecky medzi bodmi n[i] - n[i+1] v databaze
                line = self.check_line(llist, nodes[i], nodes[i+1])
                # priradenie mena usecke
                if self.name != '': 
                    line.name = self.name + '-' + str(i)
                else:
                    line.name = 'p-' + str(line.l[0])
                self.lines.append(line)
      
            # vygenerovanie koncovej usecky pre uzatvoreny utvar
            if closed==True:
                # kontrola existencie koncovej usecky
                line = self.check_line(llist, nodes[-1], nodes[0]) 
                # priradenie mena koncovej usecke
                if self.name != '': 
                    line.name = self.name + '-' + str(len(nodes)-1)
                else:
                    line.name = 'p-' + str(line.l[0])
                self.lines.append(line)
        
            # vygenerovanie zoznamov bodov a useciek
            self.p = []
            for i in self.points:
                self.p.append(i.p)
                #print('point ',i.p )
                
            self.l = []
            for i in self.lines:
                self.l.append(i.l[0])
                #print('line ',i.l[0], 'body', i.points[0].p, i.points[1].p)
        
            if closed == True:
                self.c = self.create_loop(self.lines)  
                Model.items[self] = [Model.LOOP,
                                        nodes,
                                        self.lines,
                                        self.c, 
                                        self.name]
            
            Model.items[self] = [self.type,
                                        nodes,
                                        self.lines,
                                        None, 
                                        name]
                                        
        def check_line(self, key_list, na, nb):
            '''
            Konntrola existencie usecky v databaze - zdielanie susednej usecky
            '''
            line_exist = None
            for q in key_list:
                # usecka na -> nb
                if   [na, nb] == Model.items[q][1]:
                    line_exist = q
                # usecka nb -> na
                elif [nb, na] == Model.items[q][1]:
                    line_exist = q
            #vytvorenie alebo priradenie existujucej usecky
            if line_exist == None:
                return Model.Line(na, nb,  str(len(self.points)) )
            else:
                return line_exist
            
            
    #-------------------------------------------------------------------
    class Circle(Shape):
        
        def __init__(self, x, y, r, name='', segments=4, lc=None):
            '''
            r - polomer
            segnents - pocet deleni kruznice
            
            TODO addPoint
            '''
            super().__init__()
            self.x = x          # interne suradnice stredu
            self.y = y
            self.radius = self.r = r
            self.name = name
            self.type = Model.CIRCLE
            self.lc = Model.lc
            if lc != None:
                self.lc = lc
            
            if segments == 4:
                self.cn = Model.Point(x, y, 'cn')
                self.e = Model.Point(x+r, y, 'e', self.lc)  
                self.n = Model.Point(x, y+r, 'n', self.lc)  
                self.w = Model.Point(x-r, y, 'w', self.lc)  
                self.s = Model.Point(x, y-r, 's', self.lc)  
                self.points = [self.cn, self.e, self.n, self.w, self.s]
                self.p = [self.cn.p, self.e.p, self.n.p, self.w.p, self.s.p]
                
                self.ne = Model.CircleArc(self.e, self.cn, self.n, 'ne')
                self.nw = Model.CircleArc(self.n, self.cn, self.w, 'nw')
                self.sw = Model.CircleArc(self.w, self.cn, self.s, 'sw')
                self.se = Model.CircleArc(self.s, self.cn, self.e, 'se')
                self.lines = [self.ne, self.nw, self.sw, self.se]
                self.l = [self.ne.l, self.nw.l, self.sw.l, self.se.l]
                
                self.create_loop(self.lines)
                Model.items[self] = [self.type, self.points, self.lines, self.c, name]
        
        
    #-------------------------------------------------------------------
    class RectangleRound(Shape):
        '''
        Obdlznik so zagulatenymi hranami definovany stredom, sirkou a vyskou.
        
        TODO addPoint
        '''
        
        def __init__(self, x, y, w, h, r, name='', lc=None):
            '''
            x,y - stred obdlznika
            w,h - sirka, vyska
            '''
            super().__init__()
            self.x = x           # interne suradnice stredu
            self.y = y
            self.width  = w
            self.height = h
            self.radius = r
            self.name = name
            self.type = Model.RECTANGLE_ROUND
            self.lc = Model.lc
            if lc != None:
                self.lc = lc
            
            # body v radiusoch
            self.p1 = Model.Point(x-w/2+r, y+h/2-r, 'c1')   # nw
            self.p2 = Model.Point(x+w/2-r, y+h/2-r, 'c2')   # ne
            self.p3 = Model.Point(x+w/2-r, y-h/2+r, 'c3')   # se
            self.p4 = Model.Point(x-w/2+r, y-h/2+r, 'c4')   # sw
            self.points = [self.p1, self.p2, self.p3, self.p4]
            self.p = [self.p1.p, self.p2.p, self.p3.p, self.p4.p]
            
            # body po obvode
            self.nnw = Model.Point(x-w/2+r, y+h/2  , 'nnw', self.lc)   
            self.nne = Model.Point(x+w/2-r, y+h/2  , 'nne', self.lc)  
            self.een = Model.Point(x+w/2  , y+h/2-r, 'een', self.lc)
            self.ees = Model.Point(x+w/2  , y-h/2+r, 'ees', self.lc)
            self.sse = Model.Point(x+w/2-r, y-h/2  , 'sse', self.lc)   
            self.ssw = Model.Point(x-w/2+r, y-h/2  , 'ssw', self.lc)
            self.wss = Model.Point(x-w/2 ,  y-h/2+r, 'wss', self.lc)
            self.wnn = Model.Point(x-w/2 ,  y+h/2-r, 'wnn', self.lc)
            self.points = self.points + [self.nnw, self.nne, self.een, self.ees, self.sse, self.ssw, self.wss, self.wnn]
            self.p = self.p + [self.nnw.p, self.nne.p, self.een.p, self.ees.p, self.sse.p, self.ssw.p, self.wss.p, self.wnn.p]
            
            # obrys
            self.n = Model.Line(self.nnw, self.nne, 'n')
            self.ne = Model.CircleArc(self.nne, self.p2, self.een, 'ne')
            self.e = Model.Line(self.een, self.ees, 'e')
            self.se = Model.CircleArc(self.ees, self.p3, self.sse, 'se')
            self.s = Model.Line(self.sse, self.ssw, 's')
            self.sw = Model.CircleArc(self.ssw, self.p4, self.wss, 'sw')
            self.w = Model.Line(self.wss, self.wnn, 'w')
            self.nw = Model.CircleArc(self.wnn, self.p1, self.nnw, 'nw')
            self.lines = [self.n, self.ne, self.e, self.se, self.s, self.sw, self.w, self.nw]
            self.l = [self.n.l, self.ne.l, self.e.l, self.se.l, self.s.l, self.sw.l, self.w.l, self.nw.l]
            
            self.c = self.create_loop(self.lines)
            Model.items[self] = [self.type, self.points, self.lines, self.c, self.name]
                                    
        def updateLoop(self, name=''):
            '''
            '''
            self.name = name
            gmsh.model.geo.remove([ (2, self.c) ])
            self.create_loop(self.lines)
            Model.items[self] = [self.type, self.points, self.lines, self.c, self.name]
            
 
    #-------------------------------------------------------------------
    class RectangleBevel(Shape):
        '''
        Obdlznik so skosenymi hranami definovany stredom, sirkou a vyskou.
        '''
        
        def __init__(self, x, y, w, h, r, name='', lc=None):
            '''
            x,y - stred obdlznika
            w,h - sirka, vyska
            r   - dlzka skosenia
            '''
            super().__init__()
            self.x = x           # interne suradnice stredu
            self.y = y
            self.width  = w
            self.height = h
            self.radius = r
            self.name = name
            self.type = Model.RECTANGLE_BEVEL
            self.lc = Model.lc
            if lc != None:
                self.lc = lc
            
            # body po obvode
            self.nnw = Model.Point(x-w/2+r, y+h/2  , 'nnw', self.lc)   
            self.nne = Model.Point(x+w/2-r, y+h/2  , 'nne', self.lc)   
            self.een = Model.Point(x+w/2  , y+h/2-r, 'een', self.lc) 
            self.ees = Model.Point(x+w/2  , y-h/2+r, 'ees', self.lc) 
            self.sse = Model.Point(x+w/2-r, y-h/2  , 'sse', self.lc)   
            self.ssw = Model.Point(x-w/2+r, y-h/2  , 'ssw', self.lc)
            self.wss = Model.Point(x-w/2 ,  y-h/2+r, 'wss', self.lc)
            self.wnn = Model.Point(x-w/2 ,  y+h/2-r, 'wnn', self.lc)
            self.points = [self.nnw, self.nne, self.een, self.ees, self.sse, self.ssw, self.wss, self.wnn]
            self.p = [self.nnw.p, self.nne.p, self.een.p, self.ees.p, self.sse.p, self.ssw.p, self.wss.p, self.wnn.p]
            
            # obrys
            self.n  = Model.Line(self.nnw, self.nne, 'n')
            self.ne = Model.Line(self.nne, self.een, 'ne')
            self.e  = Model.Line(self.een, self.ees, 'e')
            self.se = Model.Line(self.ees, self.sse, 'se')
            self.s  = Model.Line(self.sse, self.ssw, 's')
            self.sw = Model.Line(self.ssw, self.wss, 'sw')
            self.w  = Model.Line(self.wss, self.wnn, 'w')
            self.nw = Model.Line(self.wnn, self.nnw, 'nw')
            self.lines = [self.n, self.ne, self.e, self.se, self.s, self.sw, self.w, self.nw]
            self.l = [self.n.l, self.ne.l, self.e.l, self.se.l, self.s.l, self.sw.l, self.w.l, self.nw.l]
            
            self.c = self.create_loop(self.lines)
            Model.items[self] = [self.type, self.points, self.lines, self.c, self.name]
            
    class Loop(Shape):
        '''
        Vytvorenie slucky zo zoznamu useciek (TODO - nemusia byt v poradi)
        alebo zo zoznamu utvarov  
        '''
        
        def __init__(self, items, name=''):
            super().__init__()
            
            # TODO inicializacia self.x, self.y - vypocitat suradnice stredu slucky 
            self.name = name
            self.type = Model.LOOP
           

            if isinstance(items, list ) is True:    # argumentom musi byt zoznam 
                isLine = True
                isShape = True
                for k in items:                     # TODO kontrola typov - prerobit ...
                    if isinstance(k, (Model.Line, Model.Polyline, Model.CircleArc)) is False:   # TODO kontrola Spline ...
                        isLine = False
                    if isinstance(k, (Model.Rectangle , Model.RectangleBevel, Model.RectangleRound, Model.Polyline)) is False:   # TODO oostatne utvary
                        isShape = False
                        
            # ----------------------------------------------------------
            # argument - zoznam useciek 
            # TODO - rozsirit o kontrolu oblukov  
            if isLine==True: 
                # vytvorenie slucky z useciek, oblukov a lomenych ciar
                # inicializuje lines a points
                self.c = self.create_loop(items)
                self.points.append(self.lines[0].points[0])
                for q in self.lines:
                    self.points.append(self.lines[0].points[1])
                    
                Model.items[self] = [Model.LOOP,        # typ 
                                        self.points,    # list-points
                                        self.lines,     # list-lines
                                        self.c,         # loop ref
                                        self.name]      # name
                                        
            # ----------------------------------------------------------
            # argument - zoznam utvarov
            elif isShape==True:
                # vytvorenie slucky z obrysu utvarov
                a = set()                               # mnozina spolocnych useciek
                b = set()                               # mnozina vsetkych useciek 
                for j in range(len(items)):         
                    b = b | set(items[j].lines)         # mnozina vsetkych useciek
                    print(items[j])
                    for i in range(len(items)):     
                        if i != j : 
                            z = set(items[i].lines) & set(items[j].lines)
                            for k in z:
                                a.add(k)                # referencia na zdielanu usecku

                c = (a | b) - (a & b )                  # vylucenie vnutornych useciek
                
                #-------------------------------------------------------
                # usporiadanie useciek podla nadvaznosti
                print('dlzka c', len(c))     
                c = list(c)                         
                j = 0
                n = len(c)
                out_list = []
                prev_line = c[0]
                out_list.append(prev_line)

                while True:
                    i = j % n
                    next_line = c[i]
                    
                    if prev_line != next_line:
                        if prev_line.invert == False:
                            # todo - kontrola kruhoveho obluku
                            ps = prev_line.points[1]
                        else:
                            ps = prev_line.points[0]
                            
                        if ps == next_line.points[0]: 
                            #print(prev_line.l, prev_line.points[1].p , 'najdene =>', next_line.l, next_line.points[0].p)
                            prev_line = next_line
                            out_list.append(prev_line)
                            
                        elif ps == next_line.points[1]:
                            #print(prev_line.l, prev_line.points[1].p , 'najdene <=', next_line.l, next_line.points[1].p)
                            prev_line = next_line 
                            prev_line.invert  = True
                            out_list.append(prev_line)

                    if len(out_list) == len(c):
                        break

                    j+=1
                    if j>=n**2:
                        print('Error: Loop - utvary nevytvaraju suvislu hranicu')
                        break

                #print(j)
                #for q in out_list:
                #    print(q.l)
                
                self.c = self.create_loop(out_list)
                self.points.append(self.lines[0].points[0])
                for q in self.lines:
                    self.points.append(self.lines[0].points[1])
                    
                Model.items[self] = [Model.LOOP,        # typ 
                                        self.points,    # list-points
                                        self.lines,     # list-lines
                                        self.c,         # loop ref
                                        self.name]      # name
                                        
            else:
                print('Error: Nezname argumenty pre Loop')
                
                                    
            
            
            
            
        
#=======================================================================
# Shadow functions
#========================================================================
def Point(x, y, name='', lc=None):
    return Model.Point(x, y, name, lc)

def Line(p0, p1, name=''):
    return Model.Line(p0, p1, name)
    
def Arc(ps, pc, pe, name=''):
    return Model.CircleArc(ps, pc, pe, name)
    
def Rectangle(*args, name='', lc=None):
    '''
    *args - variabilny pocet argumentov
    '''
    return Model.Rectangle(*args, name=name, lc=lc)
    
    
def RectangleRound(x, y, w, h, r, name='', lc=None):
    return Model.RectangleRound(x, y, w, h, r, name, lc)
    
def RectangleBevel(x, y, w, h, r, name='', lc=None):
    return Model.RectangleBevel(x, y, w, h, r, name, lc)
    
def Circle(x, y, r, name='', segments=4, lc=None):
    return Model.Circle(x,y,r, name, segments, lc)
    
def Polygon(points, name=''):
    return Model.Polyline(points, True, name)
    
def PolyLine(points, name='', closed = False):
    return Model.Polyline(points, closed, name)
    
def Loop(items):
    s = Model.Loop(items)
    return s
    
def PlaneSurface(items):
    if isinstance(items, list): 
        loops = []
        for q in items:
            loops.append(q.c)
        #print('loops=', loops)
        surface = gmsh.model.geo.addPlaneSurface(loops)
    else:
        surface = gmsh.model.geo.addPlaneSurface([items.c])
    gmsh.model.geo.synchronize()
    return surface
    
def PhysicalLine(item, name):
    pl = gmsh.model.addPhysicalGroup(1, item.l)
    gmsh.model.setPhysicalName(1, pl, name)
    return pl
    
def PhysicalSurface(item_id, name):
    pg = gmsh.model.addPhysicalGroup(2, [item_id])
    gmsh.model.setPhysicalName(2, pg, name)
    return pg

def lastPointPos():
    return Model.lastResult

def PrintItem(K):
    '''
    Tlac vlastnosti objektu - zoznam bodov a čiar 
    '''
    # TODO - index bodu, ciary s hodnotou v danom objekte
    # TODO - doplnit Shared - spolocny bod/ciara s inymi objektami                                      
    print('                 Meno objektu', K.name)
    print('                  Typ objektu', K.type)
    print('            Pozicia stredu x ', K.x)
    print('            Pozicia stredu y ', K.y)
    print('Zoznam gmsh oznaceni bodov   ', K.p)
    print('Zoznam gmsh oznaceni useciek ', K.l)
    print('       Oznacenie gmsh slucky ', K.c)
    print()
    # TODO - index v donom utvare
    print('Body')
    print('-----+------+-------+-------+-------+----------------------------------------+')
    print(' idx | gmsh |   x   |   y   |  name | shared                                 |')
    print('-----+------+-------+-------+-------+----------------------------------------+')
    for p in K.points:
        print('  {:2d} |   {:2d} |{:> 6.2f} |{:> 6.2f} | {:>5s} | '.format(K.points.index(p), p.p, p.x, p.y, p.name) )
    print('-----+------+-------+-------+-------+----------------------------------------+')
    print()
    print('Usecky / Obluky')
    # TODO doplnit typ - obluky, polyline - koncove body, stred, opravit index , ty
    print('-----+------+--------+--------+-------+------------------+-------------------+')
    print(' idx | gmsh |   x    |    y   |  name |    start x,y     |     end x,y       |')
    print('-----+------+--------+--------+-------+--------+---------+---------+---------+')
    for w in K.lines:
        print('  {:2d} |   {:2d} | {:> 6.2f} | {:> 6.2f} | {:>5s} | {:> 6.2f} |  {:> 6.2f} |  {:> 6.2f} |  {:> 6.2f} |'.format( K.lines.index(w), 
        w.l[0], w.x, w.y, w.name, w.points[0].x, w.points[0].y, w.points[1].x, w.points[1].y) )
    print('-----+------+--------+--------+-------+--------+---------+---------+---------+')



def Plot(w):
    '''
    Vygenerovanie retazca s prikazmi pre circuit macros. 
    
    w - zoznam utvarov na vykreslenie alebo None.
    TODO Ak w ma hodnotu None, vykreslenie vsetkych utvarov.  
    '''

    fontFormat   = r'\footnotesize \textit '
    pointNumbers = True
    pointNames   = True
    lineNumbers  = True
    lineNames    = True
    arcNumbers   = True
    arcNames     = True 
    
    st = ''
    retStr = ''      # navratovy string
    
    # generovanie povelov pre objektu
    if w.type == Model.RECTANGLE or w.type == Model.RECTANGLE_BEVEL or w.type == Model.RECTANGLE_ROUND:
        retStr +=  r'{" ' + fontFormat + ' {' + str(w.name)    + r'} " at (' + str(w.x) + ',' + str(w.y) +  ') center }; ' + '\n' 
    
    
    # generovanie povelov pre zo zoznamov bodov, useciek a oblukov
    # TODO - doplnit spline krivky
    for q in w.points:
        #if q.name == '':
        #    q.name=' '
        s = r'move to (' + str(q.x) + ',' + str(q.y) +'); '
        s = s + r'dot; '
        s = s + r'color_red;'   + '\n'
        if pointNumbers:
            s = s + r'{" ' + fontFormat + ' {' + str(q.p)    + r'} " at Here + (-0.1,  0.1) above }; ' + '\n' 
        if pointNames:
            s = s + r'{" ' + fontFormat + ' {' + str(q.name) + r'} " at Here + (0.1, -0.1) below }; ' + '\n'
        s = s + r'color_black;' + '\n'
        #print(s + '\n')
        retStr = retStr + s + '\n'
        

    for q in w.lines:
        if q.type == Model.LINE:
            ps  = q.points[0]
            pe  = q.points[1]
            s = 'line -> from (' + str(ps.x) +',' + str(ps.y) + ') to (' + str(pe.x) +',' + str(pe.y) + ');'
            s = s + r'color_dark_green;'   + '\n'
            if lineNumbers:
                s = s + r'{" ' + fontFormat + ' {' + str(q.l[0])    + r'} " at last line.c rjust above}; ' + '\n' 
            if lineNames:
                s = s + r'{" ' + fontFormat + ' {' + str(q.name) + r'} " at last line.c ljust below} '  + '\n'
            s = s + r'color_black;' + '\n'
            #print(s + '\n')
            retStr = retStr + s  + '\n'
        
        
        if q.type == Model.ARC:
            ps  = q.points[0]
            pc  = q.points[1]
            pe  = q.points[2]
            r   = sqrt( (ps.x -pc.x)**2 + (ps.y - pc.y)**2 ) 
            rad = ' rad ' + str(r)
            
            '''
            Pe
            |
            Pc - Ps    (a)  kruznica - obluk e -> n (I. kv)
            
            
            Pe - Pc    (b)
                 | 
                 Ps
            '''
            if ps.x > pe.x and ps.y < pe.y:
                # poloha stredu
                if pc.x < ps.x and pc.y < pe.y:
                    cw = ' cw '    # (a)
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.ne  };'
                else:
                    cw = '    '    # (b)
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.sw  };'
                    
                arr = ' <- '
                pa  = ' (' + str(pe.x) + ',' + str(pe.y) + ') '
                pb  = ' (' + str(ps.x) + ',' + str(ps.y) + ') '
                s = 'arc' + arr + cw + rad + ' from' + pa + 'to' + pb + ';'
            
            '''
                 Ps
                 |
            Pe - Pc     (a)  kruznica obluk n -> w (II kv.)
            
            Pc - Ps     (b)
            |
            Pe
            '''
            
            if ps.x > pe.x and ps.y > pe.y:
                # poloha stredu
                if pc.x < ps.x and pc.y > pe.y:
                    pb  = ' (' + str(pe.x) + ',' + str(pe.y) + ') '
                    pa  = ' (' + str(ps.x) + ',' + str(ps.y) + ') '
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.se  };'
                    arr = ' -> '
                else:
                    pa  = ' (' + str(pe.x) + ',' + str(pe.y) + ') '
                    pb  = ' (' + str(ps.x) + ',' + str(ps.y) + ') '
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.nw  };'
                    arr = ' <- '
                cw  = ' cw '
                s = 'arc' + arr + cw + rad + ' from' + pa + 'to' + pb + ';'
            '''
            Ps - Pc
                 |
                 Pe     (a)   kruznica obluk w -> e (III kv.)
            
            Ps          (b)
            |
            Pc - Pe
            '''
            
            if ps.x < pe.x and ps.y > pe.y:
                if pc.x > ps.x and pc.y > pe.y:
                    cw  = '    '
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.sw  };'
                else:
                    cw  = ' cw '
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.ne  };'
                    
                arr = ' -> '
                pb  = ' (' + str(pe.x) + ',' + str(pe.y) + ') '
                pa  = ' (' + str(ps.x) + ',' + str(ps.y) + ') '
            
                s = 'arc' + arr + cw + rad + ' from' + pa + 'to' + pb + ';'
            
            '''
            Pc - Pe  (a)  kruznica, obluk s -> e (IV kv.)
            |
            Ps
            
                 Pe
                 |
            Ps - Pc
            '''
            if ps.x < pe.x and ps.y < pe.y:
                if pc.x < pe.x and pc.y > ps.y:
                    pa  = ' (' + str(pe.x) + ',' + str(pe.y) + ') '
                    pb  = ' (' + str(ps.x) + ',' + str(ps.y) + ') '
                    arr = ' <- '
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.se  };'
                else:
                    pb  = ' (' + str(pe.x) + ',' + str(pe.y) + ') '
                    pa  = ' (' + str(ps.x) + ',' + str(ps.y) + ') '
                    st = r'{" ' + fontFormat + '  ' + str(q.name) +  ' " at last arc.nw  };'
                    arr = ' -> '
                cw  = ' cw '
                s = 'arc' + arr + cw + rad + ' from' + pa + 'to' + pb + ';'
                
            s = s + r'color_dark_green;'
            s = s + st
            s = s + r'color_black;'
            
            #print(s + '\n')
            retStr = retStr + s  + '\n'
            st = ''
    return retStr + '\n'
            

