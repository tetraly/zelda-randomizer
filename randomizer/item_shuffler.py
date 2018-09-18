from collections import defaultdict
from random import shuffle
from typing import DefaultDict, List, Tuple, Iterable
from randomizer.constants import Item, LevelNum, Range
from randomizer.location import Location


class ItemShuffler():
  def __init__(self) -> None:
    self.item_num_list: List[Item] = []
    self.per_level_item_location_lists: DefaultDict[LevelNum, List[Location]] = defaultdict(list)
    self.per_level_item_lists: DefaultDict[LevelNum, List[Item]] = defaultdict(list)

  def ResetState(self):
    self.item_num_list.clear()
    self.per_level_item_location_lists.clear()
    self.per_level_item_lists.clear()

  def AddLocationAndItem(self, location: Location, item_num: Item) -> None:
    if item_num == Item.TRIFORCE_OF_POWER:
      return
    level_num = location.GetLevelNum() if location.IsLevelRoom() else 10
    self.per_level_item_location_lists[level_num].append(location)
    if item_num in [Item.MAP, Item.COMPASS, Item.TRINGLE]:
      return
    self.item_num_list.append(item_num)

  def ShuffleItems(self) -> None:
    shuffle(self.item_num_list)
    for level_num in Range.VALID_LEVEL_AND_CAVE_NUMBERS:
      # Levels 1-8 get a tringle, map, and compass.  Level 9 only gets a map and compass.
      if level_num in Range.VALID_LEVEL_NUMBERS:
        self.per_level_item_lists[level_num] = [Item.MAP, Item.COMPASS]
      if level_num in range(1, 9):
        self.per_level_item_lists[level_num].append(Item.TRINGLE)

      num_locations_needing_an_item = len(self.per_level_item_location_lists[level_num]) - len(
          self.per_level_item_lists[level_num])

      while num_locations_needing_an_item > 0:
        self.per_level_item_lists[level_num].append(self.item_num_list.pop())
        num_locations_needing_an_item = num_locations_needing_an_item - 1

      if level_num in range(1, 10):  # Technically this could be for OW and caves too
        shuffle(self.per_level_item_lists[level_num])
    assert not self.item_num_list

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[Location, Item]]:
    for level_num in range(0, 11):
      for location, item_num in zip(self.per_level_item_location_lists[level_num],
                                    self.per_level_item_lists[level_num]):
        yield (location, item_num)
