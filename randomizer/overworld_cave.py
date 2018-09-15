from typing import List
from randomizer.constants import Item


class Cave(object):
  def __init__(self, raw_data: List[int]) -> None:
    self.raw_data = raw_data

  def GetItemAtPosition(self, position_num: int) -> Item:
    return Item(self.raw_data[position_num - 1] & 0x3F)

  def SetItemAtPosition(self, item: Item, position_num: int) -> None:
    part_not_to_change = self.raw_data[position_num - 1] & 0xC0  # The two highest bits
    self.raw_data[position_num - 1] = part_not_to_change + int(item)

  def GetItemData(self) -> List[int]:
    assert len(self.raw_data[0:3]) == 3
    return self.raw_data[0:3]

  def GetPriceData(self) -> List[int]:
    assert len(self.raw_data[3:6]) == 3
    return self.raw_data[3:6]
