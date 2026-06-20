# ============================================================================
#  PROCESS-TUBE ADAPTER  -  parts generator  (plain-English commented version)
# ============================================================================
#  WHAT THIS IS:
#    A recipe that DRAWS the parts in 3D and saves printer files (.stl) and
#    editable CAD files (.step). It does NOT run your printer - it just makes
#    the files. Change a number in the SETTINGS block and re-run it, and every
#    part is redrawn to match.
#
#  HOW TO RUN IT (on Zeus, in a terminal):
#    pip install build123d bd_warehouse      <- one-time, installs the drawing tools
#    python3 process_adapter_v4_commented.py <- builds all the files into out4/
#
#  All measurements are in millimeters (mm).
# ============================================================================

from math import cos, radians, pi, sin     # basic math helpers (for angles)
from build123d import *                    # the 3D-drawing toolkit
from bd_warehouse.thread import IsoThread  # add-on that draws real screw threads


# ============================================================================
#  SETTINGS  -  every dimension lives here. Change a number, re-run, done.
# ============================================================================

BORE = 4.0          # width of the hole down the middle (where refrigerant flows)
PRINT_CLR = 0.40    # extra slack so printed threads aren't too tight to screw together

# The screw joint between the BODY and the CAP:
CT_NOM, CT_PITCH = 20.0, 2.5        # thread is 20mm across, threads spaced 2.5mm apart
CT_LEN_MALE, CT_LEN_FEMALE = 12.0, 13.0   # thread length: 12 on the body, 13 inside the cap

# The flat tip of the body that pushes down on the washer:
NOSE_DIA, NOSE_LEN = 14.0, 5.0      # 14mm wide, 5mm long

# The fat grip barrel you turn with your fingers:
GRIP_R, GRIP_LEN, FLUTES, FL_RC, FL_DEPTH = 17.0, 12.0, 14, 3.0, 1.3
#   GRIP_R 17   -> 17mm from center to edge (so 34mm across)
#   GRIP_LEN 12 -> 12mm tall
#   FLUTES 14   -> 14 finger-grooves cut around it for grip
#   FL_RC 3.0 / FL_DEPTH 1.3 -> size and depth of each groove

# The boss on top that you drill/tap for the brass fitting:
NPT_TAP, BOSS_OD, BOSS_LEN, CHAMFER = 11.1125, 20.0, 14.0, 1.2
#   NPT_TAP 11.11 -> the pre-drilled hole, correct size to hand-tap 1/4" NPT
#   BOSS_OD 20    -> boss is 20mm across   |  BOSS_LEN 14 -> 14mm tall
#   CHAMFER 1.2   -> small bevel at the mouth so the tap starts straight

# The O-ring pocket (the "gland") inside each cap:
CS = 1.78           # thickness of the Viton O-ring (this is the 1/16" size)
SQUEEZE = 0.15      # squash the O-ring 15% to make it seal against the tube
FLOOR_T, GLAND_H = 2.5, 2.4     # cap floor is 2.5 thick; O-ring pocket is 2.4 deep
CBORE_DIA, CBORE_DEPTH = 14.4, 5.0  # wider pocket above it (14.4 wide, 5 deep) for the washer + nose

# The anti-extrusion washer (the disc that caps the O-ring):
WASHER_OD, WASHER_T, WASHER_ID_CLR = 14.0, 1.5, 0.40  # 14mm across, 1.5 thick, 0.4 hole slack

CAP_AF = 28.0       # the cap's six-sided hub measures 28mm across the flats
TUBE_CLR = 0.40     # extra room so the copper tube slides through easily

# The grip wings on the cap (so you can hand-tighten, no wrench):
R_WING, WING_W, NWING = 24.0, 8.0, 3   # wings reach out to 24mm, 8mm wide, 3 of them

# The four copper tube sizes and their actual widths in mm:
TUBES = {"3-16": 4.762, "1-4": 6.350, "5-16": 7.938, "3-8": 9.525}

# Which Viton O-ring (from the Harbor Freight kit) goes with each tube size:
RING = {"3-16": "A008", "1-4": "A010", "5-16": "A011", "3-8": "A012"}

# Two small helper formulas:
def aflat(af):                      # converts "across the flats" into the math the
    return af / (2 * cos(radians(30)))   # hexagon-drawing command needs

def gland_dia(od):                  # O-ring pocket width = tube width + room for a
    return od + 2 * CS * (1 - SQUEEZE)   # squashed O-ring on each side


