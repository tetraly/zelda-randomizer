import random
import sys
from typing import List
from zelda_rom import ZeldaRom
from rom import Rom

from zelda_constants import Direction


[randomizer logic] -> item location manger
[zelda_rom] -> LevelRooms (get/set) levelroom.set(room_num, level_num, item_code)
[rom]


class ItemAndLocationManager(object):
  NO_ITEM_NUMBER = 0x03  # Actually code for mags, but that's how they did it!
  ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS = [0x16, 0x17, 0x1B] # Compass, map, tringle

  def __init__(self) -> None:
    self.item_locations = {} # type: Dict[int, List[int]]
    self.item_num_list = [] # type: List[int]
    
    self.per_level_item_lists = {} # Dict int -> list[item]

  def AddLocationAndItem(self, level_num: int, room_num: int, item_num) -> None:
    assert level_num in range(1, NUM_LEVELS + 1)
    assert item_num in range(0, 0x20)
    if item_num == self.NO_ITEM_NUMBER:
      return
    if item_num in self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS:
      return
      
    self.item_locations[level_num] = room_num
    self.item_num_list.append(item_num)
    
  def ShuffleItemsGlobally(self) -> None:
    random.shuffle(self.item_num_list)
  
  def ShuffleItemsWithinLevels(self) -> None:
    for level_num in range(1, NUM_LEVELS + 1):
     random.shuffle(self.item_locations[level_num])

  def CreatePerLevelItemLists(self) -> None:
    for level_num in range(1, NUM_LEVELS + 1):
      self.per_level_item_lists[level_num].extend(ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS)
      for unused_location in self.item_locations[level_num]:
        self.per_level_item_lists[level_num].append(self.item_num_list.pop())
  
  def GetAllLocationAndItemData(self) -> List[Tuple[int, int, int]]:
    for level_num in range(1, NUM_LEVELS + 1):
      





shuffle all items around all levels.  
Constraint: each level must have 1 triforce, map, and compass

shuffle across all levels all items except those codes
Then, for each level:
  Re-shuffle among only the level all the items
  

Reading in data, keep per-level lists of locations, items

List[List[int]]
level, list[locations]
***Dict[level -> list[locations]]***

List[int]
items that should be shuffled over all levels





class ItemRandomizer(object):
  NUM_LEVELS = 9
  NUM_ROOMS_PER_MAP = 0x80

  def __init__(self, rom: ZeldaRom) -> None:
    self.rom = rom
    self.level_location_lists = [None] # type: List[List[int]]
    for level_num in range(1, self.NUM_LEVELS + 1):
      self.level_location_lists.append([])
    self.item_list = [] # type: List[int]

  def ReadItemsAndLocations(self) -> None:
    for level_num in range(1, self.NUM_LEVELS + 1):
      print("Reading data for level %d " % level_num)
      for stairway_room_num in self.rom.GetLevelStairwayRoomNumberList(level_num):
        stairway_room = self.rom.GetRoom(stairway_room_num, level_num)
        # Item room case
        if stairway_room.GetLeftExit() == stairway_room.GetRightExit():
          self.location_list.append((level_num, stairway_room_num))
          self.item_list.append(stairway_room.GetItemNumber())
        # Transport staircase case
        else:
          left_exit = stairway_room.GetLeftExit()
          right_exit = stairway_room.GetRightExit()
          self.rom.GetRoom(left_exit, level_num).SetStairwayPassageRoom(right_exit, 0)
          self.rom.GetRoom(right_exit, level_num).SetStairwayPassageRoom(left_exit, 0)
      print("  Found start room %x" % self.rom.GetLevelStartRoomNumber(level_num))
      self._ReadItemsAndLocationsRecursively(
          self.rom.GetLevelStartRoomNumber(level_num), level_num)
    assert len(self.location_list) == len(self.item_list)

  def _ReadItemsAndLocationsRecursively(self, room_num: int, level_num: int) -> None:
    if room_num >= self.NUM_ROOMS_PER_MAP:
      return  # No escaping back into the overworld! :)
    room = self.rom.GetRoom(room_num, level_num)
    if room.WasAlreadyVisited():
      return
    room.MarkAsVisited()

    item_num = room.GetItemNumber()
    if item_num != self.NO_ITEM_NUMBER:
      self.location_list.append((level_num, room_num))
      self.item_list.append(item_num)

    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if room.CanMove(direction):
        self._ReadItemsAndLocationsRecursively(
            room_num + direction, level_num)
    if room.HasStairwayPassageRoom():
      self._ReadItemsAndLocationsRecursively(room.GetStairwayPassageRoom(), level_num)

  def ShuffleItems(self):
    print("Lists:")
    print(len(self.location_list))
    print(len(self.item_list))
    assert len(self.location_list) == len(self.item_list)

    for (level_num, room_num), item_num in zip(self.location_list, self.item_list):
      print("Level %d, room %x, item #%x" % (level_num, room_num, item_num))
    random.seed(12345)
    random.shuffle(self.item_list)
    print("hello")
    for (level_num, room_num), item_num in zip(self.location_list, self.item_list):
      print("Level %d, room %x, item #%x" % (level_num, room_num, item_num))
      self.rom.GetRoom(room_num, level_num).SetItemNumber(item_num)


def main(input_filename: str) -> None:
  base_rom = Rom(input_filename, add_nes_header_offset=True)
  base_rom.OpenFile(write_mode=True)
  rom = ZeldaRom(base_rom)
  rom.ReadLevelData()

  item_randomizer = ItemRandomizer(rom)
  item_randomizer.ReadItemsAndLocations()
  item_randomizer.ShuffleItems()



if __name__ == "__main__":
  main(sys.argv[1])
