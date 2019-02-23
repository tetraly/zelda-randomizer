import random
from typing import List
from absl import logging

from .constants import TextSpeed
from .patch import Patch


NEW_QUOTES = [
  (0x4000, "_____WILL_THIS_BE_A_____|___LOZ_APPROVED_SEED?___"),
  (0x4002, "______AND_THERE_IS______|______YOUR_DAGGER!______"),
  (0x4004, "__THERE'S_NEVER_A_CAB___|___WHEN_YOU_WANT_ONE____"),
  (0x400C, "____I_NEVER_LEARNED_____|________TO_READ_________"),
  (0x4010, "__HAVE A DRINK, EDDIE___"),
  (0x401C, "___SHOP_'TIL_YOU_DROP___"),
  (0x401E, "_ONCE_YOU_BUY_A_PRIZE,__|__IT'S_YOURS_TO_KEEP!___"),
  (0x4020, "_ARE_YOU_GOING_TO_PASS__|__OR_PRESS_YOUR_LUCK?___"),
  (0x4022, "_THIS DONATION GOES TO__|____RUNNER'S CHOICE_____"),
  (0x4024, "_____WOULD YOU LIKE_____|____FRIES WITH THAT?____"),
  (0x4028, "___THE_SILVER_TO_KILL___|___THE_BEAST_LIES_IN_A__|____PRE-1965_QUARTER____"),
  (0x402A, "___WELCOME_TO_LEVEL_3___|_____SIMULATOR_2019_____"),
  (0x402C, "_____TETRA_WAS_HERE_____"),
  (0x0000, "_____THE_GAME_KNOWS_____"),
  (0x4032, "____I'M_BOMB_BARKER_____|_PLEASE_REMEMBER_TO_SPAY|__OR_NEUTER_YOUR_PETS.__"),
  (0x4048, "_____WELCOME_TO_THE_____|_____GREAT_EQUALIZER____"),
  (0x4038, "FOR_255_RUPEES,_HERE_IS_|YOUR_FIRST_SUBJECT._GO!_"),
  (0x4042, "FOR_255_RUPEES,_HERE_IS_|YOUR_FIRST_SUBJECT._GO!_"),
]

