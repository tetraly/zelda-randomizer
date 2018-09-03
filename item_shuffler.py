import random
from typing import Dict, List, Tuple, Iterable
from constants import Item, LevelNum, Range, RoomNum


class ItemShuffler(object):

  ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS = [Item(0x16), Item(0x17), Item(0x1B)]
  NUM_LEVELS = 9

  # NUM_ITEM_TYPES = Item(0x20)

  def __init__(self) -> None:
    self.per_level_item_location_lists: Dict[LevelNum, List[RoomNum]] = {}
    self.item_num_list: List[Item] = []
    self.per_level_item_lists: Dict[LevelNum, List[Item]] = {}
    self.seed: int = None

  def AddLocationAndItem(self, level_num: LevelNum, room_num: RoomNum, item_num: Item) -> None:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    assert item_num in Range.VALID_ITEMS
    assert room_num in Range.VALID_ROOM_NUMBERS
    if item_num == Item.NO_ITEM:
      return

    if level_num not in self.per_level_item_location_lists:
      self.per_level_item_location_lists[level_num] = []
    self.per_level_item_location_lists[level_num].append(room_num)
    if item_num in self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS:
      return
    self.item_num_list.append(item_num)

  def ShuffleItems(self) -> None:
    random.shuffle(self.item_num_list)
    for level_num in Range.VALID_LEVEL_NUMBERS:
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
