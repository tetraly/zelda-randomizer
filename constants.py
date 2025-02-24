from enum import IntEnum
from typing import Dict

CHAR_MAP = {
  0x00: "0",
  0x01: "1",
  0x02: "2",
  0x03: "3",
  0x04: "4",
  0x05: "5",
  0x06: "6",
  0x07: "7",
  0x08: "8",
  0x09: "9",
  0x0A: "A",
  0x0B: "B",
  0x0C: "C",
  0x0D: "D",
  0x0E: "E",
  0x0F: "F",
  0x10: "G",
  0x11: "H",
  0x12: "I",
  0x13: "J",
  0x14: "K",
  0x15: "L",
  0x16: "M",
  0x17: "N",
  0x18: "O",
  0x19: "P",
  0x1A: "Q",
  0x1B: "R",
  0x1C: "S",
  0x1D: "T",
  0x1E: "U",
  0x1F: "V",
  0x20: "W",
  0x21: "X",
  0x22: "Y",
  0x23: "Z",
  0x24: " ",
  0x25: "",
  0x28: ",",
  0x29: "!",
  0x2A: "'",
  0x2B: "&",
  0x2C: '.',
  0x2D: "\"",
  0x2E: "?",
  0x2F: "-",
  0x3F: " ",
  0xFF: " ",
}

OVERWORLD_BLOCK_TYPES = {
  0x00: "Bomb",  # 2nd quest level 9
  0x01: "Bomb",
  0x02: "Bomb", #2nd quest only
  0x03: "Bomb",
  0x04: "Open",
  0x05: "Bomb", # 1st quest level 9
  0x06: "Recorder", #2nd quest only
  0x07: "Bomb", 
  0x09: "Power Bracelet", #2nd quest only
  0x0A: "Open",
  0x0B: "Open",
  0x0C: "Open",
  0x0D: "Bomb",
  0x0E: "Open",
  0x0F: "Open",  # 1st quest 100 secret
  0x10: "Bomb",  
  0x11: "Power Bracelet", # 2nd quest letter cave
  0x12: "Bomb", 
  0x13: "Bomb",
  0x14: "Bomb",
  0x15: "Bomb", # 2nd quest only
  0x16: "Bomb", 
  0x18: "Ladder+Bomb", #  quest only
  0x19: "Ladder+Bomb", # 2nd quest only
  0x1A: "Open",
  0x1B: "Power Bracelet", # 2nd quest only
  0x1C: "Open",
  0x1D: "Power Bracelet",
  0x1E: "Bomb",
  0x1F: "Open",
  0x20: "Open",  # 2nd quest Grave block
  0x21: "Open", # 1st quest Grave block
  0x22: "Open", # 1Q6
  0x23: "Power Bracelet",
  0x24: "Open",
  0x25: "Open",
  0x26: "Bomb", # forgotten spot
  0x27: "Bomb", # 1st quest only
  0x28: "Candle",
  0x29: "Recorder", #2nd quest only
  0x2B: "Recorder", #2nd quest only
  0x2C: "Bomb",  # 1st quest only
  0x2D: "Bomb",
  0x2F: "Raft",
  0x30: "Recorder",  # 2nd quest level 6
  0x33: "Bomb",
  0x34: "Open",
  0x37: "Open", 
  0x3A: "Recorder",  # 2nd quest only
  0x3C: "Recorder",  # 2nd quest level 3
  0x3D: "Open",
  0x42: "Recorder", # 1st quest level 7
  0x44: "Open",
  0x45: "Raft", # 1st quest level 4
  0x46: "Candle", 
  0x47: "Candle",  # 1st quest only 
  0x48: "Candle", 
  0x49: "Power Bracelet", 
  0x4A: "Open",
  0x4B: "Candle",
  0x4D: "Candle",
  0x4E: "Open",
  0x51: "Candle",
  0x53: "Candle",  # 2nd quest only
  0x56: "Candle", 
  0x58: "Recorder",  # 2nd quest only
  0x5B: "Candle",
  0x5E: "Open",
  0x60: "Recorder",  # 2nd quest onlye
  0x62: "Candle", # 1st quest only
  0x63: "Candle",
  0x64: "Open",
  0x66: "Open", 
  0x67: "Bomb",  # 1st quest only 
  0x68: "Candle", 
  0x6A: "Candle",
  0x6B: "Candle",  # 1st quest only
  0x6C: "Candle",  # 2nd quest only
  0x6D: "Candle",  # 1st quest only
  0x6E: "Recorder",  # 2nd quest only
  0x6F: "Open", 
  0x70: "Open", 
  0x71: "Bomb",  # 1st quest only
  0x72: "Recorder", #2nd quest only
  0x74: "Open",
  0x75: "Open",
  0x76: "Bomb",
  0x77: "Open", 
  0x78: "Candle", 
  0x79: "Power Bracelet",
  0x7B: "Bomb",  # 1st quest only
  0x7C: "Bomb",
  0x7D: "Bomb",
}

class Direction(IntEnum):
  NORTH = -0x10
  WEST = -0x1
  NO_DIRECTION = 0
  EAST = 0x1
  SOUTH = 0x10
  
ENTRANCE_DIRECTION_MAP: Dict[int, Direction] = {
  1: Direction.NORTH,
  2: Direction.SOUTH,
  3: Direction.WEST,
  4: Direction.EAST
}