class TextDataTable():
  BASE_POINTER_ADDRESS = 0x4010  # Includes 16-byte NES header
  TEXT_SPEED_ADDRESS = 0x482D
  TEXT_LEVEL_ADDRESS = 0x19D17
  LINE_CODES = {1: 128, 2: 64, 3: 192}

  def __init__(self, text_speed: str, phrase: str,
               custom_text: bool=False) -> None:
    self.patch = Patch()
    self.text_speed = text_speed
    self.phrase = phrase
    self.custom_text = custom_text
    self.next_writeable_byte_addr = 0x7770

  def GetPatch(self) -> Patch:
    self._AddTextSpeedToPatchIfNeeded()
    self._AddLevelNameToPatchIfNeeded()
    for (pointer_addr, quote) in NEW_QUOTES:
      self._ChangeTextForMessage(pointer_addr, quote)

    # Replace 4 8x8 Zelda sprites with SMB2 Luigi sprites
    self.patch.AddData(0xEAEB, [0x00, 0x07, 0x1F, 0x3F, 0x3F, 0xBF, 0xFA, 0xD2,
                                0x00, 0x07, 0x1C, 0xF0, 0xE3, 0x6F, 0x3F, 0xBF])
    self.patch.AddData(0xEAFB, [0x60, 0x26, 0x13, 0x0C, 0x0F, 0x1B, 0x3F, 0x7E,
                                0x7F, 0x3F, 0x1F, 0x0F, 0x06, 0x1F, 0x3F, 0x42])
    self.patch.AddData(0xEB4B, [0x00, 0x07, 0x1F, 0x3F, 0x3F, 0x3F, 0x3A, 0x52,
                                0x00, 0x07, 0x1C, 0x30, 0x23, 0x2F, 0x3F, 0x7F])
    self.patch.AddData(0xEB5B, [0x20, 0x26, 0x73, 0x4C, 0x4F, 0x1B, 0x3F, 0x7E,
                                0x3F, 0x3F, 0x5F, 0x7F, 0x76, 0x1F, 0x3F, 0x42])

    # Change "the hero of hyrule." to "cute. wanna cuddle?" after "Thank's Link, you're"
    self.patch.AddData(0xA97C, [0x0C, 0x1E, 0x1D, 0x0E, 0x2C, 0x24, 0x20, 0x0A, 0x17, 0x17, 0x0A,
                                0x24, 0x0C, 0x1E, 0x0D, 0x0D, 0x15, 0x0E, 0xEE])

    # Randomize HCs for white sword and mags.  This should really be done elsewhere.
    self.patch.AddData(0x490D, [random.choice([0x30, 0x40, 0x50])])
    self.patch.AddData(0x4916, [random.choice([0x70, 0x80, 0x90, 0xA0, 0xB0])])
    return self.patch

  def _ChangeTextForMessage(self, pointer_address: int, text: str) -> None:

    # Bank 1 in the ROM is from 0x4000 - 0x7FFF.  But when swapped
    # into NES memory, add 0x4000 since it'll be in 0x8000 - 0xBFFF
    pointer_value = self.next_writeable_byte_addr + 0x4000 - 0x10
    pointer_value_high_byte = int(pointer_value / 0x100)
    pointer_value_low_byte = pointer_value % 0x100
    self.patch.AddData(pointer_address + 0x10, [pointer_value_low_byte, pointer_value_high_byte])

    self.patch.AddData(self.next_writeable_byte_addr, self._ConvertTextToHex(text))
    self.next_writeable_byte_addr += (len(text) + 1)
    assert self.next_writeable_byte_addr < 0x7C88

  def _ConvertTextToHex(self, text: str) -> List[int]:
    to_be_returned: List[int] = []
    ptr = 0
    line = 1
    size = len(text)

    while ptr < size:
      hex_val = self._ascii_char_to_bytes(text[ptr])
      ptr += 1
      if ptr == size or text[ptr] == '|':
        assert line <= 3
        hex_val += self.LINE_CODES[line]
        ptr += 1
        line += 1
      to_be_returned.append(hex_val)
    return to_be_returned

  def _AddTextSpeedToPatchIfNeeded(self) -> None:
    logging.debug("Updating text speed.")

    converted_text_speed = TextSpeed.NORMAL
    if self.text_speed == 'normal':
      return
    elif self.text_speed == 'random':
      converted_text_speed = random.choice(list(TextSpeed))
    else:
      converted_text_speed = TextSpeed[self.text_speed.upper()]

    self.patch.AddData(self.TEXT_SPEED_ADDRESS, [int(converted_text_speed)])

  def _AddLevelNameToPatchIfNeeded(self) -> None:
    assert len(self.phrase) == 6, "The level prefix must be six characters long."
    if self.phrase.lower() == 'level-':
      return  # No need to replace the existing text with the same text.

    self.patch.AddData(self.TEXT_LEVEL_ADDRESS, self.__ascii_string_to_bytes(self.phrase))

  def __ascii_string_to_bytes(self, phrase: str) -> List[int]:
    """Convert the string to a form the game can understand."""
    return list(map(self._ascii_char_to_bytes, phrase))

  @staticmethod
  def _ascii_char_to_bytes(char: str) -> int:
    if ord(char) >= 48 and ord(char) <= 57:  # 0-9
      return ord(char) - 48
    if ord(char) >= 65 and ord(char) <= 90:  # A-Z
      return ord(char) - 55
    if ord(char) >= 97 and ord(char) <= 122:  # a-z
      return ord(char) - 87

    misc_char_map = {
        ' ': 0x24,
        '_': 0x24,  # Meant to represent a space.
        '~': 0x25,  # Meant to represent leading space.
        ',': 0x28,
        '!': 0x29,
        "'": 0x2A,
        '&': 0x2B,
        '.': 0x2C,
        '"': 0x2D,
        '?': 0x2E,
        '-': 0x2F
    }

    return misc_char_map[char] or misc_char_map['_']
