from typing import DefaultDict, List, Tuple, Iterable
from collections import defaultdict
from random import shuffle
from absl import logging

from .constants import Direction, Item, LevelNum, Range, RoomNum, RoomType, WallType
from .data_table import DataTable
from .location import Location
from .settings import Settings


class ItemRandomizer():
  def __init__(self, data_table: DataTable, settings: Settings) -> None:
    self.data_table = data_table
    self.settings = settings
    self.item_shuffler = ItemShuffler(settings)

  WOOD_SWORD_LOCATION = Location.CavePosition(0, 2)
  TAKE_ANY_HEART_LOCATION = Location.CavePosition(1, 3)
  WHITE_SWORD_LOCATION = Location.CavePosition(2, 2)
  MAGICAL_SWORD_LOCATION = Location.CavePosition(3, 2)
  LETTER_LOCATION = Location.CavePosition(8, 2)
  BLUE_POTION_LOCATION = Location.CavePosition(10, 1)
  SHIELD_LOCATION_1 = Location.CavePosition(13, 1)
  WOODEN_ARROWS_LOCATION = Location.CavePosition(13, 3)
  SHIELD_LOCATION_2 = Location.CavePosition(14, 1)
  BLUE_CANDLE_LOCATION = Location.CavePosition(14, 3)
  SHIELD_LOCATION_3 = Location.CavePosition(15, 1)
  BAIT_LOCATION_1 = Location.CavePosition(15, 2)
  BLUE_RING_LOCATION = Location.CavePosition(16, 2)
  BAIT_LOCATION_2 = Location.CavePosition(16, 3)
  ARMOS_ITEM_LOCATION = Location.CavePosition(20, 2)
  COAST_ITEM_LOCATION = Location.CavePosition(21, 2)

  def _GetOverworldItemsToShuffle(self) -> List[Location]:
    items: List[Location] = []
    if self.settings.shuffle_white_sword:
      items.append(self.WHITE_SWORD_LOCATION)
    if self.settings.shuffle_magical_sword:
      items.append(self.MAGICAL_SWORD_LOCATION)
    if self.settings.shuffle_coast_item:
      items.append(self.COAST_ITEM_LOCATION)
    if self.settings.shuffle_armos_item:
      items.append(self.ARMOS_ITEM_LOCATION)
    if self.settings.shuffle_letter:
      items.append(self.LETTER_LOCATION)
    if self.settings.shuffle_shop_items:
      items.extend(
          [self.WOODEN_ARROWS_LOCATION, self.BLUE_CANDLE_LOCATION, self.BLUE_RING_LOCATION])
      if not self.settings.shuffle_take_any_hearts_shields_and_bait:
        items.extend([self.BAIT_LOCATION_1, self.BAIT_LOCATION_2])
    return items

  def ResetState(self):
    self.item_shuffler.ResetState()

  def ReadItemsAndLocationsFromTable(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      self._ReadItemsAndLocationsForUndergroundLevel(level_num)
    for location in self._GetOverworldItemsToShuffle():
      item_num = self.data_table.GetCaveItem(location)
      self.item_shuffler.AddLocationAndItem(location, item_num)
    if self.settings.shuffle_take_any_hearts_shields_and_bait:
      self.item_shuffler.AddLocationAndItem(self.BAIT_LOCATION_1, Item.BAIT)
      self.item_shuffler.AddLocationAndItem(self.BAIT_LOCATION_2, Item.HEART_CONTAINER)
      self.item_shuffler.AddLocationAndItem(self.SHIELD_LOCATION_1, Item.MAGICAL_SHIELD)
      self.item_shuffler.AddLocationAndItem(self.SHIELD_LOCATION_2, Item.HEART_CONTAINER)
      self.item_shuffler.AddLocationAndItem(self.SHIELD_LOCATION_3, Item.HEART_CONTAINER)
      self.item_shuffler.AddLocationAndItem(self.TAKE_ANY_HEART_LOCATION, Item.HEART_CONTAINER)

  def _ReadItemsAndLocationsForUndergroundLevel(self, level_num: LevelNum) -> None:
    logging.debug("Reading staircase room data for level %d " % level_num)
    for staircase_room_num in self.data_table.GetLevelStaircaseRoomNumberList(level_num):
      self._ParseStaircaseRoom(level_num, staircase_room_num)
    level_start_room_num = self.data_table.GetLevelStartRoomNumber(level_num)
    logging.debug("Traversing level %d.  Start room is %x. " % (level_num, level_start_room_num))
    self._ReadItemsAndLocationsRecursively(level_num, level_start_room_num)

  def _ParseStaircaseRoom(self, level_num: LevelNum, staircase_room_num: RoomNum) -> None:
    staircase_room = self.data_table.GetRoom(level_num, staircase_room_num)

    if staircase_room.GetType() == RoomType.ITEM_STAIRCASE:
      logging.debug("  Found item staircase %x in L%d " % (staircase_room_num, level_num))
      assert staircase_room.GetLeftExit() == staircase_room.GetRightExit()
      self.data_table.GetRoom(
          level_num, staircase_room.GetLeftExit()).SetStaircaseRoomNumber(staircase_room_num)
    elif staircase_room.GetType() == RoomType.TRANSPORT_STAIRCASE:
      logging.debug("  Found transport staircase %x in L%d " % (staircase_room_num, level_num))
      assert staircase_room.GetLeftExit() != staircase_room.GetRightExit()
      for associated_room_num in [staircase_room.GetLeftExit(), staircase_room.GetRightExit()]:
        self.data_table.GetRoom(level_num,
                                associated_room_num).SetStaircaseRoomNumber(staircase_room_num)
    else:
      logging.fatal("Room in staircase room number list (%x) didn't have staircase type (%x)." %
                    (staircase_room_num, staircase_room.GetType()))

  def _ReadItemsAndLocationsRecursively(self, level_num: LevelNum, room_num: RoomNum) -> None:
    if room_num not in Range.VALID_ROOM_NUMBERS:
      return  # No escaping back into the overworld! :)
    room = self.data_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()

    item_num = room.GetItem()
    if item_num not in [Item.NO_ITEM, Item.TRIFORCE_OF_POWER]:
      self.item_shuffler.AddLocationAndItem(Location.LevelRoom(level_num, room_num), item_num)

    # Staircase cases (bad pun intended)
    if room.GetType() == RoomType.ITEM_STAIRCASE:
      return  # Dead end, no need to traverse further.
    elif room.GetType() == RoomType.TRANSPORT_STAIRCASE:
      for upstairs_room in [room.GetLeftExit(), room.GetRightExit()]:
        self._ReadItemsAndLocationsRecursively(level_num, upstairs_room)
      return
    # Regular (non-staircase) room case.  Check all four cardinal directions, plus "down".
    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if room.GetWallType(direction) != WallType.SOLID_WALL:
        self._ReadItemsAndLocationsRecursively(level_num, RoomNum(room_num + direction))
    if room.HasStaircase():
      self._ReadItemsAndLocationsRecursively(level_num, room.GetStaircaseRoomNumber())

  def ShuffleItems(self) -> None:
    self.item_shuffler.ShuffleItems()

  def WriteItemsAndLocationsToTable(self) -> None:
    for (location, item_num) in self.item_shuffler.GetAllLocationAndItemData():
      if location.IsLevelRoom():
        self.data_table.SetRoomItem(location, item_num)
        if item_num == Item.TRINGLE:
          self.data_table.UpdateTriforceLocation(location)
      elif location.IsCavePosition():
        self.data_table.SetCaveItem(location, item_num)


class ItemShuffler():
  def __init__(self, settings: Settings) -> None:
    self.settings = settings
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
    #TODO: This would be more elgant with a dict lookup
    if self.settings.progressive_items:
      if item_num == Item.RED_CANDLE:
        item_num = Item.BLUE_CANDLE
      if item_num == Item.RED_RING:
        item_num = Item.BLUE_RING
      if item_num == Item.SILVER_ARROWS:
        item_num = Item.WOOD_ARROWS
      if item_num == Item.WHITE_SWORD:
        item_num = Item.WOOD_SWORD
      if item_num == Item.MAGICAL_SWORD:
        item_num = Item.WOOD_SWORD
      if item_num == Item.INFERIOR_MODEL:
        item_num = Item.LORD_BANANA

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
