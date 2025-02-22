import logging
from typing import Dict, List
from .constants import CaveNum, Item, LevelNum, Range, RoomNum
from .room import Room
from .location import Location
from .cave import Cave
from .patch import Patch
from rom_reader import RomReader

NES_FILE_OFFSET = 0x10
START_ROOM_OFFSET = 0x2F
STAIRWAY_LIST_OFFSET = 0x34
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


class DataTable():

  def __init__(self, rom_reader: RomReader) -> None:
    self.rom_reader = rom_reader
    self.level_1_to_6_raw_data = self.rom_reader.GetLevelBlock(1)
    self.level_7_to_9_raw_data = self.rom_reader.GetLevelBlock(7)
    self.overworld_cave_raw_data = self.rom_reader.GetLevelBlock(0)[0x80*4:0x80*5]
    self.level_info: List[List[int]] = []
    self._ReadLevelInfo() 
    
    self.level_1_to_6_rooms: List[Room] = []
    self.level_7_to_9_rooms: List[Room] = []
    self.overworld_caves: List[Cave] = []
    self.triforce_locations: Dict[LevelNum, RoomNum] = {}

  def ResetToVanilla(self) -> None:
    self.level_1_to_6_rooms = self._ReadDataForLevelGrid(self.level_1_to_6_raw_data)
    self.level_7_to_9_rooms = self._ReadDataForLevelGrid(self.level_7_to_9_raw_data)
    self._ReadDataForOverworldCaves()
    self.triforce_locations = {}

  def _ReadLevelInfo(self):
    self.is_z1r = True
    for level_num in range(0, 10):
        level_info = self.rom_reader.GetLevelInfo(level_num)
        self.level_info.append(level_info)
        vals = level_info[0x34:0x3E]
        if vals[-1] in range(0, 5):
            continue
        self.is_z1r = False

  def _ReadDataForLevelGrid(self, level_data: List[int]) -> List[Room]:
    rooms: List[Room] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data: List[int] = []
      for byte_num in range(0, NUM_BYTES_OF_DATA_PER_ROOM):
        room_data.append(level_data[byte_num * LEVEL_TABLE_SIZE + room_num])
      rooms.append(Room(room_data))
    return rooms

  def _ReadDataForOverworldCaves(self) -> None:
    self.overworld_caves = []
    for cave_num in Range.VALID_CAVE_NUMBERS:
      if cave_num == CAVE_NUMBER_REPRESENTING_ARMOS_ITEM:
        self.overworld_caves.append(Cave([0x3F, Item.POWER_BRACELET, 0x7F, 0x00, 0x00, 0x00]))
      elif cave_num == CAVE_NUMBER_REPRESENTING_COAST_ITEM:
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
  #def GetLevelStartRoomNumber(self, level_num: LevelNum) -> RoomNum:
  #  assert level_num in Range.VALID_LEVEL_NUMBERS
  #  return self.LEVEL_START_ROOM_NUMBERS[level_num - 1]
    
  def GetLevelStartRoomNumber(self, level_num: int) -> int:
      logging.warning("Level %d start room is %x" % 
                      (level_num, self.level_info[level_num][START_ROOM_OFFSET]))
      return self.level_info[level_num][START_ROOM_OFFSET]


  # Gets a list of staircase rooms for a level.
  #
  # Note that this will include not just passage staircases between two
  # dungeon rooms but also item rooms with only one passage two and
  # from a dungeon room.
  #def GetLevelStaircaseRoomNumberList(self, level_num: LevelNum) -> List[RoomNum]:
  #  assert level_num in Range.VALID_LEVEL_NUMBERS
  #  return self.STAIRCASE_LISTS[level_num]

  def _GetRawLevelStairwayRoomNumberList(self, level_num: int) -> List[int]:
        vals = self.level_info[level_num][
            STAIRWAY_LIST_OFFSET:STAIRWAY_LIST_OFFSET + 10]
        stairway_list = []  # type: List[int]
        for val in vals:
            if val != 0xFF:
                stairway_list.append(val)

        # This is a hack needed in order to make vanilla L3 work.  For some reason,
        # the vanilla ROM's data for level 3 doesn't include a stairway room even
        # though there obviously is one in vanilla level 3.
        #
        # See http://www.romhacking.net/forum/index.php?topic=18750.msg271821#msg271821
        # for more information about why this is the case and why this hack
        # is needed.
        if level_num == 3 and not stairway_list:
            stairway_list.append(0x0F)
        return stairway_list

  def GetLevelStaircaseRoomNumberList(self, level_num: int) -> List[int]:
        stairway_list = self._GetRawLevelStairwayRoomNumberList(level_num)
        # In randomized roms, the last item in the stairway list is the entrance dir.
        if self.is_z1r:
            stairway_list.pop(-1)
        return stairway_list

  def GetPatch(self) -> Patch:
    patch = Patch()
    patch += self._GetPatchForLevelGrid(LEVEL_1_TO_6_DATA_START_ADDRESS,
                                        self.level_1_to_6_rooms)
    patch += self._GetPatchForLevelGrid(LEVEL_7_TO_9_DATA_START_ADDRESS,
                                        self.level_7_to_9_rooms)
    patch += self._GetPatchForOverworldCaveData()
    return patch

  def _GetPatchForLevelGrid(self, start_address: int, rooms: List[Room]) -> Patch:
    patch = Patch()
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data = rooms[room_num].GetRomData()
      assert len(room_data) == NUM_BYTES_OF_DATA_PER_ROOM

      for table_num in range(0, NUM_BYTES_OF_DATA_PER_ROOM):
        patch.AddData(start_address + table_num * LEVEL_TABLE_SIZE + room_num,
                      [room_data[table_num]])
    # Write Triforce room location to update where the compass displays it in levels 1-8.
    # The room the compass points to in level 9 doesn't change.
    for level_num in range(1, 9):
      assert level_num in self.triforce_locations
      patch.AddData(
          COMPASS_ROOM_NUMBER_ADDRESS + (level_num - 1) * SPECIAL_DATA_LEVEL_OFFSET,
          [self.triforce_locations[level_num]])
    return patch

  def _GetPatchForOverworldCaveData(self) -> Patch:
    patch = Patch()
    for cave_num in Range.VALID_CAVE_NUMBERS:
      if cave_num == CAVE_NUMBER_REPRESENTING_ARMOS_ITEM:
        patch.AddData(ARMOS_ITEM_ADDRESS,
                      [self.overworld_caves[cave_num].GetItemAtPosition(2)])
        continue
      if cave_num == CAVE_NUMBER_REPRESENTING_COAST_ITEM:
        patch.AddData(COAST_ITEM_ADDRESS,
                      [self.overworld_caves[cave_num].GetItemAtPosition(2)])
        continue

      # Note that the Cave class is responsible for protecting bits 6 and 7 in its item data
      patch.AddData(CAVE_ITEM_DATA_START_ADDRESS + (3 * cave_num),
                    self.overworld_caves[cave_num].GetItemData())
      patch.AddData(CAVE_PRICE_DATA_START_ADDRESS + (3 * cave_num),
                    self.overworld_caves[cave_num].GetPriceData())
    return patch
