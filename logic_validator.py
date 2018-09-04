from typing import List, Tuple
from level_data_table import LevelDataTable
from constants import Direction, Item, LevelNum, Range, RoomNum


class LogicValidator(object):
  # Note: The inclusion of a "Tringle" as a progression item is to ensure that no other progression
  # item can be in level 9 unless all eight of the tringles in levels 1-8 can be obtained without
  # that item.  This leaves the possibility of double-dips of level 9, particularly for the bow.
  PROGRESSION_ITEMS = [Item.BOW, Item.RECORDER, Item.LADDER, Item.TRINGLE]

  def __init__(self, level_data_table: LevelDataTable) -> None:
    self.level_data_table = level_data_table
    self.required_item_for_entry = [
        None, None, None, None, Item.RAFT, None, None, Item.RECORDER, None, Item.TRINGLE
    ]
    self.item_depenedencies: List[Tuple[Item, Item]] = []
    self.circular_dependencies: List[Tuple[Item, Item]] = []

  def Validate(self):
    self._FindItemDependencies()
    return not self.circular_dependencies

  def _FindItemDependencies(self) -> None:
    for level_num in Range.VALID_LEVEL_NUMBERS:

      # Get a list of items in the level that may be needed for progression elsewhere.
      self.level_data_table.ClearAllVisitMarkers()
      all_progression_items: List[Item] = []
      self._GetProgressionItemsInLevelRecursively(
          level_num, self.level_data_table.GetLevelStartRoomNumber(level_num), Direction.NORTH,
          None, all_progression_items)
      self.level_data_table.ClearAllVisitMarkers()

      # For dungeons where entry is gated on an item (e.g. raft for level 4)
      if self.required_item_for_entry[level_num] is not None:
        for item in all_progression_items:
          self._AddItemDependency(self.required_item_for_entry[level_num], item)

      # Now, to find dependencies!
      for missing_item in [Item.BOW, Item.RECORDER, Item.LADDER]:
        items_obtained: List[Item] = []
        self._GetProgressionItemsInLevelRecursively(
            level_num, self.level_data_table.GetLevelStartRoomNumber(level_num), Direction.NORTH,
            missing_item, items_obtained)
        for item in all_progression_items:
          if not item in items_obtained:
            self._AddItemDependency(missing_item, item)

  def _GetProgressionItemsInLevelRecursively(self, level_num: LevelNum, room_num: RoomNum,
                                             entry_direction: Direction, missing_item: Item,
                                             items_obtained: List[Item]) -> None:
    if not room_num in Range.VALID_ROOM_NUMBERS:
      return  # No escaping back into the overworld! :)
    room = self.level_data_table.GetLevelRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()

    if room.GetItem() in self.PROGRESSION_ITEMS and room.CanGetItem(entry_direction, missing_item):
      items_obtained.append(room.GetItem())

    # An item staircase room is a dead-end, so no need to recurse more.
    if room.IsItemStaircase():
      return

    # For a transport staircase, we don't know whether we came in through the left or right.
    # So try to leave both ways; the one that we came from will have already been marked as
    # visited, which won't do anything.
    elif room.IsTransportStaircase():
      for room_num_to_visit in [room.GetLeftExit(), room.GetRightExit()]:
        self._GetProgressionItemsInLevelRecursively(level_num, room_num_to_visit, Direction.UP,
                                                    missing_item, items_obtained)

    # Regular level room case.  Try all cardinal directions as well as taking a staircase (if any).
    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH,
                      Direction.DOWN):
      self._GetProgressionItemsInLevelRecursively(level_num, room_num, direction, missing_item,
                                                  items_obtained)

  def _AddItemDependency(self, required_item: Item, blocked_item: Item) -> None:
    self.item_depenedencies.append((required_item, blocked_item))
    # TODO: This only finds direct circular dependencies (e.g. A needed for B and B needed for A).
    # Need more work to find dependency chains, such as A -> B -> C -> A
    if (blocked_item, required_item) in self.item_depenedencies:
      self.circular_dependencies.append((blocked_item, required_item))
