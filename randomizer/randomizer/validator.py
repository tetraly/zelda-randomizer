from .constants import CaveNum, Direction, Item, LevelNum
from .constants import Range, RoomNum, RoomType, WallType
from .data_table import DataTable
from .inventory import Inventory
from .room import Room
from .settings import Settings


class InvalidItemPlacementException(Exception):
  pass


class Validator(object):
  WHITE_SWORD_CAVE_NUMBER = 2
  MAGICAL_SWORD_CAVE_NUMBER = 3
  NUM_HEARTS_FOR_WHITE_SWORD_ITEM = 5
  NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM = 12
  POTION_SHOP_NUMBER = 10
  COAST_VIRTUAL_CAVE_NUMBER = 21

  def __init__(self, data_table: DataTable, settings: Settings) -> None:
    self.data_table = data_table
    self.settings = settings
    self.inventory = Inventory()

  def IsSeedValid(self) -> bool:
    self.inventory.Reset()
    self.inventory.SetStillMakingProgressBit()
    while self.inventory.StillMakingProgress():
      self.inventory.ClearMakingProgressBit()
      self.data_table.ClearAllVisitMarkers()
      for cave_num in Range.VALID_CAVE_NUMBERS:
        if self.CanGetItemsFromCave(cave_num):
          self.inventory.AddMultipleItems(self.data_table.GetAllCaveItems(cave_num))
      for level_num in Range.VALID_LEVEL_NUMBERS:
        if self.CanEnterLevel(level_num):
          try:
            self._RecursivelyTraverseLevel(level_num,
                                           self.data_table.GetLevelStartRoomNumber(level_num),
                                           Direction.NORTH)
          except InvalidItemPlacementException:
            return False
      if self.inventory.Has(Item.TRIFORCE_OF_POWER):
        return True
    return False

  def CanGetRoomItem(self, entry_direction: Direction, room: Room) -> bool:
    # Can't pick up a room in any rooms with water/moats without a ladder.
    # TODO: Make a better determination here based on the drop location and the entry direction.
    if room.HasPotentialLadderBlock() and not self.inventory.Has(Item.LADDER):
      return False
    if room.HasDropBitSet() and not self.CanDefeatEnemies(room):
      return False
    if (room.GetType() == RoomType.HORIZONTAL_CHUTE_ROOM
        and entry_direction in [Direction.NORTH, Direction.SOUTH]):
      return False
    if (room.GetType() == RoomType.VERTICAL_CHUTE_ROOM
        and entry_direction in [Direction.EAST, Direction.WEST]):
      return False
    return True

  def CanDefeatEnemies(self, room: Room) -> bool:
    if room.HasNoEnemiesToKill():
      return True
    if ((room.HasGannon() and not self.inventory.HasBowSilverArrowsAndSword())
        or (room.HasDigdogger() and not self.inventory.HasRecorderAndReusableWeapon())
        or (room.HasGohma() and not self.inventory.HasBowAndArrows())
        or (room.HasWizzrobes() and not self.inventory.HasSword())
        or (room.HasSwordOrWandRequiredEnemies() and not self.inventory.HasSwordOrWand())
        or (room.HasOnlyZeroHPEnemies() and not self.inventory.HasReusableWeaponOrBoomerang())
        or (room.HasHungryGoriya() and not self.inventory.Has(Item.BAIT))):
      return False
    if (room.HasPolsVoice()
        and not (self.inventory.HasSwordOrWand() or self.inventory.HasBowAndArrows())):
      return False

    if (self.settings.avoid_required_hard_combat and room.HasHardCombatEnemies()
        and not (self.inventory.HasRing() and self.inventory.Has(Item.WHITE_SWORD))):
      return False

    # At this point, assume regular enemies
    return self.inventory.HasReusableWeapon()

  def CanGetItemsFromCave(self, cave_num: CaveNum) -> bool:
    if (cave_num == self.WHITE_SWORD_CAVE_NUMBER
        and self.inventory.GetHeartCount() < self.NUM_HEARTS_FOR_WHITE_SWORD_ITEM):
      return False
    if (cave_num == self.MAGICAL_SWORD_CAVE_NUMBER
        and self.inventory.GetHeartCount() < self.NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM):
      return False
    if cave_num == self.POTION_SHOP_NUMBER and not self.inventory.Has(Item.LETTER):
      return False
    if cave_num == self.COAST_VIRTUAL_CAVE_NUMBER and not self.inventory.Has(Item.LADDER):
      return False
    return True

  def CanEnterLevel(self, level_num: LevelNum) -> bool:
    if level_num == 4 and not self.inventory.Has(Item.RAFT):
      return False
    if level_num == 7 and not self.inventory.Has(Item.RECORDER):
      return False
    if level_num == 8 and not self.inventory.HasCandle():
      return False
    if level_num == 9 and self.inventory.GetTriforceCount() < 8:
      return False
    return True

  def _RecursivelyTraverseLevel(self, level_num: LevelNum, room_num: RoomNum,
                                entry_direction: Direction) -> None:
    if not room_num in Range.VALID_ROOM_NUMBERS:
      return  # No escaping back into the overworld! :)
    room = self.data_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()

    if self.CanGetRoomItem(entry_direction, room):
      self.inventory.AddItem(room.GetItem())

    # An item staircase room is a dead-end, so no need to recurse more.
    if room.IsItemStaircase():
      # For some reason, the Magical Sword doesn't show up when it's in an item staircase.
      if room.GetItem() == Item.MAGICAL_SWORD:
        raise InvalidItemPlacementException
      return

    # For a transport staircase, we don't know whether we came in through the left or right.
    # So try to leave both ways; the one that we came from will have already been marked as
    # visited, which won't do anything.
    elif room.IsTransportStaircase():
      for room_num_to_visit in [room.GetLeftExit(), room.GetRightExit()]:
        self._RecursivelyTraverseLevel(
            level_num,
            room_num_to_visit,
            Direction.STAIRCASE,
        )
      return

    # TODO: Add logic for shutter rooms that don't open like in L5
    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
      if self.CanMove(entry_direction, direction, room):
        self._RecursivelyTraverseLevel(level_num, RoomNum(room_num + direction),
                                       Direction(-1 * direction))

    if room.HasUnobstructedStaircase():
      self._RecursivelyTraverseLevel(level_num, room.GetStaircaseRoomNumber(), Direction.STAIRCASE)
    elif room.HasStaircase():
      if self.CanDefeatEnemies(room):
        self._RecursivelyTraverseLevel(level_num, room.GetStaircaseRoomNumber(),
                                       Direction.STAIRCASE)

  def CanMove(self, entry_direction: Direction, exit_direction: Direction, room: Room) -> bool:
    if (room.PathUnconditionallyObstructed(entry_direction, exit_direction)
        or room.PathObstructedByWater(entry_direction, exit_direction,
                                      self.inventory.Has(Item.LADDER))):
      return False
    wall_type = room.GetWallType(exit_direction)
    if (wall_type == WallType.SOLID_WALL
        or (wall_type == WallType.SHUTTER_DOOR and not self.CanDefeatEnemies(room))):
      return False


# TODO: Add this key logic back
#    if wall_type in [WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2
#                     ] and not self.inventory.HasKey():
#      self.inventory.UseKey()
    return True
