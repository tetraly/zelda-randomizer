from typing import Dict, List
from constants import Direction, Enemy, Item, RoomNum, RoomType, WallType


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
  POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS: Dict[RoomType, List[Direction]] = {
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
    self.already_visited = False
    self.is_staircase_room = False

    self.transport_staircase_desintation: RoomNum = None
    # TODO: This is a hack for a sentinel value.  Make this nicer.
    self.stairway_item: Item = Item.NO_ITEM

  def GetRomData(self) -> List[int]:
    return self.rom_data

  def GetEnemy(self) -> Enemy:
    return Enemy(self.rom_data[2] & 0x3F)

  def GetRoomType(self) -> RoomType:
    return RoomType(self.rom_data[3] & 0x3F)

  def GetWallType(self, direction: Direction) -> WallType:
    assert not self.is_staircase_room
    (table_num, offset) = self.WALL_TYPE_TABLE_NUMBERS_AND_OFFSETS[direction]
    return WallType(self.rom_data[table_num] >> offset & 0x07)

  def GetItem(self) -> Item:
    return Item(self.rom_data[4] & 0x1F)

  def HasDropBitSet(self) -> bool:
    assert self.rom_data[5] & 0x04 == 0 or self.rom_data[5] & 0x04 == 4
    return self.rom_data[5] & 0x04 > 0

  def SetStaircaseRoom(self, is_staircase_room: bool) -> None:
    self.is_staircase_room = is_staircase_room

  def IsItemRoom(self) -> bool:
    # The left and right exit are the same only for an item room, not a transport staircase
    return self.is_staircase_room and (self.rom_data[0] & 0x7F == self.rom_data[1] & 0x7F)

  def IsTransportStaircase(self) -> bool:
    return self.is_staircase_room and not self.IsItemRoom()

  def GetLeftExit(self) -> RoomNum:
    assert self.IsTransportStaircase()
    return RoomNum(self.rom_data[0] & 0x7F)

  def GetRightExit(self) -> RoomNum:
    assert self.IsTransportStaircase()
    return RoomNum(self.rom_data[1] & 0x7F)

  def HasTransportStaircase(self) -> bool:
    return self.transport_staircase_desintation is not None

  def GetTransportStaircaseDestination(self) -> RoomNum:
    assert self.HasTransportStaircase()
    return self.transport_staircase_desintation

  def SetTransportStaircaseDestination(self, transport_staircase_desintation: RoomNum) -> None:
    self.transport_staircase_desintation = transport_staircase_desintation

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
    if missing_item == Item.RECORDER and self.GetEnemy() in [
        Enemy.DIGDOGGER_SINGLE, Enemy.DIGDOGGER_TRIPLE
    ]:
      return False
    if missing_item == Item.BOW and self.GetEnemy() in [Enemy.GOHMA_RED, Enemy.GOHMA_BLUE]:
      return False
    return True

  def CanGetItem(self, entry_direction: Direction, missing_item: Item) -> bool:
    # Can't pick up a room in any rooms with water/moats without a ladder.
    # TODO: Make a better determination here based on the drop location and the entry direction.
    if missing_item == Item.LADDER and self.GetRoomType() in self.POTENTIAL_LADDER_BLOCK_ROOMS:
      return False
    if self.HasDropBitSet() and not self.CanDefeatEnemies(missing_item):
      return False
    if self.GetRoomType() == RoomType.HORIZONTAL_CHUTE_ROOM and entry_direction in [
        Direction.NORTH, Direction.SOUTH
    ]:
      return False
    if self.GetRoomType() == RoomType.VERTICAL_CHUTE_ROOM and entry_direction in [
        Direction.EAST, Direction.WEST
    ]:
      return False
    return True

  def SetItem(self, item_num_param: Item) -> None:
    item_num = int(item_num_param)
    old_item_num = self.rom_data[4] & 0x1F
    assert (old_item_num >= 0 and old_item_num <= 0x1F)
    assert (item_num >= 0 and item_num <= 0x1F)

    part_that_shouldnt_be_modified = self.rom_data[4] & 0xE0

    new_value = part_that_shouldnt_be_modified + int(item_num)
    assert new_value & 0xE0 == part_that_shouldnt_be_modified
    assert new_value & 0x1F == item_num
    self.rom_data[4] = new_value
    print("Changed item %x to %x" % (old_item_num, item_num))

  def WasAlreadyVisited(self) -> bool:
    return self.already_visited

  def MarkAsVisited(self) -> None:
    self.already_visited = True

  def ClearVisitMark(self) -> None:
    self.already_visited = False
