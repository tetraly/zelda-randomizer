from typing import List
from randomizer.constants import Item, PositionNum

class Cave(object):
  def __init__(self, raw_data: List[int]) -> None:
    self.raw_data = raw_data
    
  def GetItemAtPosition(self, position_num: PositionNum) -> Item:
    return Item(self.raw_data[position_num] & 0x3F)

  def SetItemAtPosition(self, item: Item, position_num: PositionNum) -> None:
    pass