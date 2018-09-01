from typing import Dict, List, Tuple, Iterable
import random
from zelda_constants import LevelNum, RoomNum, ItemNum


class ItemShuffler(object):

  NO_ITEM_NUMBER = ItemNum(0x03)  # Actually code for mags, but that's how they did it!
  # Compass, map, tringle
  ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS = [ItemNum(0x16), ItemNum(0x17), ItemNum(0x1B)]
  NUM_LEVELS = 9
  NUM_ITEM_TYPES = ItemNum(0x20)
  NUM_ROOMS_PER_TABLE = RoomNum(0x80)

  def __init__(self) -> None:
    self.item_locations = {}  # type: Dict[LevelNum, List[RoomNum]]
    self.item_num_list = []  # type: List[ItemNum]
    self.per_level_item_lists = {}  # type: Dict[LevelNum, List[ItemNum]]
    self.seed = None  # type: int

  def PrintLengths(self) -> None:  # For debugging
    print("item_num_list length: %d" % len(self.item_num_list))
    print(self.item_locations.keys())
    for level in range(1, self.NUM_LEVELS + 1):
      print("level %d item_location list length: %d" % (level, len(self.item_locations[level])))

    print(self.per_level_item_lists.keys())
    for level in range(1, self.NUM_LEVELS + 1):
      if level in self.per_level_item_lists:
        print("level %d per_level_item list length: %d" % (level,
                                                           len(self.per_level_item_lists[level])))

  def AddLocationAndItem(self, level_num: LevelNum, room_num: RoomNum, item_num: ItemNum) -> None:
    assert level_num in range(1, self.NUM_LEVELS + 1)
    assert item_num in range(0, self.NUM_ITEM_TYPES)
    assert room_num in range(0, self.NUM_ROOMS_PER_TABLE)
    if item_num == self.NO_ITEM_NUMBER:
      return
    if item_num in self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS:
      return

    if level_num not in self.item_locations:
      self.item_locations[level_num] = []
    self.item_locations[level_num].append(room_num)
    self.item_num_list.append(item_num)

  def ShuffleItems(self) -> None:
    self.PrintLengths()
    random.shuffle(self.item_num_list)
    for level_num in range(1, self.NUM_LEVELS + 1):
      if not level_num in self.per_level_item_lists:
        self.per_level_item_lists[level_num] = []
      self.per_level_item_lists[level_num].extend(self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS)
      for unused_location in self.item_locations[level_num]:
        self.per_level_item_lists[level_num].append(self.item_num_list.pop())
      random.shuffle(self.item_locations[level_num])

    self.PrintLengths()

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[LevelNum, RoomNum, ItemNum]]:
    for level_num in range(1, self.NUM_LEVELS + 1):
      yield (level_num, self.item_locations[level_num].pop(),
             self.per_level_item_lists[level_num].pop())
