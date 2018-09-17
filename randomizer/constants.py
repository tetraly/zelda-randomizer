from typing import NewType
from enum import IntEnum

LevelNum = int
CaveNum = int
RoomNum = NewType("RoomNum", int)
PositionNum = NewType("PositionNum", int)


class Range():
  VALID_ROOM_NUMBERS = range(0, 0x80)  # 128 rooms (0-indexed)
  VALID_ROOM_TABLE_NUMBERS = range(0, 6)  # Six tables (0-indexed)
  VALID_LEVEL_NUMBERS = range(1, 10)  # Levels 1-9 (1-indexed)
  VALID_LEVEL_AND_CAVE_NUMBERS = range(1, 11)  # L1-9 plus L10 repreenting OW caves (1-indexed)
  VALID_ITEM_NUMBERS = range(0, 0x20)
  VALID_CAVE_NUMBERS = range(0, 22)  # Includes 20 actual +2 virtual caves 0-19, 20-21.
  VALID_CAVE_POSITION_NUMBERS = range(1, 4)  # Three possible positions per cave (1-indexed)


class Direction(IntEnum):
  NORTH = -0x10
  SOUTH = 0x10
  UP = 0x00
  DOWN = 0x00
  WEST = -0x1
  EAST = 0x1


class Item(IntEnum):
  BOMBS = 0x00
  WOOD_SWORD = 0x01
  WHITE_SWORD = 0x02
  MAGICAL_SWORD = 0x03
  NO_ITEM = 0x03
  BAIT = 0x04
  RECORDER = 0x05
  BLUE_CANDLE = 0x06
  RED_CANDLE = 0x07
  WOOD_ARROWS = 0x08
  SILVER_ARROWS = 0x09
  BOW = 0x0A
  ANY_KEY = 0x0B
  RAFT = 0x0C
  LADDER = 0x0D
  TRIFORCE_OF_POWER = 0x0E
  FIVE_RUPEES = 0x0F
  WAND = 0x10
  BOOK = 0x11
  BLUE_RING = 0x12
  RED_RING = 0x13
  POWER_BRACELET = 0x14
  LETTER = 0x15
  COMPASS = 0x16
  MAP = 0x17
  RUPEE = 0x18
  KEY = 0x19
  HEART_CONTAINER = 0x1A
  TRINGLE = 0x1B
  WHAT_IS_THIS = 0x1C
  LORD_BANANA = 0x1D
  INFERIOR_MODEL = 0x1E
  BLUE_POTION = 0x1F


class RoomType(IntEnum):
  PLAIN_ROOM = 0x00
  SPIKE_TRAP_ROOM = 0x01
  FOUR_SHORT_ROOM = 0x02
  FOUR_TALL_ROOM = 0x03
  AQUAMENTUS_ROOM = 0x04
  GLEEOK_ROOM = 0x05
  TODO_____NEED_TO_FIGURE_OUT_WHAT_THIS_IS = 0x06
  TODO_____NEED_TO_FIGURE_OUT_WHAT_THIS_IS_ = 0x07
  REVERSE_C = 0x08  #Stairway
  TODO_____NEED_TO_FIGURE_OUT_WHAT_THIS_IS__ = 0x09
  DOUBLE_BLOCK = 0x0A  # Stairway
  MAZE_ROOM = 0x0C
  GRID_ROOM = 0x0D
  VERTICAL_CHUTE_ROOM = 0x0E
  HORIZONTAL_CHUTE_ROOM = 0x0F
  ZIGZAG_ROOM = 0x11
  T_ROOM = 0x12
  VERTICAL_MOAT_ROOM = 0x13
  CIRCLE_MOAT_ROOM = 0x14
  POINTLESS_MOAT_ROOM = 0x15
  CHEVY_ROOM = 0x16
  NSU = 0x17
  HORIZONTAL_MOAT_ROOM = 0x18
  DOUBLE_MOAT_ROOM = 0x19
  DIAMOND_STAIR_ROOM = 0x1A
  NARROW_STAIR_ROOM = 0x1B  #stair
  SPIRAL_STAIR_ROOM = 0x1C  # stair
  DOUBLE_SIX_BLOCK_ROOM = 0x1D
  SINGLE_SIX_BLOCK_ROOM = 0x1E
  FIVE_PAIR_ROOM = 0x1F
  ENTRANCE_ROOM = 0x21  # stair
  SINGLE_BLOCK_ROOM = 0x22
  TWO_FIREBALL_ROOM = 0x23
  FOUR_FIREBALL_ROOM = 0x24
  BLANK_ROOM_5 = 0x25
  OLD_MAN_ROOM = 0x26
  ZELDA_ROOM = 0x27
  GANNON_ROOM = 0x28
  TRIFORCE_ROOM = 0x29
  TRANSPORT_STAIRCASE = 0x3E
  ITEM_STAIRCASE = 0x3F


class Enemy(IntEnum):
  GOHMA_BLUE = 0x33
  GOHMA_RED = 0x34
  DIGDOGGER_TRIPLE = 0x38
  DIGDOGGER_SINGLE = 0x39
  BLUE_GORIYA = 0x05
  RED_GORIYA = 0x06
  RED_DARKNUT = 0x0B
  BLUE_DARKNUT = 0x0C
  """0x12: "Vire",
    0x13: "Zol",
    0x15: "Gel",
    0x16: "PolVoi",
    0x17: "LikeLk",
    0x1B: "Keese",
    0x1C: "Keese",
    0x1D: "Keese",
    0x23: "B Wizz",
    0x24: "R Wizz",
    0x27: "WallM",
    0x28: "Rope",
    0x2A: "Stalfs",
    0x2B: "Bubble",
    0x2C: "Bubble",
    0x2D: "Bubble",
    0x2E: "Traps",
    0x30: "Gibdo",
    0x31: "Dodong",
    0x32: "Dodong",
    0x33: "BGohma",
    0x34: "RGohma",
    0x35: "RupeeB",
    0x36: "Hungry",
    0x37: "Zelda",
    0x38: "DigDog",  # The one in vanilla 7
    0x39: "DigDog",
    0x3A: "R Lanm",
    0x3B: "B Lamn",
    0x3C: "Manhnd",
    0x3D: "Aquamn",
    0x3E: "Gannon",
}"""


class WallType(IntEnum):
  OPEN_DOOR = 0
  SOLID_WALL = 1
  WALK_THROUGH_WALL_1 = 2
  WALK_THROUGH_WALL_2 = 3
  BOMB_HOLE = 4
  LOCKED_DOOR_1 = 5
  LOCKED_DOOR_2 = 6
  SHUTTER_DOOR = 7


class TextSpeed(IntEnum):
  VERY_FAST = 2
  FAST = 4
  NORMAL = 6
  SLOW = 8
  VERY_SLOW = 10
