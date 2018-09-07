from absl import logging
from constants import TextSpeed
from rom import Rom


class TextDataTable(object):
  TEXT_SPEED_ADDRESS = 0x481D

  def __init__(self, rom: Rom) -> None:
    self.rom = rom

  def WriteTextSpeedToRom(self, text_speed: TextSpeed):
    logging.debug("Updating text speed.")
    self.rom.WriteByte(address=self.TEXT_SPEED_ADDRESS, data=int(text_speed))
