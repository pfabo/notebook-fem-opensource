'''
Utility pre pouyitie skriptov CircuitMacro v jupyter/notebooku.

Historia
220422  - doplnenie konverziu rad dpic prikladov
        - upravy utilit pre konverziu pomocou pycirkuit
240616  - uprava cesty pre zdielane kniznice v owncloud 
240830  - doplnenia a upravy

Otvorenie suboru v pycirkuit
          os.system('pycirkuit ' + file_name + ' &') 
'''

import os
import sys
from IPython.display import HTML, display

#=======================================================================
# template - header
# template pre zahlavie suboru, predpoklada sa pouzitie z notebooku,
# ktory je v nadradenom adresari

cm_start = r'''
.PS
pi=3.14159265359
                        # parametre z PIC (resp. GNU PIC)
scale = 2.54            # cm - jednotka pre obrazok
maxpswid = 30           # rozmery obrazku
maxpsht = 30            # 30 x 30cm, default je 8.5x11 inch
cct_init                # inicializacia lokalnych premennych

arrowwid  = 0.127       # parametre sipok - sirka
arrowht = 0.254         # dlzka

#-----------------------------------------------------------------------
# named colors
#-----------------------------------------------------------------------
define(`color_reset',              `[ resetrgb;                          ]')

# base colors
define(`color_black',              `[ setrgb(       0,       0,       0); ]')
define(`color_white',              `[ setrgb(       1,       1,       1); ]')
define(`color_grey',               `[ setrgb( 192/255, 192/255, 192/255); ]')
define(`color_blue',               `[ setrgb(       0,       0,       1); ]')
define(`color_green',              `[ setrgb(       0,       1,       0); ]')
define(`color_red',                `[ setrgb(       1,       0,       0); ]')
define(`color_yellow',             `[ setrgb(       1,       1,       0); ]')
define(`color_cyan',               `[ setrgb(       0,       1,       1); ]')
define(`color_brown',              `[ setrgb( 165/255,  42/255,  42/255); ]')
define(`color_orange',             `[ setrgb( 255/255, 165/255,       0); ]')
define(`color_violet',             `[ setrgb( 238/255, 130/255, 238/255); ]')

# light base colors
define(`color_light_grey',         `[ setrgb( 211/255, 211/255, 211/255); ]')
define(`color_light_yellow',       `[ setrgb( 255/255, 255/255, 224/255); ]')
define(`color_light_blue',         `[ setrgb( 173/255, 216/255, 230/255); ]')

# dark base colors
define(`color_dark_grey',          `[ setrgb( 169/255, 169/255, 169/255); ]')
define(`color_dark_cyan',          `[ setrgb(       0, 139/255, 139/255); ]')
define(`color_dark_green',         `[ setrgb(  47/255,  79/255,  47/255); ]')
define(`color_dark_orange',        `[ setrgb( 255/255, 140/255,       0); ]')
define(`color_dark_red',           `[ setrgb( 139/255,       0,       0); ]')
define(`color_dark_violet',        `[ setrgb( 148/255,       0, 211/255); ]')

# grey colors
define(`color_silver'              `[ setrgb( 192/255, 192/255, 192/255); ]')


# named colors
define(`color_aquamarine',         `[ setrgb( 127/255, 255/255, 212/255); ]')
define(`color_cadetblue',          `[ setrgb(  95/255, 158/255, 160/255); ]')
define(`color_coral',              `[ setrgb( 255/255, 127/255,       0); ]')
define(`color_gold',               `[ setrgb( 204/255, 127/255,  50/255); ]')
define(`color_mediumForestGreen',  `[ setrgb( 107/255, 142/255,  35/255); ]')
define(`color_slategrey',          `[ setrgb( 112/255, 128/255, 144/255); ]')
define(`color_firebrick',          `[ setrgb( 178/255,  34/255,  34/255); ]')
define(`color_olive',              `[ setrgb( 128/255, 128/255,       0); ]')
define(`color_khaki',              `[ setrgb( 240/255, 230/255, 140/255); ]')
define(`color_dark_khaki',         `[ setrgb( 189/255, 183/255, 107/255); ]')
define(`color_lemonchiffon',       `[ setrgb( 255/255, 250/255, 205/255); ]')
define(`color_steelblue',          `[ setrgb(  70/255, 130/255, 180/255); ]')

# light named colors
define(`color_snow',               `[ setrgb( 255/255, 250/255, 250/255); ]')
define(`color_honeydew',           `[ setrgb( 240/255, 255/255, 240/255); ]')
define(`color_mintcream',          `[ setrgb( 245/255, 255/255, 250/255); ]')
define(`color_azure',              `[ setrgb( 240/255, 255/255, 255/255); ]')
define(`color_aliceblue',          `[ setrgb( 240/255, 248/255, 255/255); ]')
define(`color_ghostwhite',         `[ setrgb( 248/255, 248/255, 255/255); ]')
define(`color_whitesmoke',         `[ setrgb( 245/255, 245/255, 245/255); ]')
define(`color_seashell',           `[ setrgb( 255/255, 245/255, 238/255); ]')
define(`color_beige',              `[ setrgb( 245/255, 245/255, 220/255); ]')
define(`color_oldlace',            `[ setrgb( 253/255, 248/255, 230/255); ]')
define(`color_floralwhite',        `[ setrgb( 255/255, 250/255, 240/255); ]')
define(`color_ivory',              `[ setrgb( 255/255, 255/255, 240/255); ]')
define(`color_antiquewhite',       `[ setrgb( 255/255, 235/255, 215/255); ]')
define(`color_linien',             `[ setrgb( 250/255, 240/255, 230/255); ]')
define(`color_lavenderblush',      `[ setrgb( 255/255, 240/255, 245/255); ]')
define(`color_mistyrose',          `[ setrgb( 255/255, 228/255, 225/255); ]')

#define(`color_'                `[ setrgb( /255, /255, /255); ]')

#-----------------------------------------------------------------------
# kody farieb pre farebnu vypln
# rgbfill( r,g,b, {uzavreta oblast, box, circle ...})

# base colors
define(`fill_black',              `       0,       0,       0')
define(`fill_white',              `       1,       1,       1')
define(`fill_grey',               `192/255, 192/255, 192/255')
define(`fill_blue',               `       0,       0,       1')
define(`fill_green',              `       0,       1,       0')
define(`fill_red',                `       1,       0,       0')
define(`fill_yellow',             `       1,       1,       0')
define(`fill_cyan',               `       0,       1,       1')
define(`fill_brown',              ` 165/255,  42/255,  42/255')
define(`fill_orange',             ` 255/255, 165/255,       0')
define(`fill_violet',             ` 238/255, 130/255, 238/255')

# light base colors
define(`fill_light_grey',         ` 211/255, 211/255, 211/255')
define(`fill_light_yellow',       ` 255/255, 255/255, 224/255')
define(`fill_light_blue',         ` 173/255, 216/255, 230/255')

# dark base colors
define(`fill_dark_grey',          ` 169/255, 169/255, 169/255')
define(`fill_dark_cyan',          `       0, 139/255, 139/255')
define(`fill_dark_green',         `  47/255,  79/255,  47/255')
define(`fill_dark_orange',        ` 255/255, 140/255,       0')
define(`fill_dark_red',           ` 139/255,       0,       0')
define(`fill_dark_violet',        ` 148/255,       0, 211/255')

# grey colors
define(`fill_silver'              ` 192/255, 192/255, 192/255')

define(`gnd',`[
    d = 1;
    L: line from Here to Here + (0, -d/4)
    linethick = 2
    line from L.end + (-d/4, 0) to L.end + (d/4, 0) 
]')

define(`power',`[
    d = 1;
    up_
    PWR: tconn(d/2, 0); "\textit{$1}" at PWR.n above; 
]')

#=======================================================================

Origin: Here 
d = 2;                  # 1cm zakladna dlzka
'''


