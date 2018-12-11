from typing import Dict, List
import logging

log = logging.getLogger(__name__)


class Screen():

  def __init__(self, rom_data: List[int]) -> None:
    self.rom_data = rom_data

  def GetRomData(self) -> List[int]:
    return self.rom_data
