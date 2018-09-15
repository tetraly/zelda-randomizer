from absl import logging

from randomizer.item_shuffler import ItemShuffler
from randomizer.level_data_table import LevelDataTable
from randomizer.constants import (CaveNum, Direction, Item, LevelNum, PositionNum, Range, RoomNum,
                                  RoomType, WallType)


class ItemRandomizer():
  def __init__(self, level_table: LevelDataTable, item_shuffler: ItemShuffler) -> None:
    self.level_table = level_table
    self.item_shuffler = item_shuffler

  WHITE_SWORD_LOCATION = (CaveNum(0x12), PositionNum(2))
  LETTER_LOCATION = (CaveNum(0x18), PositionNum(2))
  WOODEN_ARROWS_LOCATION = (CaveNum(0x1D), PositionNum(3))
  BLUE_CANDLE_LOCATION = (CaveNum(0x1E), PositionNum(3))
  BLUE_RING_LOCATION = (CaveNum(0x20), PositionNum(2))

  CAVE_ITEMS_TO_SHUFFLE = [
      WHITE_SWORD_LOCATION, LETTER_LOCATION, WOODEN_ARROWS_LOCATION, BLUE_CANDLE_LOCATION,
      BLUE_RING_LOCATION
  ]

  def ReadItemsAndLocationsFromTable(self) -> None:
    for level_num in Range.VALID_UNDERGROUND_LEVEL_NUMBERS:
      self._ReadItemsAndLocationsForUndergroundLevel(level_num)

    for (cave_num, position_num) in self.CAVE_ITEMS_TO_SHUFFLE:
      item_num = self.level_table.GetCave(cave_num).GetItemAtPosition(position_num)
      self.item_shuffler.AddLocationAndItem(cave_num, position_num, item_num)

  def _ReadItemsAndLocationsForUndergroundLevel(self, level_num: LevelNum) -> None:
    logging.debug("Reading staircase room data for level %d " % level_num)
    for staircase_room_num in self.level_table.GetLevelStaircaseRoomNumberList(level_num):
      self._ParseStaircaseRoom(level_num, staircase_room_num)
    level_start_room_num = self.level_table.GetLevelStartRoomNumber(level_num)
    logging.debug("Traversing level %d.  Start room is %x. " % (level_num, level_start_room_num))
    self._ReadItemsAndLocationsRecursively(level_num, level_start_room_num)

  def _ParseStaircaseRoom(self, level_num: LevelNum, staircase_room_num: RoomNum) -> None:
    staircase_room = self.level_table.GetRoom(level_num, staircase_room_num)

    if staircase_room.GetRoomType() == RoomType.ITEM_STAIRCASE:
      logging.debug("  Found item staircase %x in L%d " % (staircase_room_num, level_num))
      assert staircase_room.GetLeftExit() == staircase_room.GetRightExit()
      self.level_table.GetRoom(
          level_num, staircase_room.GetLeftExit()).SetStaircaseRoomNumber(staircase_room_num)
    elif staircase_room.GetRoomType() == RoomType.TRANSPORT_STAIRCASE:
      logging.debug("  Found transport staircase %x in L%d " % (staircase_room_num, level_num))
      assert staircase_room.GetLeftExit() != staircase_room.GetRightExit()
      for associated_room_num in [staircase_room.GetLeftExit(), staircase_room.GetRightExit()]:
        self.level_table.GetRoom(level_num,
                                 associated_room_num).SetStaircaseRoomNumber(staircase_room_num)
    else:
      logging.fatal("Room in staircase room number list (%x) didn't have staircase type (%x)." %
                    (staircase_room_num, staircase_room.GetRoomType()))

  def _ReadItemsAndLocationsRecursively(self, level_num: LevelNum, room_num: RoomNum) -> None:
    if room_num not in Range.VALID_ROOM_NUMBERS:
      return  # No escaping back into the overworld! :)
    room = self.level_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()

    item_num = room.GetItem()
    if item_num not in [Item.NO_ITEM, Item.TRIFORCE_OF_POWER]:
      self.item_shuffler.AddLocationAndItem(level_num, room_num, item_num)

    # Staircase cases (bad pun intended)
    if room.GetRoomType() == RoomType.ITEM_STAIRCASE:
      return  # Dead end, no need to traverse further.
    elif room.GetRoomType() == RoomType.TRANSPORT_STAIRCASE:
      for upstairs_room in [room.GetLeftExit(), room.GetRightExit()]:
        self._ReadItemsAndLocationsRecursively(level_num, upstairs_room)
      return
    # Regular (non-staircase) room case.  Check all four cardinal directions, plus "down".
    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if room.GetWallType(direction) != WallType.SOLID_WALL:
        self._ReadItemsAndLocationsRecursively(level_num, RoomNum(room_num + direction))
    if room.HasStaircaseRoom():
      self._ReadItemsAndLocationsRecursively(level_num, room.GetStaircaseRoomNumber())

  def ShuffleItems(self):
    self.item_shuffler.ShuffleItems()

  def WriteItemsAndLocationsToTable(self) -> None:
    for (level_or_cave_num, room_or_position_num,
         item_num) in self.item_shuffler.GetAllLocationAndItemData():
      if level_or_cave_num in Range.VALID_UNDERGROUND_LEVEL_NUMBERS:
        level_num = LevelNum(level_or_cave_num)
        room_num = RoomNum(room_or_position_num)
        self.level_table.GetRoom(level_num, room_num).SetItem(item_num)
        # TODO: Fix Compass bug for tringles in item staircases
        if item_num == Item.TRINGLE:
          self.level_table.UpdateTriforceLocation(level_num, room_num)
      elif level_or_cave_num >= 0x10:
        cave_num = CaveNum(level_or_cave_num)
        position_num = PositionNum(room_or_position_num)
      self.level_table.GetCave(cave_num).SetItemNumberAtPosition(item_num, position_num)
