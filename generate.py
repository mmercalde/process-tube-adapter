"""
Process-Tube Adapter — parametric generator (v5, twin-O-ring grooved washer pair)

Builds the body, four caps, and four grooved washers. Change a constant, re-run,
and all STL/STEP files are rebuilt into ./stl and ./step.

    pip install build123d bd_warehouse
    python3 generate.py

Sealing principle: a PAIR of grooved washers (printed CF) sandwiches two standard
O-rings. The OUTER ring seals radially against the 17 mm cap bore; the INNER ring
seals radially against the copper tube OD. The body's clearance plunger nose drives
the sandwich down against a reinforced floor — crush is thread-driven, with no hard
shoulder to bottom out, so FDM tolerance variation never starves the seal.
"""
from build123d import *
from bd_warehouse.thread import IsoThread
from math import cos, sin, pi
import os

# ---------------- shared ----------------
PRINT_CLR = 0.40                      # FDM thread clearance
CT_NOM, CT_PITCH = 20.0, 2.5          # body<->cap thread (M20x2.5)
M = (Align.CENTER, Align.CENTER, Align.MIN)
TUBES = {"3-16": 4.762, "1-4": 6.350, "5-16": 7.938, "3-8": 9.525}  # copper OD

# ---------------- cap ----------------
BORE       = 17.0                     # gland bore (seals outer ring) — matches Robinair
FLOOR_T    = 4.5                      # reinforced floor (was 2.5, buckled under crush)
INT_DEPTH  = 15.65                    # bore-floor to top opening (measured)
THREAD_DEPTH = 7.0
GLAND_DEPTH  = INT_DEPTH - THREAD_DEPTH
CAP_AF     = 28.0                     # hex across-flats
TUBE_CLR   = 0.40
R_WING, WING_W, NWING = 24.0, 8.0, 3  # hand-tighten wings

# ---------------- grooved washer (prints x2 per cap) ----------------
WASHER_OD, WASHER_T, WASHER_HOLE_CLR = 16.6, 3.0, 0.6
OG_W, OG_D = 3.0, 1.4                 # outer ring pocket (holds bore O-ring)
IG_W, IG_D = 2.0, 1.0                 # inner ring pocket (holds tube O-ring)

# ---------------- body ----------------
REFRIG_BORE = 4.0
NOSE_DIA, NOSE_LEN = 15.0, 8.0        # clearance plunger: floats in 17 bore, no bottoming
CT_LEN_MALE = 12.0
GRIP_R, GRIP_LEN, FLUTES, FL_RC, FL_DEPTH = 17.0, 12.0, 14, 3.0, 1.3
NPT_TAP, BOSS_OD, BOSS_LEN, CHAMFER = 11.1125, 20.0, 14.0, 1.2   # 1/4" NPT tap-drill boss


def aflat(af):
    return af / (2 * cos(pi / 6))


def build_cap(od):
    H = FLOOR_T + INT_DEPTH
    c = extrude(Plane.XY * RegularPolygon(aflat(CAP_AF), 6), H)
    for i in range(NWING):
        a = 2 * pi * i / NWING
        wing = (Pos((11 + R_WING) / 2, 0, H / 2) * Box(R_WING - 11, WING_W, H)
                + Pos(R_WING, 0, H / 2) * Cylinder(WING_W / 2, H))
        c += Rot(0, 0, a * 180 / pi) * wing
    c -= Cylinder((od + TUBE_CLR) / 2, FLOOR_T + 0.1, align=M)                       # tube hole
    c -= Pos(0, 0, FLOOR_T) * Cylinder(BORE / 2, GLAND_DEPTH + 0.01, align=M)        # 17 gland
    c -= Pos(0, 0, FLOOR_T + GLAND_DEPTH) * Cylinder(CT_NOM / 2, THREAD_DEPTH + 0.1, align=M)
    c += Pos(0, 0, FLOOR_T + GLAND_DEPTH) * IsoThread(
        major_diameter=CT_NOM, pitch=CT_PITCH, length=THREAD_DEPTH,
        external=False, end_finishes=("fade", "fade"))
    return c


def build_washer(od):
    hole = od + WASHER_HOLE_CLR
    w = Cylinder(WASHER_OD / 2, WASHER_T, align=M) - Cylinder(hole / 2, WASHER_T + 0.1, align=M)
    w -= Pos(0, 0, WASHER_T - OG_D) * (Cylinder(WASHER_OD / 2, OG_D + 0.01, align=M)
                                       - Cylinder(WASHER_OD / 2 - OG_W, OG_D + 0.1, align=M))
    w -= Pos(0, 0, WASHER_T - IG_D) * (Cylinder(hole / 2 + IG_W, IG_D + 0.01, align=M)
                                       - Cylinder(hole / 2, IG_D + 0.1, align=M))
    return w


def build_body():
    z = 0.0
    b = Pos(0, 0, NOSE_LEN / 2) * Cylinder(NOSE_DIA / 2, NOSE_LEN); z += NOSE_LEN
    th = IsoThread(major_diameter=CT_NOM - PRINT_CLR, pitch=CT_PITCH, length=CT_LEN_MALE,
                   external=True, end_finishes=("fade", "fade"))
    b += Pos(0, 0, z) * (Cylinder(th.min_radius, CT_LEN_MALE, align=M) + th); z += CT_LEN_MALE
    grip = Pos(0, 0, z) * Cylinder(GRIP_R, GRIP_LEN, align=M)
    Rc = GRIP_R + FL_RC - FL_DEPTH
    for i in range(FLUTES):
        a = 2 * pi * i / FLUTES
        grip -= Pos(Rc * cos(a), Rc * sin(a), z - 1) * Cylinder(FL_RC, GRIP_LEN + 2, align=M)
    b += grip; z += GRIP_LEN
    b += Pos(0, 0, z) * Cylinder(BOSS_OD / 2, BOSS_LEN, align=M); top = z + BOSS_LEN
    b -= Pos(0, 0, top - BOSS_LEN) * Cylinder(NPT_TAP / 2, BOSS_LEN + 0.01, align=M)
    b -= Cylinder(REFRIG_BORE / 2, top - BOSS_LEN + 0.01, align=M)
    b -= Pos(0, 0, top - CHAMFER) * Cone(NPT_TAP / 2, NPT_TAP / 2 + CHAMFER, CHAMFER, align=M)
    return b


if __name__ == "__main__":
    os.makedirs("stl", exist_ok=True); os.makedirs("step", exist_ok=True)
    body = build_body()
    export_stl(body, "stl/body.stl"); export_step(body, "step/body.step")
    for n, od in TUBES.items():
        c = build_cap(od);  export_stl(c, f"stl/cap_{n}.stl");    export_step(c, f"step/cap_{n}.step")
        w = build_washer(od); export_stl(w, f"stl/washer_{n}.stl"); export_step(w, f"step/washer_{n}.step")
    print("Built body + 4 caps + 4 grooved washers into ./stl and ./step")
