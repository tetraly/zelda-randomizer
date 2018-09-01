from typing import Dict, List
from zelda_constants import Direction, RoomNum, ItemNum

class LevelRoom(object):
  def __init__(self, rom_data: List[int]) -> None:
    self.wall_type = {} # type: Dict[int, int]

    # Applicable to regular dungeon rooms
    self.wall_type[Direction.WEST] = (rom_data[1] >> 5) & 0x07
    self.wall_type[Direction.NORTH] = (rom_data[0] >> 5) & 0x07
    self.wall_type[Direction.EAST] = (rom_data[1] >> 2) & 0x07
    self.wall_type[Direction.SOUTH] = (rom_data[0] >> 2) & 0x07

    # Applicable to stairway rooms
    self.left_exit = RoomNum(rom_data[0] & 0x7F)
    self.right_exit = RoomNum(rom_data[1] & 0x7F)

    # Room atributes
    self.has_stairway = rom_data[5] & 0x01 == 1
    self.item_num = ItemNum(rom_data[4] & 0x1F)

    # Non-ROM values
    self.already_visited = False
    # TODO: This is a hack for a sentinal value.  Make this nicer.
    self.stairway_passage_room = RoomNum(-1) # type: RoomNum
    self.stairway_item = ItemNum(-1) # type: ItemNum

  def CanMove(self, direction: int) -> bool:
    return self.wall_type[direction] != 1  # sold wall

  def GetStairwayItemNumber(self) -> ItemNum:
    return self.stairway_item
  def SetStairwayItemNumber(self, item_type: ItemNum) -> None:
    self.stairway_item = item_type

  def HasStairwayPassageRoom(self) -> bool:
    return self.stairway_passage_room >= 0x00
  def GetStairwayPassageRoom(self) -> RoomNum:
    return self.stairway_passage_room
  def SetStairwayPassageRoom(self, other_room: RoomNum) -> None:
    self.stairway_passage_room = other_room

  def GetLeftExit(self) -> RoomNum:
    return self.left_exit
  def GetRightExit(self) -> RoomNum:
    return self.right_exit

  def MarkAsVisited(self) -> None:
    self.already_visited = True
  def WasAlreadyVisited(self) -> bool:
    return self.already_visited
  def ClearVisitMark(self) -> None:
    self.already_visited = False


  def GetItemNumber(self) -> ItemNum:
    return self.item_num
  def SetItemNumber(self, item_num: ItemNum) -> None:
    assert(item_num >= 0 and item_num <= 0x1F)
    self.item_num = item_num