# template - grid (optional)
cm_grid = r'''
#=======================================================================
# grid - vykreslenie mriezky
# grid(x,y) - velkost x,y - rozmery v default jednotkach
#-----------------------------------------------------------------------
define(`grid',`[
    
    W: box ht $2+1 wid $1+1 invis
    move to W.w + (.5,0)
    Q: box ht $2 wid $1 invis

    setrgb(0.9,0.9,0.9);
    for i=0 to $2*2 do{
        line from (Q.w.x, Q.s.y+i*0.5) to (Q.w.x+$1, Q.s.y+i*0.5);
        { color_blue; sprintf("\scriptsize %g",i/2) at (Q.w.x-0.55, Q.s.y+i*0.5) ljust; setrgb(0.9,0.9,0.9); };
    }; 
    for i=0 to $1*2 do{
        line from (Q.w.x + i*0.5, Q.s.y) to (Q.w.x + i*0.5, Q.s.y+$2);
        { color_blue; sprintf("\scriptsize %g",i/2) at (Q.w.x + i*0.5, Q.s.y-0.2); setrgb(0.9,0.9,0.9); };
    }
    resetrgb;
]')

# mriezka, size_x a size_y sa substituuju z argumentov funkcie
move to (-0.5, size_y/2); grid(size_x, size_y); move to 0,0;
'''

