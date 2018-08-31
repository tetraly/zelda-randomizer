from typing import Dict, List
from zelda_constants import Direction
import zelda_constants

class LevelRoom(object):
  def __init__(self, rom_data: List[int]) -> None:
    self.wall_type = {} # type: Dict[int, int]

    # Applicable to regular dungeon rooms
    self.wall_type[Direction.WEST] = (rom_data[1] >> 5) & 0x07
    self.wall_type[Direction.NORTH] = (rom_data[0] >> 5) & 0x07
    self.wall_type[Direction.EAST] = (rom_data[1] >> 2) & 0x07
    self.wall_type[Direction.SOUTH] = (rom_data[0] >> 2) & 0x07

    # Applicable to stairway rooms
    self.left_exit = rom_data[0] & 0x7F
    self.right_exit = rom_data[1] & 0x7F

    # Room atributes
    self.has_stairway = rom_data[5] & 0x01 == 1
    self.item_num = rom_data[4] & 0x1F
 
    # Non-ROM values
    self.already_visited = False
    self.stairway_passage_room = -1
    self.stairway_passage_num = 0
    self.stairway_item = -1

  def CanMove(self, direction: int) -> bool:
    return self.wall_type[direction] != 1  # sold wall

  def CanMoveWithoutOpeningShutters(self, direction: int) -> bool:
    return self.wall_type[direction] not in [1, 7]  # solid wall or shutter

  def CanMoveWithoutLadder(self, entry_direction: int, exit_direction: int) -> bool:
    if self.room_type == 0x12: # T Room
      return not (entry_direction == Direction.SOUTH or
                  exit_direction == Direction.SOUTH)
    if self.room_type == 0x13: # "E River"
      return not (entry_direction == Direction.EAST or
                  exit_direction == Direction.EAST)
    if self.room_type == 0x16: # "Chevy" room
      return False
    if self.room_type == 0x18: # TopRivr
      return not (entry_direction == Direction.NORTH or
                  exit_direction == Direction.NORTH)
    if self.room_type == 0x19:  # = River
      return (not (entry_direction == Direction.NORTH or
                   exit_direction == Direction.NORTH) and
              not (entry_direction == Direction.SOUTH or
                   exit_direction == Direction.SOUTH))
    return True

  def CanDefeatEnemiesOrGetItemWithoutDoingSo(self, missing_item: int) -> bool:
    if not self.is_drop_item:
      return True
    return self.CanDefeatEnemies(missing_item)

  def CanDefeatEnemiesOrBlockClipOrRightStairs(self, missing_item: int) -> bool:
    if self.room_type in (zelda_constants.DIAMOND_ROOM_TYPE,
                          zelda_constants.RIGHT_STAIRS_ROOM_TYPE):
      return True
    return self.CanDefeatEnemies(missing_item)

  def CanDefeatEnemies(self, missing_item: int) -> bool:
    if (missing_item == zelda_constants.RECORDER and
        not self.has_mixed_enemies and
        self.enemy_type in zelda_constants.DIGDOGGER_ENEMY_TYPES):
      return False
    if (missing_item == zelda_constants.BOW and not self.has_mixed_enemies and
        self.enemy_type in zelda_constants.GOHMA_ENEMY_TYPES):
      return False
    if missing_item in [zelda_constants.RED_RING, zelda_constants.BLUE_RING]:
      if (not self.has_mixed_enemies and
          self.enemy_type in zelda_constants.HARD_COMBAT_ENEMY_TYPES):
        return False
    return True

  def GetStairwayItemNumber(self) -> int:
    return self.stairway_item
  def SetStairwayItemNumber(self, item_type: int) -> None:
    self.stairway_item = item_type

  def HasStairwayPassageRoom(self) -> bool:
    return self.stairway_passage_room >= 0x00
  def GetStairwayPassageRoom(self) -> int:
    return self.stairway_passage_room
  def SetStairwayPassageRoom(self, other_room: int, stairway_num: int) -> None:
    self.stairway_passage_room = other_room
    self.stairway_passage_num = stairway_num

  def GetLeftExit(self) -> int:
    return self.left_exit
  def GetRightExit(self) -> int:
    return self.right_exit

  def MarkAsVisited(self) -> None:
    self.already_visited = True
  def WasAlreadyVisited(self) -> bool:
    return self.already_visited
  def ClearVisitMark(self) -> None:
    self.already_visited = False


  def GetItemNumber(self) -> int:
    return self.item_num

  def SetItemNumber(self, item_num: int) -> None:
    assert(item_num >= 0 and item_num <= 0x1F)
    self.item_num = item_num
    
