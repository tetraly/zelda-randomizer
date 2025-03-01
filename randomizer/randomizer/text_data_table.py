import logging
import random
from typing import List

from .patch import Patch


class TextDataTable():
  TEXT_SPEED_ADDRESS = 0x482D
  TEXT_LEVEL_ADDRESS = 0x19D17

  def __init__(self, text_speed: str, phrase: str) -> None:
    self.patch = Patch()
    self.text_speed = text_speed
    self.phrase = phrase

  def GetPatch(self) -> Patch:
    self._AddTextSpeedToPatchIfNeeded()
    self._AddLevelNameToPatchIfNeeded()
    return self.patch

  def _AddTextSpeedToPatchIfNeeded(self) -> None:
    logging.debug("Updating text speed.")

    if self.text_speed == 'normal':
      return
    self.patch.AddData(self.TEXT_SPEED_ADDRESS, [2])

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
