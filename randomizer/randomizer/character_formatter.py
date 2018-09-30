from enum import IntEnum


class NpcNextCharacterFormatter(IntEnum):
  NONE = 0x00
  LINE_2 = 0x40
  LINE_3 = 0x80
  END = 0xC0