# ============================================================================
#  BUILD THE BODY  (the shared piece: nose + grip + boss)
# ============================================================================
def build_body():
    z = 0.0   # "z" tracks how high up we are as we stack shapes from the bottom

    # 1) the flat nose at the very bottom
    b = Pos(0, 0, z + NOSE_LEN/2) * Cylinder(NOSE_DIA/2, NOSE_LEN)
    z += NOSE_LEN

    # 2) the screw thread that goes into the cap (a plain post + real threads on it)
    th = IsoThread(major_diameter=CT_NOM - PRINT_CLR, pitch=CT_PITCH,
                   length=CT_LEN_MALE, external=True, end_finishes=("fade", "fade"))
    b += Pos(0, 0, z) * (Cylinder(th.min_radius, CT_LEN_MALE,
                         align=(Align.CENTER, Align.CENTER, Align.MIN)) + th)
    z += CT_LEN_MALE

    # 3) the fat grip barrel...
    grip = Pos(0, 0, z) * Cylinder(GRIP_R, GRIP_LEN,
                                   align=(Align.CENTER, Align.CENTER, Align.MIN))
    #    ...then carve 14 finger-grooves around it (repeat the cut, rotating each time)
    Rc = GRIP_R + FL_RC - FL_DEPTH
    for i in range(FLUTES):
        a = 2 * pi * i / FLUTES
        grip -= Pos(Rc*cos(a), Rc*sin(a), z - 1) * Cylinder(FL_RC, GRIP_LEN + 2,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    b += grip
    z += GRIP_LEN

    # 4) the boss on top
    b += Pos(0, 0, z) * Cylinder(BOSS_OD/2, BOSS_LEN,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN))
    top = z + BOSS_LEN

    # 5) now SCOOP OUT the holes ("-=" means remove this material):
    #    - the wide hole in the boss you tap for NPT
    b -= Pos(0, 0, top - BOSS_LEN) * Cylinder(NPT_TAP/2, BOSS_LEN + 0.01,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    #    - the thin refrigerant passage running all the way down
    b -= Cylinder(BORE/2, top - BOSS_LEN + 0.01,
                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    #    - the little bevel at the mouth so the tap starts straight
    b -= Pos(0, 0, top - CHAMFER) * Cone(NPT_TAP/2, NPT_TAP/2 + CHAMFER, CHAMFER,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    return b


# ============================================================================
#  BUILD A CAP  (one per tube size: hex hub + wings + O-ring pocket + threads)
# ============================================================================
def build_cap(od):                  # "od" = the tube's outer width
    Dg = gland_dia(od)              # work out this cap's O-ring pocket width
    H = FLOOR_T + GLAND_H + CBORE_DEPTH + CT_LEN_FEMALE   # total cap height

    # the six-sided hub
    c = extrude(Plane.XY * RegularPolygon(aflat(CAP_AF), 6), H)

    # add 3 grip wings (each = a paddle + a rounded tip), spaced evenly around
    for i in range(NWING):
        a = 2 * pi * i / NWING
        wing = Pos((11 + R_WING)/2, 0, H/2) * Box(R_WING - 11, WING_W, H) \
             + Pos(R_WING, 0, H/2) * Cylinder(WING_W/2, H)
        c += Rot(0, 0, a * 180/pi) * wing

    # SCOOP OUT the inside, from the bottom up:
    c -= Cylinder((od + TUBE_CLR)/2, FLOOR_T + 0.1,           # 1) hole the tube slides through
                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(0, 0, FLOOR_T) * Cylinder(Dg/2, GLAND_H + 0.01,  # 2) the O-ring pocket
                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(0, 0, FLOOR_T + GLAND_H) * Cylinder(CBORE_DIA/2, CBORE_DEPTH + 0.01,  # 3) washer/nose pocket
                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    c -= Pos(0, 0, FLOOR_T + GLAND_H + CBORE_DEPTH) * Cylinder(CT_NOM/2, CT_LEN_FEMALE + 0.1,  # 4) clearance for threads
                  align=(Align.CENTER, Align.CENTER, Align.MIN))

    # add the actual screw threads inside that top hole, so the body screws in
    ith = IsoThread(major_diameter=CT_NOM, pitch=CT_PITCH, length=CT_LEN_FEMALE,
                    external=False, end_finishes=("fade", "fade"))
    c += Pos(0, 0, FLOOR_T + GLAND_H + CBORE_DEPTH) * ith
    return c


# ============================================================================
#  BUILD A WASHER  (just a disc with a hole)
# ============================================================================
def build_washer(od):
    r = Cylinder(WASHER_OD/2, WASHER_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    r -= Cylinder((od + WASHER_ID_CLR)/2, WASHER_T + 0.1,     # punch the center hole
                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    return r


# ============================================================================
#  MAKE EVERYTHING AND SAVE THE FILES
# ============================================================================
import os
out = "/home/claude/out4"          # the folder the files get saved into
os.makedirs(out, exist_ok=True)    # create that folder if it doesn't exist

# build the body once (all four sizes share it) and save it two ways
body = build_body()
export_stl(body, f"{out}/body.stl")     # .stl = the file your slicer/printer reads
export_step(body, f"{out}/body.step")   # .step = the editable CAD file
print("BODY  noseO14 flat, gripO34, vol", round(body.volume))

# now loop through the four tube sizes, building + saving a cap and washer for each
for n, od in TUBES.items():
    c = build_cap(od)
    w = build_washer(od)
    export_stl(c, f"{out}/cap_{n}.stl");    export_step(c, f"{out}/cap_{n}.step")
    export_stl(w, f"{out}/washer_{n}.stl"); export_step(w, f"{out}/washer_{n}.step")
    print(f"  {n:5s} glandO{gland_dia(od):.1f}  washerIDO{od + WASHER_ID_CLR:.2f}  Viton {RING[n]}")

print("squeeze", int(SQUEEZE * 100), "% | done")
