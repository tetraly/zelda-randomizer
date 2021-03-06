from typing import Dict, List
from absl import logging
from .constants import CaveNum, Item, LevelNum, Range, RoomNum
from .room import Room
from .location import Location
from .cave import Cave
from .patch import Patch
from .data import *


class DataTable():
  NES_FILE_OFFSET = 0x10
  LEVEL_1_TO_6_DATA_START_ADDRESS = 0x18700 + NES_FILE_OFFSET
  LEVEL_7_TO_9_DATA_START_ADDRESS = 0x18A00 + NES_FILE_OFFSET
  LEVEL_TABLE_SIZE = 0x80
  NUM_BYTES_OF_DATA_PER_ROOM = 6
  CAVE_ITEM_DATA_START_ADDRESS = 0x18600 + NES_FILE_OFFSET
  CAVE_PRICE_DATA_START_ADDRESS = 0x1863C + NES_FILE_OFFSET
  CAVE_NUMBER_REPRESENTING_ARMOS_ITEM = 0x14
  CAVE_NUMBER_REPRESENTING_COAST_ITEM = 0x15
  ARMOS_ITEM_ADDRESS = 0x10CF5 + NES_FILE_OFFSET
  COAST_ITEM_ADDRESS = 0x1788A + NES_FILE_OFFSET
  COMPASS_ROOM_NUMBER_ADDRESS = 0x1942C + NES_FILE_OFFSET
  SPECIAL_DATA_LEVEL_OFFSET = 0xFC

  # Generated by running:
  # f = open("vanilla-z1-rom.nes", "rb")
  # for a in range(0, 9):
  #   f.seek(0x1942B + 0x10 + 0xfc * a)
  #   print ("%x" % int.from_bytes(f.read(1), byteorder="big"))
  LEVEL_START_ROOM_NUMBERS = [
      RoomNum(0x73),
      RoomNum(0x7d),
      RoomNum(0x7c),
      RoomNum(0x71),
      RoomNum(0x76),
      RoomNum(0x79),
      RoomNum(0x79),
      RoomNum(0x7e),
      RoomNum(0x76)
  ]

  STAIRCASE_LISTS: Dict[int, List[RoomNum]] = {
      1: [RoomNum(0x7f)],
      2: [],
      3: [RoomNum(0x0f)],
      4: [RoomNum(0x60)],
      5: [RoomNum(0x07), RoomNum(0x04)],
      6: [RoomNum(0x08), RoomNum(0x75)],
      7: [RoomNum(0x7b), RoomNum(0x4a)],
      8: [RoomNum(0x2f), RoomNum(0x0f), RoomNum(0x6f)],
      9: [
          RoomNum(0x60),
          RoomNum(0x70),
          RoomNum(0x72),
          RoomNum(0x75),
          RoomNum(0x67),
          RoomNum(0x77),
          RoomNum(0x00),
          RoomNum(0x4f)
      ]
  }

  def __init__(self) -> None:
    self.level_1_to_6_raw_data = list(
        open("randomizer/randomizer/data/level-1-6-data.bin", 'rb').read(0x300))
    self.level_7_to_9_raw_data = list(
        open("randomizer/randomizer/data/level-7-9-data.bin", 'rb').read(0x300))
    self.overworld_cave_raw_data = list(
        open("randomizer/randomizer/data/overworld-cave-data.bin", 'rb').read(0x80))
    self.level_1_to_6_rooms: List[Room] = []
    self.level_7_to_9_rooms: List[Room] = []
    self.overworld_caves: List[Cave] = []
    self.triforce_locations: Dict[LevelNum, RoomNum] = {}

  def ResetToVanilla(self) -> None:
    self.level_1_to_6_rooms = self._ReadDataForLevelGrid(self.level_1_to_6_raw_data)
    self.level_7_to_9_rooms = self._ReadDataForLevelGrid(self.level_7_to_9_raw_data)
    self._ReadDataForOverworldCaves()
    self.triforce_locations = {}

  def _ReadDataForLevelGrid(self, level_data: List[int]) -> List[Room]:
    rooms: List[Room] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data: List[int] = []
      for byte_num in range(0, self.NUM_BYTES_OF_DATA_PER_ROOM):
        room_data.append(level_data[byte_num * self.LEVEL_TABLE_SIZE + room_num])
      rooms.append(Room(room_data))
    return rooms

  def _ReadDataForOverworldCaves(self) -> None:
    self.overworld_caves = []
    for cave_num in Range.VALID_CAVE_NUMBERS:
      if cave_num == self.CAVE_NUMBER_REPRESENTING_ARMOS_ITEM:
        self.overworld_caves.append(Cave([0x3F, Item.POWER_BRACELET, 0x7F, 0x00, 0x00, 0x00]))
      elif cave_num == self.CAVE_NUMBER_REPRESENTING_COAST_ITEM:
        self.overworld_caves.append(Cave([0x3F, Item.HEART_CONTAINER, 0x7F, 0x00, 0x00, 0x00]))
      else:
        assert cave_num in range(0, 0x14)
        cave_data: List[int] = []
        for cave_item_byte_num in range(0, 3):
          cave_data.append(self.overworld_cave_raw_data[(3 * cave_num) + cave_item_byte_num])
        for cave_price_byte_num in range(0, 3):
          cave_data.append(
              self.overworld_cave_raw_data[0x3C + (3 * cave_num) + cave_price_byte_num])
        self.overworld_caves.append(Cave(cave_data))
    assert len(self.overworld_caves) == 22  # 0-19 are actual caves, 20-21 are for the armos/coast

  def GetRoom(self, level_num: LevelNum, room_num: RoomNum) -> Room:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    assert room_num in Range.VALID_ROOM_NUMBERS

    if level_num in [7, 8, 9]:
      return self.level_7_to_9_rooms[room_num]
    return self.level_1_to_6_rooms[room_num]

  def GetRoomItem(self, location: Location) -> Item:
    assert location.IsLevelRoom()
    if location.GetLevelNum() in [7, 8, 9]:
      return self.level_7_to_9_rooms[location.GetRoomNum()].GetItem()
    return self.level_1_to_6_rooms[location.GetRoomNum()].GetItem()

  def SetRoomItem(self, location: Location, item: Item) -> None:
    assert location.IsLevelRoom()
    if location.GetLevelNum() in [7, 8, 9]:
      self.level_7_to_9_rooms[location.GetRoomNum()].SetItem(item)
    else:
      self.level_1_to_6_rooms[location.GetRoomNum()].SetItem(item)

  def GetCaveItem(self, location: Location) -> Item:
    assert location.IsCavePosition()
    return self.overworld_caves[location.GetCaveNum()].GetItemAtPosition(location.GetPositionNum())

  def SetCaveItem(self, location: Location, item: Item) -> None:
    assert location.IsCavePosition()
    self.overworld_caves[location.GetCaveNum()].SetItemAtPosition(item, location.GetPositionNum())

  def UpdateTriforceLocation(self, location: Location) -> None:
    room_num = location.GetRoomNum()
    room = self.GetRoom(location.GetLevelNum(), room_num)
    if room.IsItemStaircase():
      room_num = room.GetLeftExit()
    self.triforce_locations[location.GetLevelNum()] = room_num

  def ClearAllVisitMarkers(self) -> None:
    logging.debug("Clearing Visit markers")
    for room in self.level_1_to_6_rooms:
      room.ClearVisitMark()
    for room in self.level_7_to_9_rooms:
      room.ClearVisitMark()

  # Gets the Room number of the start screen for a level.
  def GetLevelStartRoomNumber(self, level_num: LevelNum) -> RoomNum:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    return self.LEVEL_START_ROOM_NUMBERS[level_num - 1]

  # Gets a list of staircase rooms for a level.
  #
  # Note that this will include not just passage staircases between two
  # dungeon rooms but also item rooms with only one passage two and
  # from a dungeon room.
  def GetLevelStaircaseRoomNumberList(self, level_num: LevelNum) -> List[RoomNum]:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    return self.STAIRCASE_LISTS[level_num]

  def GetPatch(self) -> Patch:
    patch = Patch()
    patch += self._GetPatchForLevelGrid(self.LEVEL_1_TO_6_DATA_START_ADDRESS,
                                        self.level_1_to_6_rooms)
    patch += self._GetPatchForLevelGrid(self.LEVEL_7_TO_9_DATA_START_ADDRESS,
                                        self.level_7_to_9_rooms)
    patch += self._GetPatchForOverworldCaveData()
    return patch

  def _GetPatchForLevelGrid(self, start_address: int, rooms: List[Room]) -> Patch:
    patch = Patch()
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data = rooms[room_num].GetRomData()
      assert len(room_data) == self.NUM_BYTES_OF_DATA_PER_ROOM

      for table_num in range(0, self.NUM_BYTES_OF_DATA_PER_ROOM):
        patch.AddData(start_address + table_num * self.LEVEL_TABLE_SIZE + room_num,
                      [room_data[table_num]])
    # Write Triforce room location to update where the compass displays it in levels 1-8.
    # The room the compass points to in level 9 doesn't change.
    for level_num in range(1, 9):
      assert level_num in self.triforce_locations
      patch.AddData(
          self.COMPASS_ROOM_NUMBER_ADDRESS + (level_num - 1) * self.SPECIAL_DATA_LEVEL_OFFSET,
          [self.triforce_locations[level_num]])
    return patch

  def _GetPatchForOverworldCaveData(self) -> Patch:
    patch = Patch()
    for cave_num in Range.VALID_CAVE_NUMBERS:
      if cave_num == self.CAVE_NUMBER_REPRESENTING_ARMOS_ITEM:
        patch.AddData(self.ARMOS_ITEM_ADDRESS,
                      [self.overworld_caves[cave_num].GetItemAtPosition(2)])
        continue
      if cave_num == self.CAVE_NUMBER_REPRESENTING_COAST_ITEM:
        patch.AddData(self.COAST_ITEM_ADDRESS,
                      [self.overworld_caves[cave_num].GetItemAtPosition(2)])
        continue

      # Note that the Cave class is responsible for protecting bits 6 and 7 in its item data
      patch.AddData(self.CAVE_ITEM_DATA_START_ADDRESS + (3 * cave_num),
                    self.overworld_caves[cave_num].GetItemData())
      patch.AddData(self.CAVE_PRICE_DATA_START_ADDRESS + (3 * cave_num),
                    self.overworld_caves[cave_num].GetPriceData())
    return patch
