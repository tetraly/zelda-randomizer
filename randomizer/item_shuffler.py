import random
from typing import Dict, List, Tuple, Iterable

from randomizer.constants import CaveNum, Item, LevelNum, Range, RoomNum


class ItemShuffler():
  def __init__(self) -> None:
    self.item_num_list: List[Item] = []
    self.per_level_item_location_lists: Dict[LevelNum, List[RoomNum]] = {}
    self.per_level_item_lists: Dict[LevelNum, List[Item]] = {}
    self.overworld_cave_item_locations: List[(CaveNum, CavePosition)] = []
    self.per_level_item_lists: Dict[LevelNum, Item] = {}

  def ResetState(self):
    self.overworld_cave_item_locations = []
    self.per_level_item_location_lists: Dict[LevelNum, List[RoomNum]] = {}
    self.item_num_list: List[Item] = []
    self.per_level_item_lists: Dict[LevelNum, List[Item]] = {}
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.per_level_item_location_lists[level_num] = []
      self.per_level_item_lists[level_num] = []

  def AddOverworldLocationAndItem(self, cave_num: CaveNum, position_num: CavePosition, item_num: Item) -> None:
    assert cave_num in Range.VALID_CAVE_NUMBERS
    assert item_num in Range.VALID_ITEM_NUMBERS
    assert position_num in Range.VALID_CAVE_POSITION_NUMBERS

    self.overworld_cave_item_locations.append((cave_num, position_num))
    self.item_num_list.append(item_num)


  def AddLocationAndItem(self, level_num: LevelNum, room_num: RoomNum, item_num: Item) -> None:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    assert item_num in Range.VALID_ITEM_NUMBERS
    assert room_num in Range.VALID_ROOM_NUMBERS
    if item_num == Item.NO_ITEM:
      return
    if item_num == Item.TRIFORCE_OF_POWER:
      return

    # TODO: A default dict might probably make sense here
    if level_num not in self.per_level_item_location_lists:
      self.per_level_item_location_lists[level_num] = []
    self.per_level_item_location_lists[level_num].append(room_num)
    if item_num in [Item.MAP, Item.COMPASS, Item.TRINGLE]:
      return
    self.item_num_list.append(item_num)

  def ShuffleItems(self) -> None:
    random.shuffle(self.item_num_list)      
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self.per_level_item_lists[level_num] = [Item.MAP, Item.COMPASS]
      if level_num != 9:
        self.per_level_item_lists[level_num].append(Item.TRINGLE)
      while (len(self.per_level_item_location_lists[level_num]) > len(
          self.per_level_item_lists[level_num])):
        tmp = self.item_num_list.pop()
        self.per_level_item_lists[level_num].append(tmp)
      random.shuffle(self.per_level_item_lists[level_num])

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[LevelNum, RoomNum, Item]]:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      for room_num, item_num in zip(self.per_level_item_location_lists[level_num],
                                    self.per_level_item_lists[level_num]):
        yield (level_num, room_num, item_num)
