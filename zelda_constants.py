from typing import NewType
from enum import IntEnum

LevelNum = int
RoomNum = NewType('RoomNum', int)


class Direction(IntEnum):
  NORTH = RoomNum(-0x10)
  SOUTH = RoomNum(0x10)
  UP = RoomNum(0x00)
  DOWN = RoomNum(0x00)
  WEST = RoomNum(-0x1)
  EAST = RoomNum(0x1)


class Enemy(IntEnum):
  GOHMA_BLUE = 0x33
  GOHMA_RED = 0x34
  DIGDOGGER_TRIPLE = 0x38
  DIGDOGGER_SINGLE = 0x39


class Item(IntEnum):
  RECORDER = 0x05
  BOW = 0x0A
  RAFT = 0x0C
  LADDER = 0x0D
  COMPASS = 0x16
  MAP = 0x17
  HEART_CONTAINER = 0x1A
  TRINGLE = 0x1B


class RoomType(IntEnum):
  PLAIN_ROOM = 0x00
  SPIKE_TRAP_ROOM = 0x01
  FOUR_SHORT_ROOM = 0x02
  FOUR_TALL_ROOM = 0x03
  AQUAMENTUS_ROOM = 0x04
  GLEEOK_ROOM = 0x05
  REVERSE_C = 0x08  #Stairway
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


class WallType(IntEnum):
  OPEN_DOOR = 0
  SOLID_WALL = 1
  WALK_THROUGH_WALL_1 = 2
  WALK_THROUGH_WALL_1 = 3
  BOMB_HOLE = 4
  LOCKED_DOOR_1 = 5
  LOCKED_DOOR_2 = 6
  SHUTTER_DOOR = 7


ENEMY_NAME = {
    0x00: "",
    0x01: "B Lynel",
    0x02: "R Lynel",
    0x03: "B Moblin",
    0x04: "R Moblin",
    0x05: "B Grya",
    0x06: "R Grya",
    0x07: "R Octr",
    0x08: "R Octr",
    0x09: "B Octr",
    0x0A: "B Octr",
    0x0B: "R Drkn",
    0x0C: "B Drkn",
    0x0D: "B Tekt",
    0x0E: "R Tekt",
    0x0F: "B Levr",
    0x10: "R Levr",
    0x11: "Zola",
    0x12: "Vire",
    0x13: "Zol",
    0x14: "?14?",
    0x15: "Gel",
    0x16: "PolVoi",
    0x17: "LikeLk",
    0x18: "?18?",
    0x19: "?19?",
    0x1A: "Peahat",
    0x1B: "Keese",
    0x1C: "Keese",
    0x1D: "Keese",
    0x1E: "1E??",
    0x1F: "Rocks",
    0x20: "Rocks",
    0x21: "Ghini",
    0x22: "Ghini",
    0x23: "B Wizz",
    0x24: "R Wizz",
    0x25: "25??",
    0x26: "26??",
    0x27: "WallM",
    0x28: "Rope",
    0x29: "??29",
    0x2A: "Stalfs",
    0x2B: "Bubble",
    0x2C: "Bubble",
    0x2D: "Bubble",
    0x2E: "Traps",
    0x2F: "Fairy",
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
    0x3F: "3F??",
}

MIX_ENEMY_NAME = {
    0x03: "2Gleeok",
    0x04: "3Gleeok",
    0x05: "4Gleeok",
    0x07: "Patra21",
    0x08: "Patra2",
    0x0B: "Hint",
    0x09: "6 Traps",
    0x0A: "Traps",
    0x0D: "Old Man",
    0x0C: "Old Man",
    0x0E: "Old Man",
    0x0F: "Old Man",
    0x10: "Old Man",
    0x11: "LeaveOne",
    0x22: "Moblins",
    0x23: "Moblins",
    0x24: "Lynels+Lv",
    0x25: "Lynels",
    0x26: "Lynels+Lv",
    0x27: "Pea+Lever",
    0x28: "B+R Octs",
    0x29: "Octorcks",
    0x2A: "Octorcks",
    0x2B: "Octorcks",
    0x2C: "Oct+Mobl",
    0x2D: "Trp+Gel",
    0x2E: "Trp+Kees",
    0x2F: "Bbl+Gel",
    0x30: "Gib+PlV",
    0x31: "Bbl+Wizz",
    0x32: "Bbl+Vire",
    0x33: "BblZolLL",
    0x34: "Dknt+Gib",
    0x35: "K+BblGor",
    0x36: "Trp+Lklk",
    0x37: "Trp+Wizz",
    0x38: "Dknt+PlV",
    0x39: "BblWallM",
    0x3A: "R+B Dknt",
    0x3B: "R+B Wizz",
    0x3C: "LLBblWiz"
}
