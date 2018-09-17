from randomizer.constants import CaveNum, Direction, Item, LevelNum
from randomizer.constants import Range, RoomNum, RoomType, WallType
from randomizer.level_room import Room
from randomizer.inventory import Inventory
from randomizer.level_data_table import LevelDataTable


class NewLogicValidator(object):
  WHITE_SWORD_CAVE_NUMBER = 2
  MAGICAL_SWORD_CAVE_NUMBER = 3
  NUM_HEARTS_FOR_WHITE_SWORD_ITEM = 5
  NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM = 12
  POTION_SHOP_NUMBER = 10
  COAST_VIRTUAL_CAVE_NUMBER = 21

  def __init__(self, level_data_table: LevelDataTable) -> None:
    self.inventory = Inventory()
    self.level_data_table = level_data_table

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
    if ((room.HasGannon() and not self.inventory.HasBowSilverArrowsAndSword())
        or (room.HasDigdogger() and not self.inventory.HasRecorderAndReusableWeapon())
        or (room.HasGohma() and not self.inventory.HasBowAndArrows())
        or (room.HasWizzrobes() and not self.inventory.HasSword())
        or (room.HasSwordOrWandRequiredEnemies() and not self.inventory.HasSwordOrWand())
        or (room.HasOnlyZeroHPEnemies() and not self.inventory.HasReusableWeaponOrBoomerang())
        or (room.HasHungryGoriya and not self.inventory.Has(Item.BAIT))):
      return False
    if (room.HasPolsVoice()
        and not (self.inventory.HasSwordOrWand() or self.inventory.HasBowAndArrows())):
      return False
    if room.HasNoEnemiesToKill():
      return True
    # At this point, assume regular enemies
    return self.inventory.HasReusableWeapon()

  def CanMove(self, entry_direction: Direction, exit_direction: Direction, room: Room) -> bool:
    if exit_direction == Direction.DOWN:
      if not room.HasStaircase():
        return False
      if room.HasUnobstructedStaircase():
        return True
      return self.CanDefeatEnemies(room)

    if (room.PathUnconditionallyObstructed(entry_direction, exit_direction)
        or room.PathObstructedByWater(entry_direction, exit_direction,
                                      self.inventory.Has(Item.LADDER))):
      return False
    wall_type = room.GetWallType(exit_direction)
    if (wall_type == WallType.SOLID_WALL
        or (wall_type == WallType.SHUTTER_DOOR and not self.CanDefeatEnemies(room))):
      return False
    if wall_type in [WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2
                     ] and not self.inventory.HasKey():
      self.inventory.UseKey()
    return True

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

  def FindPathThroughGame(self):
    inventory = Inventory()
    inventory.SetStillMakingProgressBit()
    while self.inventory.StillMakingProgress():
      self.inventory.ClearMakingProgressBit()
      for cave_num in Range.VALID_CAVE_NUMBERS:
        if self.CanGetItemsFromCave(cave_num):
          self.inventory.AddAllItemsInCave(self.level_data_table.GetCave(cave_num))
      for level_num in Range.VALID_LEVEL_NUMBERS:
        if self.CanEnterLevel(level_num):
          self._RecursivelyTraverseLevel(level_num, self.level_data_table.SetStartRoom(level_num),
                                         Direction.UP)

  def _RecursivelyTraverseLevel(self, level_num: LevelNum, room_num: RoomNum,
                                entry_direction: Direction) -> None:
    if not room_num in Range.VALID_ROOM_NUMBERS:
      return  # No escaping back into the overworld! :)
    room = self.level_data_table.GetRoom(level_num, room_num)
    if room.IsMarkedAsVisited():
      return
    room.MarkAsVisited()

    if self.CanGetRoomItem(entry_direction, room):
      self.inventory.AddItem(room.GetItem())

    # An item staircase room is a dead-end, so no need to recurse more.
    if room.IsItemStaircase():
      return

    # For a transport staircase, we don't know whether we came in through the left or right.
    # So try to leave both ways; the one that we came from will have already been marked as
    # visited, which won't do anything.
    elif room.IsTransportStaircase():
      for room_num_to_visit in [room.GetLeftExit(), room.GetRightExit()]:
        self._RecursivelyTraverseLevel(
            level_num,
            room_num_to_visit,
            Direction.UP,
        )
      return

    for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH,
                      Direction.DOWN):
      if self.CanMove(entry_direction, direction, room):
        self._RecursivelyTraverseLevel(level_num, RoomNum(room_num + direction),
                                       Direction(-1 * direction))
