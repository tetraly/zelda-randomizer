from item_shuffler import ItemShuffler
from level_data_table import LevelDataTable
from constants import Direction, Item, LevelNum, Range, RoomNum, WallType


class ItemRandomizer(object):
  def __init__(self, level_table: LevelDataTable, item_shuffler: ItemShuffler) -> None:
    self.level_table = level_table
    self.item_shuffler = item_shuffler

  def ReadItemsAndLocationsFromTable(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:
      print("Reading data for level %d " % level_num)
      for stairway_room_num in self.level_table.GetLevelStairwayRoomNumberList(level_num):
        stairway_room = self.level_table.GetLevelRoom(level_num, stairway_room_num)
        stairway_room.SetStaircaseRoom(True)
        # Item room case
        if stairway_room.IsItemRoom():
          self.item_shuffler.AddLocationAndItem(level_num, stairway_room_num,
                                                stairway_room.GetItem())
        else:  # Transport staircase case.  Mark the connecting rooms
          left_exit = stairway_room.GetLeftExit()
          right_exit = stairway_room.GetRightExit()
          self.level_table.GetLevelRoom(level_num,
                                        left_exit).SetTransportStaircaseDestination(right_exit)
          self.level_table.GetLevelRoom(level_num,
                                        right_exit).SetTransportStaircaseDestination(left_exit)
      self._ReadItemsAndLocationsRecursively(
          self.level_table.GetLevelStartRoomNumber(level_num), level_num)

  def _ReadItemsAndLocationsRecursively(self, room_num: RoomNum, level_num: LevelNum) -> None:
    if room_num not in Range.VALID_ROOM_NUMBERS:
      return  # No escaping back into the overworld! :)
    room = self.level_table.GetLevelRoom(level_num, room_num)
    if room.WasAlreadyVisited():
      return
    room.MarkAsVisited()

    item_num = room.GetItem()
    if item_num != Item.NO_ITEM:
      self.item_shuffler.AddLocationAndItem(level_num, room_num, item_num)

    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if room.GetWallType(direction) != WallType.SOLID_WALL:
        self._ReadItemsAndLocationsRecursively(RoomNum(room_num + direction), level_num)
    if room.HasTransportStaircase():
      self._ReadItemsAndLocationsRecursively(room.GetTransportStaircaseDestination(), level_num)

  def ShuffleItems(self):
    self.item_shuffler.ShuffleItems()

  def WriteItemsAndLocationsToTable(self) -> None:
    for (level_num, room_num, item_num) in self.item_shuffler.GetAllLocationAndItemData():
      self.level_table.GetLevelRoom(level_num, room_num).SetItem(item_num)
