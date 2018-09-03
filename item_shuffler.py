import random
from typing import Dict, List, Tuple, Iterable
from zelda_constants import Item, LevelNum, RoomNum


class ItemShuffler(object):

  NO_ITEM_NUMBER = Item(0x03)  # Actually code for mags, but that's how they did it!
  # Compass, map, tringle
  ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS = [Item(0x16), Item(0x17), Item(0x1B)]
  NUM_LEVELS = 9
  NUM_ITEM_TYPES = Item(0x20)
  NUM_ROOMS_PER_TABLE = RoomNum(0x80)

  def __init__(self) -> None:
    self.per_level_item_location_lists: Dict[LevelNum, List[RoomNum]] = {}
    self.item_num_list: List[Item] = []
    self.per_level_item_lists: Dict[LevelNum, List[Item]] = {}
    self.seed: int = None

  def AddLocationAndItem(self, level_num: LevelNum, room_num: RoomNum, item_num: Item) -> None:
    assert level_num in range(1, self.NUM_LEVELS + 1)
    assert item_num in range(0, self.NUM_ITEM_TYPES)
    assert room_num in range(0, self.NUM_ROOMS_PER_TABLE)
    if item_num == self.NO_ITEM_NUMBER:
      return

    if level_num not in self.per_level_item_location_lists:
      self.per_level_item_location_lists[level_num] = []
    self.per_level_item_location_lists[level_num].append(room_num)
    if item_num in self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS:
      return
    self.item_num_list.append(item_num)

  def ShuffleItems(self) -> None:
    random.shuffle(self.item_num_list)
    for level_num in range(1, self.NUM_LEVELS + 1):
      self.per_level_item_lists[level_num] = []
      self.per_level_item_lists[level_num].extend(self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS)
      while (len(self.per_level_item_location_lists[level_num]) > len(
          self.per_level_item_lists[level_num])):
        tmp = self.item_num_list.pop()
        self.per_level_item_lists[level_num].append(tmp)
      random.shuffle(self.per_level_item_lists[level_num])

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[LevelNum, RoomNum, Item]]:
    for level_num in range(1, self.NUM_LEVELS + 1):
      for room_num, item_num in zip(self.per_level_item_location_lists[level_num],
                                    self.per_level_item_lists[level_num]):
        yield (level_num, room_num, item_num)
