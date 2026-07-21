"""SM64 retail constants from n64decomp/sm64 (matching US/JP engine).

These match cartridge behavior when the ROM is bit-identical retail.
Research here supports console-first TAS: no emu-only assumptions.

Sources:
  include/types.h — Collision / TerrainData = s16
  src/engine/surface_collision.h — LEVEL_BOUNDARY_MAX, CELL_SIZE
  src/game/mario_actions_airborne.c — air drag / accel
  src/game/mario.c — ACT_LONG_JUMP 1.5× (BLJ)
  src/game/mario_step.c — 4 quarter-steps per frame
"""

# --- Collision lattice (Parallel Universes) ---
# find_floor / find_ceil cast f32 pos → TerrainData (s16) before cell lookup.
S16_MIN = -32768
S16_MAX = 32767
PU_SIZE = 65536  # 2**16 — one parallel-universe cell on X or Z
QPU_SIZE = 262144  # 2**18 — four PUs (common TAS speed lattice)

LEVEL_BOUNDARY_MAX = 0x2000  # 8192 — OOB reject for s16-cast coords
CELL_SIZE = 0x400  # 1024
NUM_CELLS = 2 * LEVEL_BOUNDARY_MAX // CELL_SIZE  # 16

FLOOR_LOWER_LIMIT = -11000.0

# --- Air / long jump ---
AIR_DRAG_THRESHOLD_NORMAL = 32.0
AIR_DRAG_THRESHOLD_LONG_JUMP = 48.0
AIR_APPROACH_ZERO = 0.35  # approach_f32 toward 0 each frame (both dirs)
AIR_ACCEL_FACTOR = 1.5  # * intendedMag * cos(dYaw)
AIR_NEG_SPEED_RECOVERY = 2.0  # if forwardVel < -16, add 2/frame
AIR_NEG_SPEED_THRESHOLD = -16.0
LONG_JUMP_SPEED_MULT = 1.5  # applied on entering ACT_LONG_JUMP
LONG_JUMP_POS_CAP = 48.0  # only if forwardVel > 48 AFTER mult (positive only!)
LONG_JUMP_Y_VEL = 30.0

# --- Quarter steps ---
QUARTER_STEPS_PER_FRAME = 4  # air and ground

# --- Squish (INPUT_SQUISHED) ---
# mario.c: dynamic floor OR dynamic ceil, and 0 <= ceil-floor <= 150
SQUISH_CEIL_FLOOR_MAX = 150.0
SQUISH_UNSQUISH_SPACE = 160.0  # act_squished state 0 → idle if space > 160
SQUISH_STEEP_PUSH = 10.0  # units/frame push along steep floor/ceil normal
SQUISH_STEEP_FLOOR_Y = 0.5  # floor normal.y < 0.5
SQUISH_STEEP_CEIL_Y = -0.5  # ceil normal.y > -0.5

# --- Game timing ---
GAMEPLAY_FPS = 30  # logic frames (VI often 60)
VI_PER_FRAME = 2  # typical NTSC

# --- Wall punch (clock punch class) ---
# Punch checks a point 50 units in front of Mario; connects if within 5 of wall.
PUNCH_PROBE_DIST = 50.0
PUNCH_CONNECT_RADIUS = 5.0
