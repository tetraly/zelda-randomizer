from typing import Dict, List
import logging
from .constants import Direction, Enemy, Item, Range, RoomNum, RoomType, WallType

log = logging.getLogger(__name__)


class Room():
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
    if rom_data[4] & 0x1F == 0x03:
      stuff_not_to_change = rom_data[4] & 0xE0
      new_value = stuff_not_to_change + 0x0E
      rom_data[4] = new_value
    self.rom_data = rom_data

    self.marked_as_visited = False
    # -1 is used as a sentinal value indicating a lack of stairway room
    self.staircase_room_num = RoomNum(-1)

  def GetRomData(self) -> List[int]:
    return self.rom_data

  def IsMarkedAsVisited(self) -> bool:
    return self.marked_as_visited

  def MarkAsVisited(self) -> None:
    self.marked_as_visited = True

  def ClearVisitMark(self) -> None:
    self.marked_as_visited = False

  def GetWallType(self, direction: Direction) -> WallType:
    assert self.GetType() not in [RoomType.ITEM_STAIRCASE, RoomType.TRANSPORT_STAIRCASE]
    (table_num, offset) = self.WALL_TYPE_TABLE_NUMBERS_AND_OFFSETS[direction]
    return WallType(self.rom_data[table_num] >> offset & 0x07)

  ### Staircase room methods ###
  def GetLeftExit(self) -> RoomNum:
    return RoomNum(self.rom_data[0] & 0x7F)

  def GetRightExit(self) -> RoomNum:
    return RoomNum(self.rom_data[1] & 0x7F)

  def HasStaircase(self) -> bool:
    # -1 is used as a sentinal value indicating a lack of stairway room
    return self.staircase_room_num != RoomNum(-1)

  def GetStaircaseRoomNumber(self) -> RoomNum:
    return self.staircase_room_num

  def SetStaircaseRoomNumber(self, staircase_room_num: RoomNum) -> None:
    self.staircase_room_num = staircase_room_num
  
    
  ### Room type-related methods ###
  def PathUnconditionallyObstructed(self, from_direction: Direction,
                                    to_direction: Direction) -> bool:
    if (self.GetType() in self.MOVEMENT_CONSTRAINED_ROOMS
        and (from_direction not in
             self.MOVEMENT_CONSTRAINED_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetType()] or to_direction
             not in self.MOVEMENT_CONSTRAINED_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetType()])):
      return True
    return False

  def PathObstructedByWater(self, from_direction: Direction, to_direction: Direction,
                            has_ladder: bool) -> bool:
    if not has_ladder and self.GetType() in self.POTENTIAL_LADDER_BLOCK_ROOMS:
      if (from_direction not in
          self.POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetType()] or to_direction
          not in self.POTENTIAL_LADDER_BLOCK_ROOMS_VALID_TRAVEL_DIRECTIONS[self.GetType()]):
        return True

    return False

  def GetType(self) -> RoomType:
    return RoomType(self.rom_data[3] & 0x3F)

  def HasPotentialLadderBlock(self) -> bool:
    return self.GetType() in self.POTENTIAL_LADDER_BLOCK_ROOMS

  #def HasUnobstructedStaircase(self) -> bool:
  #  return self.GetType() in [RoomType.SPIRAL_STAIR_ROOM, RoomType.NARROW_STAIR_ROOM]

  def IsItemStaircase(self) -> bool:
    return self.GetType() == RoomType.ITEM_STAIRCASE

  def IsTransportStaircase(self) -> bool:
    return self.GetType() == RoomType.TRANSPORT_STAIRCASE

  ### Item-related methods ###
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

  def GetItem(self) -> Item:
    return Item(self.rom_data[4] & 0x1F)

  def HasDropBitSet(self) -> bool:
    assert self.rom_data[5] & 0x04 in [0, 4]
    assert self.rom_data[5] & 0x01 in [0, 1]
    return self.rom_data[5] & 0x04 > 0 and self.rom_data[5] & 0x01 > 0

  def HasMovableBlockBitSet(self) -> bool:
      return ((self.rom_data[3] >> 6) & 0x01) > 0
      
  def HasItem(self) -> bool:
    if self.GetItem() == Item.MAGICAL_SWORD and (self.HasStaircase() or not self.HasDropBitSet()):
      return False
    return True

  ### Enemy-related methods ###
  def GetEnemy(self) -> Enemy:
    enemy_code = self.rom_data[2] & 0x3F
    if self.rom_data[3] & 0x80 > 0:
      enemy_code += 0x40
    return Enemy(enemy_code)

  def HasTheBeast(self) -> bool:
    return self.GetEnemy() == Enemy.THE_BEAST

  #TODO: Make constants for these lists of enemies
  def HasWizzrobes(self) -> bool:
    return self.GetEnemy() in [
        Enemy.RED_WIZZROBE, Enemy.BLUE_WIZZROBE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS, Enemy.BLUE_WIZZROBE_RED_WIZZROBE,
        Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE
    ]

  def HasDigdogger(self) -> bool:
    return self.GetEnemy() in [Enemy.SINGLE_DIGDOGGER, Enemy.TRIPLE_DIGDOGGER]

  def HasGohma(self) -> bool:
    return self.GetEnemy() in [Enemy.RED_GOHMA, Enemy.BLUE_GOHMA]

  def HasHardCombatEnemies(self) -> bool:
    return self.GetEnemy() in [
        Enemy.GLEEOK_1, Enemy.GLEEOK_2, Enemy.GLEEOK_3, Enemy.GLEEOK_4, Enemy.PATRA_1,
        Enemy.PATRA_2, Enemy.BLUE_DARKNUT, Enemy.BLUE_DARKNUT_RED_DARKNUT_GORIYA_BUBBLE,
        Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE, Enemy.BLUE_WIZZROBE,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE_BUBBLE, Enemy.BLUE_WIZZROBE_RED_WIZZROBE_TRAPS,
        Enemy.BLUE_WIZZROBE_RED_WIZZROBE, Enemy.BLUE_WIZZROBE_LIKE_LIKE_BUBBLE
    ]

  def HasPolsVoice(self) -> bool:
    return self.GetEnemy() in [
        Enemy.POLS_VOICE, Enemy.POLS_VOICE_GIBDO_KEESE, Enemy.BLUE_DARKNUT_RED_DARKNUT_POLS_VOICE
    ]

  def HasHungryGoriya(self) -> bool:
    return self.GetEnemy() == Enemy.HUNGRY_GORIYA

  def HasOnlyZeroHPEnemies(self) -> bool:
    return self.GetEnemy() in [
        Enemy.GEL_1, Enemy.GEL_2, Enemy.BLUE_KEESE, Enemy.RED_KEESE, Enemy.DARK_KEESE,
        Enemy.KEESE_TRAPS
    ]

  def HasNoEnemiesToKill(self) -> bool:
    return self.GetEnemy() in [
        Enemy.BUBBLE, Enemy.THREE_PAIRS_OF_TRAPS, Enemy.CORNER_TRAPS, Enemy.OLD_MAN,
        Enemy.THE_KIDNAPPED, Enemy.NOTHING
    ]
