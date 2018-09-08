from typing import Dict, List
from absl import logging

from .constants import Direction, Enemy, Item, Range, RoomNum, RoomType, WallType


class LevelRoom(object):

  # According to http://www.bwass.org/romhack/zelda1/zelda1bank6.txt:
  # Bytes in table 0 represent:
  # xxx. ....	Type of Door on Top Wall
  # ...x xx..	Type of Door on Bottom Wall
  # .... ..xx	Code for Palette 0 (Outer Border)
  # Bytes in table 1 represent:
  # xxx. ....	Type of Door on Left Wall
  # ...x xx..	Type of Door on Right Wall
  # .... ..xx	Code for Palette 1 (Inner Section)
  WALL_TYPE_TABLE_NUMBERS_AND_OFFSETS = {
      Direction.WEST: (1, 5),  # Bits 5-8 of table 1
      Direction.NORTH: (0, 5),  # Bits 5-8 of table 0
      Direction.EAST: (1, 2),  # Bits 2-5 of table 1
      Direction.SOUTH: (0, 2)  # Bits 2-5 of table 0
  }

  # Rooms where mobility is restricted without a ladder.
  # Note that while the player can exit and enter through any door in a CIRCLE_MOAT_ROOM, we keep
  # it in this Dict since a room item may not be able to be picked up without the ladder.
  POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS: Dict[RoomType, List[Direction]] = {
      RoomType.CIRCLE_MOAT_ROOM: [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST],
      RoomType.DOUBLE_MOAT_ROOM: [Direction.EAST, Direction.WEST],
      RoomType.HORIZONTAL_MOAT_ROOM: [Direction.EAST, Direction.SOUTH, Direction.WEST],
      RoomType.VERTICAL_MOAT_ROOM: [Direction.SOUTH, Direction.WEST, Direction.NORTH],
      RoomType.CHEVY_ROOM: []
  }
  POTENTIAL_LADDER_BLOCK_ROOMS = POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS.keys()

  MOVEMENT_CONSTRAINED_ROOMS_VALID_TRAVEL_DIRECTIONS: Dict[RoomType, List[Direction]] = {
      RoomType.HORIZONTAL_CHUTE_ROOM: [Direction.EAST, Direction.WEST],
      RoomType.VERTICAL_CHUTE_ROOM: [Direction.NORTH, Direction.SOUTH],
      RoomType.T_ROOM: [Direction.WEST, Direction.NORTH, Direction.EAST]
  }
  MOVEMENT_CONSTRAINED_ROOMS = MOVEMENT_CONSTRAINED_ROOMS_VALID_TRAVEL_DIRECTIONS.keys()

  def __init__(self, rom_data: List[int]) -> None:
    self.rom_data = rom_data
    self.staircase_room_num: RoomNum = None
    self.marked_as_visited = False

  def GetRomData(self) -> List[int]:
    return self.rom_data

  # TODO: Change this back to use an Enemy enum type.
  def GetEnemy(self) -> int:
    return self.rom_data[2] & 0x3F

  def GetRoomType(self) -> RoomType:
    return RoomType(self.rom_data[3] & 0x3F)

  def GetWallType(self, direction: Direction) -> WallType:
    assert self.GetRoomType() not in [RoomType.ITEM_STAIRCASE, RoomType.TRANSPORT_STAIRCASE]
    (table_num, offset) = self.WALL_TYPE_TABLE_NUMBERS_AND_OFFSETS[direction]
    return WallType(self.rom_data[table_num] >> offset & 0x07)

  def GetItem(self) -> Item:
    return Item(self.rom_data[4] & 0x1F)

  def HasDropBitSet(self) -> bool:
    assert self.rom_data[5] & 0x04 in [0, 4]
    return self.rom_data[5] & 0x04 > 0

  def IsItemStaircase(self) -> bool:
    return self.GetRoomType() == RoomType.ITEM_STAIRCASE

  def IsTransportStaircase(self) -> bool:
    return self.GetRoomType() == RoomType.TRANSPORT_STAIRCASE

  def GetLeftExit(self) -> RoomNum:
    return RoomNum(self.rom_data[0] & 0x7F)

  def GetRightExit(self) -> RoomNum:
    return RoomNum(self.rom_data[1] & 0x7F)

  def HasStaircaseRoom(self) -> bool:
    return self.staircase_room_num is not None

  def GetStaircaseRoomNumber(self) -> RoomNum:
    return self.staircase_room_num

  def SetStaircaseRoomNumber(self, staircase_room_num: RoomNum) -> None:
    self.staircase_room_num = staircase_room_num

  def CanMove(self, from_direction: Direction, to_direction: Direction, missing_item: Item) -> bool:
    if (self.GetRoomType() in self.MOVEMENT_CONSTRAINED_ROOMS and
        (from_direction not in
         self.MOVEMENT_CONSTRAINED_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetRoomType()] or to_direction
         not in self.MOVEMENT_CONSTRAINED_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetRoomType()])):
      return False

    if (missing_item == Item.LADDER and self.GetRoomType() in self.POTENTIAL_LADDER_BLOCK_ROOMS):
      if (from_direction not in
          self.POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetRoomType()]
          or to_direction not in
          self.POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetRoomType()]):
        return False

    # Check for recorder/bow blocks due to not being able to defeat enemies.
    if self.GetWallType(
        to_direction) == WallType.SHUTTER_DOOR and not self.CanDefeatEnemies(missing_item):
      return False
    return True

  def CanDefeatEnemies(self, missing_item: Item) -> bool:
    if missing_item == Item.RECORDER:
      if self.GetEnemy() in [int(Enemy.DIGDOGGER_SINGLE), int(Enemy.DIGDOGGER_TRIPLE)]:
        return False
    if missing_item == Item.BOW and self.GetEnemy() in [
        int(Enemy.GOHMA_RED), int(Enemy.GOHMA_BLUE)
    ]:
      return False
    return True

  def CanGetItem(self, entry_direction: Direction, missing_item: Item) -> bool:
    # Can't pick up a room in any rooms with water/moats without a ladder.
    # TODO: Make a better determination here based on the drop location and the entry direction.
    if missing_item == Item.LADDER and self.GetRoomType() in self.POTENTIAL_LADDER_BLOCK_ROOMS:
      return False
    if self.HasDropBitSet() and not self.CanDefeatEnemies(missing_item):
      return False
    if self.GetRoomType() == RoomType.HORIZONTAL_CHUTE_ROOM:
      if entry_direction in [Direction.NORTH, Direction.SOUTH]:
        return False
    if self.GetRoomType() == RoomType.VERTICAL_CHUTE_ROOM:
      if entry_direction in [Direction.EAST, Direction.WEST]:
        return False
    return True

  def SetItem(self, item_num_param: Item) -> None:
    item_num = int(item_num_param)
    old_item_num = self.rom_data[4] & 0x1F
    assert old_item_num in Range.VALID_ITEM_NUMBERS
    assert item_num in Range.VALID_ITEM_NUMBERS

    part_that_shouldnt_be_modified = self.rom_data[4] & 0xE0

    new_value = part_that_shouldnt_be_modified + int(item_num)
    assert new_value & 0xE0 == part_that_shouldnt_be_modified
    assert new_value & 0x1F == item_num
    self.rom_data[4] = new_value
    logging.debug("Changed item %x to %x" % (old_item_num, item_num))

  def IsMarkedAsVisited(self) -> bool:
    return self.marked_as_visited

  def MarkAsVisited(self) -> None:
    self.marked_as_visited = True

  def ClearVisitMark(self) -> None:
    self.marked_as_visited = False