from typing import NewType

ItemNum = NewType('ItemNum', int)
LevelNum = int
RoomNum = NewType('RoomNum', int)


class Direction(object):
  NORTH = RoomNum(-0x10)
  SOUTH = RoomNum(0x10)
  WEST = RoomNum(-0x1)
  EAST = RoomNum(0x1)


DOOR_TYPES = {
    0: "Door",
    1: "Wall",
    2: "Walk-Through Wall",
    3: "Walk-Through Wall",
    4: "Bomb Hole",
    5: "Locked Door",
    6: "Locked Door",
    7: "Shutter Door",
}

WALL_TYPE_CHAR = {
    0: (" ", " "),
    1: ("-", "|"),
    2: ("=", "!"),
    3: ("=", "!"),
    4: ("B", "B"),
    5: ("K", "K"),
    6: ("K", "K"),
    7: ("S", "S"),
}

CAVE_BLOCK_TYPE = {
    0x00: "",  # No cave
    0x01: "OpenCave",
    0x02: "OpenPush",
    0x03: "Candle",
    0x04: "Bomb",
    0x05: "PowerBr",
    0x06: "Raft",
    0x07: "Recorder",
}

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

GOHMA_ENEMY_TYPES = [0x33, 0x34]
DIGDOGGER_ENEMY_TYPES = [0x38, 0x39]
HARD_COMBAT_ENEMY_TYPES = [0x0C, 0x23]

ROOM_TYPES = {
    0x00: "Empty",
    0x01: "2 3blk",
    0x02: "4 blk-",
    0x03: "4 Blk+",
    0x04: "AquaRoom",
    0x05: "GleeokRm",
    0x06: "?????6",
    0x07: "?????7",
    0x08: "Rev C",  #stairway
    0x09: "?????9",
    0x0A: "2blk",  #stairway
    0x0B: "?????B",
    0x0C: "Squiggly",
    0x0D: "lotsblks",
    0x0E: "|| Chute",
    0x0F: "== Chute",  # Block
    0x11: "DiagRoom",
    0x12: "T Room",  # Ladder
    0x13: "E River",  # Ladder
    0x14: "rvrmoat",
    0x15: "[--]",
    0x16: "Chevy",  # Ladder
    0x17: "NSU",
    0x18: "TopRivr",  # Ladder
    0x19: "= River",  # Ladder
    0x1A: "Diamond",  # Stairway
    0x1B: "Rstairs",  # Stairway
    0x1C: "Spiral",  # Stairway
    0x1D: "2 6blk",
    0x1E: "6blk",
    0x1F: "5 rects",
    0x21: "Entrance",
    0x22: "1 block",  #stairway
    0x23: "2 shoot",
    0x24: "4 shoot",
    0x25: "Empty",
    0x26: "BlackRm",
    0x27: "ZeldaRm",
    0x28: "GannonRm",
    0x29: "TriRoom",
}

ITEMS = {
    0x00: "Bombs",
    0x02: "White S",
    0x03: "NoItem",
    0x05: "Recrdr",
    0x07: "RCndle",
    0x09: "SArrow",
    0x0A: "Bow",
    0x0B: "Any Key",
    0x0C: "Raft",
    0x0D: "Ladder",
    0x0E: "Tforce",  # Big L9 triforce, not small tringle
    0x0F: "5Rupee",
    0x10: "Wand",
    0x11: "Book",
    0x12: "B Ring",
    0x13: "R Ring",
    0x14: "PowerB",
    0x16: "Cmpass",
    0x17: "Map",
    0x19: "Key",
    0x1A: "HeartC",
    0x1B: "Tringl",
    0x1C: "Shield",
    0x1D: "Banana",
    0x1E: "M Bmng",
}

SPECIAL_ITEMS = [
    0x02, 0x05, 0x07, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x10, 0x11, 0x13, 0x14, 0x1D, 0x1E
]
TRINGLE = 0x1B
RECORDER = 0x05
BOW = 0x0A
BLUE_RING = 0x12
RED_RING = 0x13
LADDER = 0x0D

DIAMOND_ROOM_TYPE = 0x1A
RIGHT_STAIRS_ROOM_TYPE = 0x1B
