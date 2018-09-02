from enum import Enum
from typing import Dict, List
from zelda_constants import Direction, RoomNum, ItemNum


class WallType(Enum):
  OPEN_DOOR = 0
  SOLID_WALL = 1
  INVISIBLE_DOOR_1 = 2
  INVISIBLE_DOOR_2 = 3
  BOMB_HOLE = 4
  LOCKED_DOOR_1 = 5
  LOCKED_DOOR_2 = 6
  SHUTTER_DOOR = 7
  LOVE = 0  # Love is an open dooo-ooooo-ooor!


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

  def __init__(self, rom_data: List[int]) -> None:
    self.rom_data = rom_data
    self.already_visited = False
    self.is_staircase_room = False

    # TODO: This is a hack for a sentinal value.  Make this nicer.
    self.transport_staircase_desintation: RoomNum = None
    self.stairway_item: ItemNum = ItemNum(-1)

  def GetRomData(self) -> List[int]:
    return self.rom_data

  def SetStaircaseRoom(self, is_staircase_room: bool) -> None:
    self.is_staircase_room = is_staircase_room

  def IsItemRoom(self) -> bool:
    # The left and right exit are the same only for an item room, not a transport staircase
    return self.is_staircase_room and (self.rom_data[0] & 0x7F == self.rom_data[1] & 0x7F)

  def IsTransportStaircase(self) -> bool:
    return self.is_staircase_room and not self.IsItemRoom()

  # TODO: Need to figure out how define Direction as a type such that it's allowed to
  # combine a direction and room to become a different room.  Maybe make direction a
  # subclass of roomnum somehow?
  def CanMove(self, direction: RoomNum) -> bool:
    assert not self.is_staircase_room
    (table_num, offset) = self.WALL_TYPE_TABLE_NUMBERS_AND_OFFSETS[direction]
    wall_type = self.rom_data[table_num] >> offset & 0x07
    return wall_type != 1  # 1 is the type code for a sold wall

  def GetStairwayItemNumber(self) -> ItemNum:
    return self.stairway_item

  def SetStairwayItemNumber(self, item_type: ItemNum) -> None:
    self.stairway_item = item_type

  def HasTransportStaircaseDestination(self) -> bool:
    return self.transport_staircase_desintation is not None

  def GetTransportStaircaseDestination(self) -> RoomNum:
    assert self.HasTransportStaircaseDestination()
    return self.transport_staircase_desintation

  def SetTransportStaircaseDestination(self, transport_staircase_desintation: RoomNum) -> None:
    self.transport_staircase_desintation = transport_staircase_desintation

  def GetLeftExit(self) -> RoomNum:
    assert self.IsTransportStaircase()
    return RoomNum(self.rom_data[0] & 0x7F)

  def GetRightExit(self) -> RoomNum:
    assert self.IsTransportStaircase()
    return RoomNum(self.rom_data[1] & 0x7F)

  def MarkAsVisited(self) -> None:
    self.already_visited = True

  def WasAlreadyVisited(self) -> bool:
    return self.already_visited

  def ClearVisitMark(self) -> None:
    self.already_visited = False

  def GetItemNumber(self) -> ItemNum:
    return ItemNum(self.rom_data[4] & 0x1F)

  def SetItemNumber(self, item_num: ItemNum) -> None:
    old_item_num = self.rom_data[4] & 0x1F
    assert (old_item_num >= 0 and old_item_num <= 0x1F)
    assert (item_num >= 0 and item_num <= 0x1F)

    part_that_shouldnt_be_modified = self.rom_data[4] & 0xE0

    new_value = part_that_shouldnt_be_modified + int(item_num)
    assert new_value & 0xE0 == part_that_shouldnt_be_modified
    assert new_value & 0x1F == item_num
    self.rom_data[4] = new_value
    print("Changed item %x to %x" % (old_item_num, item_num))
