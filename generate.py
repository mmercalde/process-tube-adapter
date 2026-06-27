"""
Process-Tube Adapter - parametric generator (v6, channel-washer sealing)

Builds the body, four caps, four channel washers (the sealing element), and four
flat backer washers. Change a constant, re-run, all STL/STEP rebuild into ./stl, ./step.

    pip install build123d bd_warehouse
    python3 generate.py

Sealing: a thick CHANNEL washer fills the annular gap between tube and 17 mm bore.
A groove in its OUTER RIM holds an O-ring that bulges out to seal the bore; a groove
in its CENTER HOLE holds an O-ring that bulges in to seal the copper tube OD. Both
rings get ~20 % radial squeeze. A flat BACKER washer spreads the plunger crush load.
The body's clearance plunger nose drives the stack with no hard stop, so FDM tolerance
never starves the seal.
"""
from build123d import *
from bd_warehouse.thread import IsoThread
from math import cos, sin, pi
import os

PRINT_CLR = 0.40
CT_NOM, CT_PITCH = 20.0, 2.5
M = (Align.CENTER, Align.CENTER, Align.MIN)
TUBES = {"3-16": 4.762, "1-4": 6.350, "5-16": 7.938, "3-8": 9.525}

# ---- cap ----
BORE, FLOOR_T, INT_DEPTH = 17.0, 4.5, 15.65
THREAD_DEPTH = 7.0
GLAND_DEPTH = INT_DEPTH - THREAD_DEPTH          # 8.65 - holds the 8.0 washer stack
CAP_AF, TUBE_CLR = 28.0, 0.40
R_WING, WING_W, NWING = 24.0, 8.0, 3

# ---- washers ----
WASHER_OD, WASHER_HOLE_CLR = 16.6, 0.6
CHAN_T, BACK_T = 6.0, 2.0                        # channel + backer = 8.0 stack
SQUEEZE = 0.20
CS_OUT, CS_IN = 2.62, 1.78                       # A112 outer ; 1/16" inner
OG_ROOT = BORE - 2 * CS_OUT * (1 - SQUEEZE)      # 12.81 outer groove root (vs 17 bore)
OG_W = CS_OUT * 1.2                              # 3.14
IG_W = CS_IN * 1.2                               # 2.14

# ---- body ----
REFRIG_BORE = 4.0
NOSE_DIA, NOSE_LEN = 15.0, 8.0
CT_LEN_MALE = 12.0
GRIP_R, GRIP_LEN, FLUTES, FL_RC, FL_DEPTH = 17.0, 12.0, 14, 3.0, 1.3
NPT_TAP, BOSS_OD, BOSS_LEN, CHAMFER = 11.1125, 20.0, 14.0, 1.2


def aflat(af): return af / (2 * cos(pi / 6))


def build_cap(od):
    H = FLOOR_T + INT_DEPTH
    c = extrude(Plane.XY * RegularPolygon(aflat(CAP_AF), 6), H)
    for i in range(NWING):
        a = 2 * pi * i / NWING
        c += Rot(0, 0, a * 180 / pi) * (Pos((11 + R_WING) / 2, 0, H / 2) * Box(R_WING - 11, WING_W, H)
                                        + Pos(R_WING, 0, H / 2) * Cylinder(WING_W / 2, H))
    c -= Cylinder((od + TUBE_CLR) / 2, FLOOR_T + 0.1, align=M)
    c -= Pos(0, 0, FLOOR_T) * Cylinder(BORE / 2, GLAND_DEPTH + 0.01, align=M)
    c -= Pos(0, 0, FLOOR_T + GLAND_DEPTH) * Cylinder(CT_NOM / 2, THREAD_DEPTH + 0.1, align=M)
    c += Pos(0, 0, FLOOR_T + GLAND_DEPTH) * IsoThread(major_diameter=CT_NOM, pitch=CT_PITCH,
                                                      length=THREAD_DEPTH, external=False,
                                                      end_finishes=("fade", "fade"))
    return c


def build_channel_washer(od):
    hole = od + WASHER_HOLE_CLR
    ig_root = od + 2 * CS_IN * (1 - SQUEEZE)     # inner groove root (vs tube) -> 20% squeeze
    w = Cylinder(WASHER_OD / 2, CHAN_T, align=M) - Cylinder(hole / 2, CHAN_T + 0.1, align=M)
    # outer rim groove (seals 17 bore)
    z = (CHAN_T - OG_W) / 2
    w -= Pos(0, 0, z) * (Cylinder(WASHER_OD / 2 + 0.1, OG_W, align=M) - Cylinder(OG_ROOT / 2, OG_W, align=M))
    # inner hole groove (seals tube OD)
    z = (CHAN_T - IG_W) / 2
    w -= Pos(0, 0, z) * (Cylinder(ig_root / 2, IG_W, align=M) - Cylinder(hole / 2 - 0.1, IG_W, align=M))
    return w


def build_backer_washer(od):
    hole = od + WASHER_HOLE_CLR
    return Cylinder(WASHER_OD / 2, BACK_T, align=M) - Cylinder(hole / 2, BACK_T + 0.1, align=M)


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
    export_stl(build_body(), "stl/body.stl"); export_step(build_body(), "step/body.step")
    for n, od in TUBES.items():
        c = build_cap(od);             export_stl(c, f"stl/cap_{n}.stl");            export_step(c, f"step/cap_{n}.step")
        cw = build_channel_washer(od); export_stl(cw, f"stl/washer_channel_{n}.stl"); export_step(cw, f"step/washer_channel_{n}.step")
        bw = build_backer_washer(od);  export_stl(bw, f"stl/washer_backer_{n}.stl");  export_step(bw, f"step/washer_backer_{n}.step")
    print(f"channel washer {CHAN_T}mm + backer {BACK_T}mm = {CHAN_T+BACK_T}mm stack (gland {GLAND_DEPTH})")
    print(f"outer groove root {OG_ROOT:.2f} (20% on A112) | inner groove 20% per tube")
    print("Built body + 4 caps + 4 channel washers + 4 backers")
