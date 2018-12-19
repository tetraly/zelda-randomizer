from typing import Dict, List
from .constants import ScreenCode
import logging

log = logging.getLogger(__name__)


# Add comment here about how byte 4 (zero-indexed) is skipped
class Screen():
  def __init__(self, rom_data: List[int]) -> None:
    assert len(rom_data) == 5
    self.rom_data = rom_data
    self.has_visit_mark = False

  def MarkAsVisited(self) -> None:
    self.has_visit_mark = True

  def IsMarkedAsVisited(self) -> bool:
    return self.has_visit_mark

  def GetRomData(self) -> List[int]:
    return self.rom_data

  def HasEntrance(self) -> bool:
    # Special thing -- it's 4 not 5 because of the missing cave data
    second_quest_only = self.rom_data[4] & 0x80 > 0
    return not second_quest_only and (self.rom_data[1] & 0xFC) >> 2 > 0

  def GetEntrance(self) -> int:
#    log.warning("rom_data[1] is %x" % self.rom_data[1])
#    log.warning("rom_data[1] & 0xFC is ...")
#    log.warning(self.rom_data[1] & 0xFC)
#    log.warning("(rom_data[1] & 0xFC) >> 2 is")
#    log.warning((self.rom_data[1] & 0xFC) >> 2)
    
    return (self.rom_data[1] & 0xFC) >> 2

  def GetScreenCode(self) -> ScreenCode:
    return self.rom_data[3] & 0x7F
