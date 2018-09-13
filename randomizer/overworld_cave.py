from typing import List
from randomizer.constants import Item

class Cave(object):
  def __init__(self, raw_data: List[int]) -> None:
    self.raw_data = raw_data
    
  def GetItemAtPosition(self, position_num: int) -> Item:
    return self.raw_data[position_num] & 0x3F

