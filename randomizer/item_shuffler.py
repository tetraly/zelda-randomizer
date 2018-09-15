from collections import defaultdict
from random import shuffle
from typing import DefaultDict, List, Tuple, Iterable
from randomizer.constants import Item, LevelOrCaveNum, LevelNum, RoomOrPositionNum, Range, RoomNum


class ItemShuffler():
  def __init__(self) -> None:
    self.item_num_list: List[Item] = []
    self.per_level_item_location_lists: DefaultDict[LevelNum, List[RoomNum]] = defaultdict(list)
    self.per_level_item_lists: DefaultDict[LevelNum, List[Item]] = defaultdict(list)

  def ResetState(self):
    self.item_num_list.clear()
    self.per_level_item_location_lists.clear()
    self.per_level_item_lists.clear()

  def AddLocationAndItem(self, level_or_cave_num: LevelOrCaveNum,
                         room_or_position_num: RoomOrPositionNum, item_num: Item) -> None:
    assert (level_or_cave_num in Range.VALID_LEVEL_NUMBERS
            or level_or_cave_num in Range.VALID_CAVE_NUMBERS)
    if level_or_cave_num in Range.VALID_CAVE_NUMBERS:
      assert room_or_position_num in range(1, 4)
    else:
      assert room_or_position_num in Range.VALID_ROOM_NUMBERS
    assert item_num in Range.VALID_ITEM_NUMBERS
    if item_num == Item.TRIFORCE_OF_POWER:
      return

    self.per_level_item_location_lists[level_or_cave_num].append(room_or_position_num)
    if item_num in [Item.MAP, Item.COMPASS, Item.TRINGLE]:
      return
    self.item_num_list.append(item_num)

  def ShuffleItems(self) -> None:
    shuffle(self.item_num_list)
    for level_num in Range.VALID_LEVEL_NUMBERS:
      # Levels 1-8 get a map, compass, and tringle.  Level 9 just gets a map and compass
      if level_num in range(1, 10):
        self.per_level_item_lists[level_num] = [Item.MAP, Item.COMPASS]
      if level_num in range(1, 9):
        self.per_level_item_lists[level_num].append(Item.TRINGLE)

      num_locations_needing_an_item = len(self.per_level_item_location_lists[level_num])
      while num_locations_needing_an_item > 0:
        self.per_level_item_lists[level_num].append(self.item_num_list.pop())
        num_locations_needing_an_item = num_locations_needing_an_item - 1

      if level_num in range(1, 10):  # Technically this could be for OW and caves too
        shuffle(self.per_level_item_lists[level_num])
    assert not self.item_num_list

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[LevelOrCaveNum, RoomOrPositionNum, Item]]:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      for room_num, item_num in zip(self.per_level_item_location_lists[level_num],
                                    self.per_level_item_lists[level_num]):
        yield (level_num, room_num, item_num)