# template - footer
cm_end = r'''
.PE
'''

#======================================================================

def cm_compile(file_name, cm_data='', dpi=300, grid=False, dx=10, dy=10, log=False):
    '''
    Konverzia textu s makrami na obrazok.
    Vyuziva pycirkuit.
    '''
    fp = open( file_name + '.ckt', 'w'); 
    
    if grid == True:
        fp.write(cm_start +\
                 r'size_x='+ str(dx) +';\n' +\
                 r'size_y='+ str(dy) +';\n' +\
                cm_grid +\
                cm_data +\
                cm_end); 
    else:
        fp.write(cm_start + cm_data + cm_end); 
    fp.close()

    os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    if log==True:
        os.system(r'pycirkuit --overwrite --dpi ' + str(dpi) +' -p ' + file_name + '.ckt ') 
    else:
        os.system(r'pycirkuit --overwrite --dpi ' + str(dpi) +' -p ' + file_name + '.ckt > /dev/null')

    return file_name + '.ckt'
    
#-----------------------------------------------------------------------

CIRCUIT_MACROS_PATH = './img/cm'

def cm2ps(fname):
    '''
    Konverzia cm na eps
    '''

    fname_base = os.path.splitext(fname )[0]
    texfile      = fname_base + '_pst'
    templatefile = fname_base + '.tex'
    epsfile      = fname_base + '.eps'

    #print('>> m4 pstricks')
    os.system( 'm4 -I %s pstricks.m4 %s | dpic -p > %s'%(CIRCUIT_MACROS_PATH, fname, texfile+'.tex') )

    latextemplate = '''\\documentclass{article}
    \\usepackage{times,pstricks,pst-eps,pst-grad,xfrac}
    \\usepackage{graphicx}
    \\begin{document}
    \\begin{TeXtoEPS}
    \\input %s
    \\end{TeXtoEPS}\\end{document}
    '''%texfile

    f = open( templatefile, 'w' )
    f.write( latextemplate )
    f.flush()
    f.close()

    #print('>> latex')    
    os.system( 'latex -output-directory=./img/  %s'%templatefile )       

    #print('>> dvips')
    os.system( 'dvips  -E %s -o %s '%(fname_base, epsfile) ) 
    
    # na poradi argumentov ZALEZI !!!
    #print('>> convert eps to png')
    os.system('convert -density 600 -quality 100 -flatten %s -colorspace RGB %s'%(epsfile, fname_base+'.png'))

    #os.system( 'dvips -Ppdf -G0 -E %s -o %s'%(fname_base, epsfile) )
    #os.system( 'rm '+fname_base + '.dvi' ) 
    #os.system( 'rm '+fname_base + '.aux' ) 
    #os.system( 'rm '+fname_base + '.log' ) 
        

def cm_show(pngfile, width=300):
    '''
    Display *.png file in HTML string. 
    
    more userfull as
        Image(filename='image.png', width=600)     
    '''
    s = r'<img src="%s" width=%d>' %(pngfile, width)
    display(HTML(s))
    
        
