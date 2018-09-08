from absl import logging

from ..constants import TextSpeed
from ..rom import Rom
from .character_map import CharacterMap

class TextDataTable():
  TEXT_SPEED_ADDRESS = 0x481D
  TEXT_LEVEL_ADDRESS = 0x19D07

  def __init__(self, rom: Rom) -> None:
    self.rom = rom
    self.character_map = CharacterMap()

  def WriteTextSpeedToRom(self, text_speed: TextSpeed):
    logging.debug("Updating text speed.")
    self.rom.WriteByte(address=self.TEXT_SPEED_ADDRESS, data=int(text_speed))

  def WriteLevelNameToRom(self, phrase: str):
    self.rom.WriteBytes(
        address=self.TEXT_LEVEL_ADDRESS,
        data=self.character_map.single_line_to_bytes(phrase)
    )
