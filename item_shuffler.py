from typing import Dict, List, NewType, Tuple, Iterable
import random
from zelda_constants import LevelNum, RoomNum, ItemNum

class ItemShuffler(object):

  NO_ITEM_NUMBER = ItemNum(0x03) # Actually code for mags, but that's how they did it!
  # Compass, map, tringle
  ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS = [ItemNum(0x16), ItemNum(0x17), ItemNum(0x1B)]
  NUM_LEVELS = 9
  NUM_ITEM_TYPES = ItemNum(0x20)

  def __init__(self) -> None:
    self.item_locations = {} # type: Dict[LevelNum, List[RoomNum]]
    self.item_num_list = [] # type: List[ItemNum]
    self.per_level_item_lists = {} # type: Dict[LevelNum, List[ItemNum]]
    self.seed = None # type: int

  def AddLocationAndItem(self, level_num: LevelNum, room_num: RoomNum, item_num: ItemNum) -> None:
    assert level_num in range(1, self.NUM_LEVELS + 1)
    assert item_num in range(0, self.NUM_ITEM_TYPES)
    if item_num == self.NO_ITEM_NUMBER:
      return
    if item_num in self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS:
      return

    if level_num not in self.item_locations:
      self.item_locations[level_num] = []
    self.item_locations[level_num].append(room_num)
    self.item_num_list.append(item_num)

  def ShuffleItemsGlobally(self) -> None:
    random.shuffle(self.item_num_list)

  def ShuffleItemsWithinLevels(self) -> None:
    for level_num in range(1, self.NUM_LEVELS + 1):
      self.per_level_item_lists[level_num].extend(self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS)
      for unused_location in self.item_locations[level_num]:
        self.per_level_item_lists[level_num].append(self.item_num_list.pop())
      random.shuffle(self.item_locations[level_num])

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[LevelNum, RoomNum, ItemNum]]:
    for level_num in range(1, self.NUM_LEVELS + 1):
      yield (level_num,
             self.item_locations[level_num].pop(),
             self.per_level_item_lists[level_num].pop())
