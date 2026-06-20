"""
Process-tube adapter -- FINAL (Viton O-ring, R600a low-pressure)
  body (flat 14mm nose, fluted grip, NPT boss) + 4 winged caps + 4 washers
  Seals = purchased HF Viton 1/16" CS rings (A008/A010/A011/A012), ~15% radial squeeze
"""
from math import cos, radians, pi, sin
from build123d import *
from bd_warehouse.thread import IsoThread

BORE=4.0; PRINT_CLR=0.40
CT_NOM,CT_PITCH=20.0,2.5; CT_LEN_MALE,CT_LEN_FEMALE=12.0,13.0
NOSE_DIA,NOSE_LEN=14.0,5.0
GRIP_R,GRIP_LEN,FLUTES,FL_RC,FL_DEPTH=17.0,12.0,14,3.0,1.3
NPT_TAP,BOSS_OD,BOSS_LEN,CHAMFER=11.1125,20.0,14.0,1.2
# cap / O-ring gland
CS=1.78; SQUEEZE=0.15
FLOOR_T,GLAND_H=2.5,2.4
CBORE_DIA,CBORE_DEPTH=14.4,5.0
WASHER_OD,WASHER_T,WASHER_ID_CLR=14.0,1.5,0.40
CAP_AF=28.0; TUBE_CLR=0.40
R_WING,WING_W,NWING=24.0,8.0,3
TUBES={"3-16":4.762,"1-4":6.350,"5-16":7.938,"3-8":9.525}
def aflat(af): return af/(2*cos(radians(30)))
def gland_dia(od): return od + 2*CS*(1-SQUEEZE)     # ~15% squeeze

def build_body():
    z=0.0
    b=Pos(0,0,z+NOSE_LEN/2)*Cylinder(NOSE_DIA/2,NOSE_LEN); z+=NOSE_LEN
    th=IsoThread(major_diameter=CT_NOM-PRINT_CLR,pitch=CT_PITCH,length=CT_LEN_MALE,
                 external=True,end_finishes=("fade","fade"))
    b+=Pos(0,0,z)*(Cylinder(th.min_radius,CT_LEN_MALE,align=(Align.CENTER,Align.CENTER,Align.MIN))+th); z+=CT_LEN_MALE
    grip=Pos(0,0,z)*Cylinder(GRIP_R,GRIP_LEN,align=(Align.CENTER,Align.CENTER,Align.MIN))
    Rc=GRIP_R+FL_RC-FL_DEPTH
    for i in range(FLUTES):
        a=2*pi*i/FLUTES
        grip-=Pos(Rc*cos(a),Rc*sin(a),z-1)*Cylinder(FL_RC,GRIP_LEN+2,align=(Align.CENTER,Align.CENTER,Align.MIN))
    b+=grip; z+=GRIP_LEN
    b+=Pos(0,0,z)*Cylinder(BOSS_OD/2,BOSS_LEN,align=(Align.CENTER,Align.CENTER,Align.MIN)); top=z+BOSS_LEN
    b-=Pos(0,0,top-BOSS_LEN)*Cylinder(NPT_TAP/2,BOSS_LEN+0.01,align=(Align.CENTER,Align.CENTER,Align.MIN))
    b-=Cylinder(BORE/2,top-BOSS_LEN+0.01,align=(Align.CENTER,Align.CENTER,Align.MIN))
    b-=Pos(0,0,top-CHAMFER)*Cone(NPT_TAP/2,NPT_TAP/2+CHAMFER,CHAMFER,align=(Align.CENTER,Align.CENTER,Align.MIN))
    return b

def build_cap(od):
    Dg=gland_dia(od)
    H=FLOOR_T+GLAND_H+CBORE_DEPTH+CT_LEN_FEMALE
    c=extrude(Plane.XY*RegularPolygon(aflat(CAP_AF),6),H)
    for i in range(NWING):                       # grip wings
        a=2*pi*i/NWING
        wing=Pos((11+R_WING)/2,0,H/2)*Box(R_WING-11,WING_W,H)+Pos(R_WING,0,H/2)*Cylinder(WING_W/2,H)
        c+=Rot(0,0,a*180/pi)*wing
    # bores bottom->top
    c-=Cylinder((od+TUBE_CLR)/2,FLOOR_T+0.1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    c-=Pos(0,0,FLOOR_T)*Cylinder(Dg/2,GLAND_H+0.01,align=(Align.CENTER,Align.CENTER,Align.MIN))
    c-=Pos(0,0,FLOOR_T+GLAND_H)*Cylinder(CBORE_DIA/2,CBORE_DEPTH+0.01,align=(Align.CENTER,Align.CENTER,Align.MIN))
    c-=Pos(0,0,FLOOR_T+GLAND_H+CBORE_DEPTH)*Cylinder(CT_NOM/2,CT_LEN_FEMALE+0.1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    ith=IsoThread(major_diameter=CT_NOM,pitch=CT_PITCH,length=CT_LEN_FEMALE,external=False,end_finishes=("fade","fade"))
    c+=Pos(0,0,FLOOR_T+GLAND_H+CBORE_DEPTH)*ith
    return c

def build_washer(od):
    r=Cylinder(WASHER_OD/2,WASHER_T,align=(Align.CENTER,Align.CENTER,Align.MIN))
    r-=Cylinder((od+WASHER_ID_CLR)/2,WASHER_T+0.1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    return r

import os
import os
RING={"3-16":"A008","1-4":"A010","5-16":"A011","3-8":"A012"}
os.makedirs("stl",exist_ok=True); os.makedirs("step",exist_ok=True)
body=build_body(); export_stl(body,"stl/body.stl"); export_step(body,"step/body.step")
print("BODY  nose\u00d814 flat, grip\u00d834, vol",round(body.volume))
for n,od in TUBES.items():
    c=build_cap(od); w=build_washer(od)
    export_stl(c,f"stl/cap_{n}.stl"); export_step(c,f"step/cap_{n}.step")
    export_stl(w,f"stl/washer_{n}.stl"); export_step(w,f"step/washer_{n}.step")
    print(f"  {n:5s} gland\u00d8{gland_dia(od):.1f}  washerID\u00d8{od+WASHER_ID_CLR:.2f}  Viton {RING[n]}")
print("squeeze",int(SQUEEZE*100),"% | done")
