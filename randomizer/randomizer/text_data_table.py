import random
from typing import List
from absl import logging

from .constants import TextSpeed
from .patch import Patch


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

  def GetPatch(self) -> Patch:
    self._AddTextSpeedToPatchIfNeeded()
    self._AddLevelNameToPatchIfNeeded()
    self._ChangeTextForMessage(
        "_____WELCOME TO THE|___QUEERING OF ZELDA!",
        0, 0x7770)
    self._ChangeTextForMessage(
        "___ARE YOU GAY ENOUGH|_______FOR THIS?",
        1, 0x77A0)
    self._ChangeTextForMessage(
        "__I'LL SUPPORT YOU NO|____MATTER WHAT PATH|_____YOU TAKE, LINK!",
        2, 0x77D0)
    self._ChangeTextForMessage(
        "__GENDER IS NOT BINARY|___BUT THIS CHOICE IS",
        16, 0x7820)
    return self.patch

  def _ChangeTextForMessage(
      self, text: str, pointer_index: int,
      text_writing_address: int) -> None:
    self.patch.AddData(text_writing_address,
                       self._ConvertTextToHex(text))

    pointer_address = self.BASE_POINTER_ADDRESS + 2 * pointer_index

    # Bank 1 in the ROM is from 0x4000 - 0x7FFF.  But when swapped
    # into NES memory, add 0x4000 since it'll be in 0x8000 - 0xBFFF
    pointer_value = text_writing_address + 0x4000 - 0x10

    pointer_value_high_byte = int(pointer_value / 0x100)
    pointer_value_low_byte = pointer_value % 0x100
    self.patch.AddData(
        pointer_address,
        [pointer_value_low_byte, pointer_value_high_byte])

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
      print("Hex value is: %02x" % hex_val)
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
