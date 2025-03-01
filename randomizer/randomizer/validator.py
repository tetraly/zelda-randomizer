#8192192025 ice's seed
from typing import List, Tuple
import logging
from constants import Direction
from .constants import CaveNum, Item, LevelNum, Enemy
from .constants import Range, RoomNum, RoomType, WallType
from .data_table import DataTable
from .inventory import Inventory
from .location import Location
from .room import Room
from .flags import Flags

import logging as log


class Validator(object):
  WHITE_SWORD_CAVE_NUMBER = 2
  MAGICAL_SWORD_CAVE_NUMBER = 3
  NUM_HEARTS_FOR_WHITE_SWORD_ITEM = 5
  NUM_HEARTS_FOR_MAGICAL_SWORD_ITEM = 12
  POTION_SHOP_NUMBER = 10
  ARMOS_VIRTUAL_CAVE_NUMBER = 0x14
  COAST_VIRTUAL_CAVE_NUMBER = 0x15

  def __init__(self, data_table: DataTable, flags: Flags) -> None:
    self.data_table = data_table
    self.flags = flags
    self.inventory = Inventory()

  def GetAccessibleDestinations(self):
    tbr = []
    tbr.extend(self.data_table.GetAvailableOverworldCaves("Open"))
    if self.inventory.HasSwordOrWand():
      tbr.extend(self.data_table.GetAvailableOverworldCaves("Bomb"))
      if self.inventory.Has(Item.LADDER):
        tbr.extend(self.data_table.GetAvailableOverworldCaves("Ladder+Bomb"))
    if self.inventory.HasCandle():
      tbr.extend(self.data_table.GetAvailableOverworldCaves("Candle"))
    if self.inventory.Has(Item.RECORDER):
      tbr.extend(self.data_table.GetAvailableOverworldCaves("Recorder"))
    if self.inventory.Has(Item.RAFT):
      tbr.extend(self.data_table.GetAvailableOverworldCaves("Raft"))
    if self.inventory.Has(Item.POWER_BRACELET):
      tbr.extend(self.data_table.GetAvailableOverworldCaves("Power Bracelet"))
    return list(set(tbr))


  def IsSeedValid(self) -> bool:
    log.info("Starting check of whether the seed is valid or not")
    self.inventory.Reset()
    self.inventory.SetStillMakingProgressBit()
    num_iterations = 0
    while self.inventory.StillMakingProgress():
      num_iterations += 1
      log.info("Iteration %d of checking" % num_iterations)
      log.info("Inventory contains: " + self.inventory.ToString())
      self.inventory.ClearMakingProgressBit()
      self.data_table.ClearAllVisitMarkers()
      log.debug("Checking caves")
      for destination in self.GetAccessibleDestinations():
        if destination in Range.VALID_LEVEL_NUMBERS:
          level_num = destination
          if level_num == 9 and self.inventory.GetTriforceCount() < 8:
            continue
          log.debug("Can access level %d" % level_num)
          self.ProcessLevel(level_num)
        else:
          cave_num = destination - 0x10
          log.debug("Can access cave type %x" % cave_num)
          if self.CanGetItemsFromCave(cave_num):
            for position_num in Range.VALID_CAVE_POSITION_NUMBERS:
              location = Location(cave_num=cave_num, position_num=position_num)
              self.inventory.AddItem(self.data_table.GetCaveItem(location), location)
      if self.CanEnterLevel(9):
        pass
      if self.inventory.Has(Item.KIDNAPPED_RESCUED_VIRTUAL_ITEM):
        log.info("Seed appears to be beatable. :)")
        return True
      elif num_iterations > 100:
        return False
    log.info("Seed doesn't appear to be beatable. :(")
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
    if room.GetType() == RoomType.T_ROOM:
      return False
    return True

  def CanDefeatEnemies(self, room: Room) -> bool:
    if room.HasNoEnemiesToKill():
      return True
    if ((room.HasTheBeast() and not self.inventory.HasBowSilverArrowsAndSword())
        or (room.HasDigdogger() and not self.inventory.HasRecorderAndReusableWeapon())
        or (room.HasGohma() and not self.inventory.HasBowAndArrows())
        or (room.HasWizzrobes() and not self.inventory.HasSword())
        or (room.GetEnemy().IsGleeokOrPatra() and not self.inventory.HasSwordOrWand())
        or (room.HasOnlyZeroHPEnemies() and not self.inventory.HasReusableWeaponOrBoomerang())
        or (room.HasHungryGoriya() and not self.inventory.Has(Item.BAIT))):
      return False
    if (room.HasPolsVoice()
        and not (self.inventory.HasSwordOrWand() or self.inventory.HasBowAndArrows())):
      return False
    if (self.flags.avoid_required_hard_combat and room.HasHardCombatEnemies()
        and not (self.inventory.HasRing() and self.inventory.Has(Item.WHITE_SWORD))):
      return False

    # At this point, assume regular enemies
    return self.inventory.HasReusableWeapon()

  #TODO: Need to update WS and MS caves with actual heart requirements
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

  def ProcessLevel(self, level_num: int) -> None:
      rooms_to_visit = [(self.data_table.GetLevelStartRoomNumber(level_num), 
                         self.data_table.GetLevelEntranceDirection(level_num))]
      while True:
          room_num, direction = rooms_to_visit.pop()
          new_rooms = self._VisitRoom(level_num, room_num, direction)
          if new_rooms:
              rooms_to_visit.extend(new_rooms)
          if not rooms_to_visit:
              break
      
  def _VisitRoom(self,
                 level_num: int,
                 room_num: int,
                 entry_direction: Direction) -> List[Tuple[int, Direction]]:
      if room_num not in range(0, 0x80):
        return
      room = self.data_table.GetRoom(level_num, room_num)
      if room.IsMarkedAsVisited():
        return
      log.debug("Visiting level %d room %x" % (level_num, room_num))
      room.MarkAsVisited()
      tbr = []

      if self.CanGetRoomItem(entry_direction, room) and room.HasItem():
          self.inventory.AddItem(room.GetItem(), Location.LevelRoom(level_num, room_num))
      if room.GetEnemy() == Enemy.THE_BEAST and self.CanGetRoomItem(entry_direction, room):
          self.inventory.AddItem(Item.BEAST_DEFEATED_VIRTUAL_ITEM, Location.LevelRoom(level_num, room_num))
      if room.GetEnemy() == Enemy.THE_KIDNAPPED:
          self.inventory.AddItem(Item.KIDNAPPED_RESCUED_VIRTUAL_ITEM, Location.LevelRoom(level_num, room_num))

      for direction in (Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH):
        if self.CanMove(entry_direction, direction, level_num, room_num, room):
          tbr.append((room_num + direction, Direction(-1 * entry_direction)))

      # Only check for stairways if this room is configured to have a stairway entrance
      if not self._HasStairway(room):
          return tbr      
      
      for stairway_room_num in self.data_table.GetLevelStaircaseRoomNumberList(level_num):
          stairway_room = self.data_table.GetRoom(level_num, stairway_room_num)
          left_exit = stairway_room.GetLeftExit()
          right_exit = stairway_room.GetRightExit()

          # Item staircase. Add the item to our inventory.
          if left_exit == room_num and right_exit == room_num:
              self.inventory.AddItem(
                  stairway_room.GetItem(), Location.LevelRoom(level_num, stairway_room_num))
          # Transport stairway cases. Add the connecting room to be checked.
          elif left_exit == room_num and right_exit != room_num:
                tbr.append((right_exit, direction.NO_DIRECTION))
                # Stop looking for additional staircases after finding one
                break
          elif right_exit == room_num and left_exit != room_num:
                tbr.append((left_exit, direction.NO_DIRECTION))
                # Stop looking for additional staircases after finding one
                break
      return tbr

  def _HasStairway(self, room: Room) -> bool:
        room_type = room.GetType()

        # Spiral Stair, Narrow Stair, and Diamond Stair rooms always have a staircase
        if room_type.HasOpenStaircase():
            return True

        # Check if there are any shutter doors in this room. If so, they'll open when a middle
        # row pushblock is pushed instead of a stairway appearing
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            if room.GetWallType(direction) == WallType.SHUTTER_DOOR:
                return False

        # Check if "Movable block" bit is set in a room_type that has a middle row pushblock
        if room_type.CanHavePushBlock() and room.HasMovableBlockBitSet():
            return True
        return False


  def CanMove(self, entry_direction: Direction, exit_direction: Direction, level_num: LevelNum,
              room_num: RoomNum, room: Room) -> bool:
    if (room.PathUnconditionallyObstructed(entry_direction, exit_direction)
        or room.PathObstructedByWater(entry_direction, exit_direction,
                                      self.inventory.Has(Item.LADDER))):
      return False

    # Hungry goriya room doesn't have a closed shutter door.  So need a special check to similate how
    # it's not possible to move up in the room until the goriya has been properly fed.
    if (exit_direction == Direction.NORTH and room.HasHungryGoriya() and not self.inventory.Has(Item.BAIT)):
      log.debug("Hungry goriya is still hungry :(")
      return False

    wall_type = room.GetWallType(exit_direction)
    if wall_type == WallType.SHUTTER_DOOR and level_num == 9:
      next_room = self.data_table.GetRoom(level_num, room_num + exit_direction)
      if next_room.GetEnemy() == Enemy.THE_KIDNAPPED:
        return self.inventory.Has(Item.BEAST_DEFEATED_VIRTUAL_ITEM)
     
    if (wall_type == WallType.SOLID_WALL
        or (wall_type == WallType.SHUTTER_DOOR and not self.CanDefeatEnemies(room))):
      return False

    # Disable key checking for now
    #if wall_type in [WallType.LOCKED_DOOR_1, WallType.LOCKED_DOOR_2]:
    #  if self.inventory.HasKey():
    #    self.inventory.UseKey(level_num, room_num, exit_direction)
    #  else:
    #    return False
    return True
