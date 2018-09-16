from typing import Dict, List
from absl import logging

from randomizer.constants import Item, LevelNum, Range, RoomNum
from randomizer.level_room import Room
from randomizer.location import Location
from randomizer.overworld_cave import Cave
from randomizer.rom import Rom


class LevelDataTable():
  CAVE_ITEM_DATA_START_ADDRESS = 0x18600
  CAVE_PRICE_DATA_START_ADDRESS = 0x1863C
  CAVE_NUMBER_REPRESENTING_ARMOS_ITEM = 20
  CAVE_NUMBER_REPRESENTING_COAST_ITEM = 21

  LEVEL_1_TO_6_DATA_START_ADDRESS = 0x18700
  LEVEL_7_TO_9_DATA_START_ADDRESS = 0x18A00
  LEVEL_TABLE_SIZE = 0x80
  OVERWORLD_TABLE_SIZE = 0x80
  NUM_BYTES_OF_DATA_PER_ROOM = 6
  NUM_BYTES_OF_DATA_PER_SCREEN = 6

  LEVEL_3_RAFT_ROOM_NUMBER = RoomNum(0x0F)
  STAIRCASE_ROOM_NUMBER_SENTINEL_VALUE = 0xFF
  SPECIAL_DATA_LEVEL_OFFSET = 0xFC
  SPECIAL_DATA_ADDRESSES = {
      "start_room": 0x1942B,
      "triforce_room": 0x1942C,
      "staircase_data": 0x19430
  }

  ARMOS_ITEM_ADDRESS = 0x10CF5
  COAST_ITEM_ADDRESS = 0x1788A

  def __init__(self, rom: Rom) -> None:
    self.rom = rom
    self._ClearTables()

  def _ClearTables(self) -> None:
    self.level_1_to_6_rooms: List[Room] = []
    self.level_7_to_9_rooms: List[Room] = []
    self.overworld_caves: List[Cave] = []
    # self.overworld_screens: List[Screen] = []
    self.triforce_locations: Dict[LevelNum, RoomNum] = {}
    """self.level_1_to_6_rooms = []
    self.level_7_to_9_rooms = []
    self.overworld_caves = []
    self.triforce_locations = {}"""

  def ReadDataFromRom(self) -> None:
    self._ClearTables()
    self.level_1_to_6_rooms = self._ReadDataForLevelGrid(self.LEVEL_1_TO_6_DATA_START_ADDRESS)
    self.level_7_to_9_rooms = self._ReadDataForLevelGrid(self.LEVEL_7_TO_9_DATA_START_ADDRESS)
    self._ReadDataForOverworldCaves()
    # self._ReadDataForOverworldScreens()

  def _ReadDataForLevelGrid(self, start_address: int) -> List[Room]:
    rooms: List[Room] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      raw_data: List[int] = []
      for byte_num in range(0, self.NUM_BYTES_OF_DATA_PER_ROOM):
        raw_data.append(
            self.rom.ReadByte(start_address + byte_num * self.LEVEL_TABLE_SIZE + room_num))
      rooms.append(Room(raw_data))
    return rooms

  # TODO: Refactor this with _ReadDataForLevelGrid since they're so similar
  """def _ReadDataForOverworldScreens(self) -> None:
    for screen_num in Range.VALID_SCREEN_NUMBERS:
      raw_data: List[int] = []
      for byte_num in range(0, self.NUM_BYTES_OF_DATA_PER_SCREEN):
        raw_data.append(
            self.rom.ReadByte(start_address + byte_num * self.OVERWORLD_TABLE_SIZE + screen_num))
      self.overworld_screens.append(Screen(raw_data))"""

  def _ReadDataForOverworldCaves(self) -> None:
    for cave_num in Range.VALID_CAVE_NUMBERS:
      if cave_num == self.CAVE_NUMBER_REPRESENTING_ARMOS_ITEM:
        armos_item = self.rom.ReadByte(self.ARMOS_ITEM_ADDRESS)
        self.overworld_caves.append(Cave([0x3F, armos_item, 0x7F, 0x00, 0x00, 0x00]))
        assert armos_item == self.overworld_caves[
            self.CAVE_NUMBER_REPRESENTING_ARMOS_ITEM].GetItemAtPosition(2)
      elif cave_num == self.CAVE_NUMBER_REPRESENTING_COAST_ITEM:
        coast_item = self.rom.ReadByte(self.COAST_ITEM_ADDRESS)
        self.overworld_caves.append(Cave([0x3F, coast_item, 0x7F, 0x00, 0x00, 0x00]))
        assert coast_item == self.overworld_caves[
            self.CAVE_NUMBER_REPRESENTING_COAST_ITEM].GetItemAtPosition(2)
      else:
        assert cave_num in range(0, 20)
        data: List[int] = []
        data.extend(self.rom.ReadBytes(self.CAVE_ITEM_DATA_START_ADDRESS + 3 * cave_num, 3))
        data.extend(self.rom.ReadBytes(self.CAVE_PRICE_DATA_START_ADDRESS + 3 * cave_num, 3))
        self.overworld_caves.append(Cave(data))
    assert len(self.overworld_caves) == 22  # 0-19 are actual caves, 20-21 are for the armos/coast

  def GetRoom(self, level_num: LevelNum, room_num: RoomNum) -> Room:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    assert room_num in Range.VALID_ROOM_NUMBERS

    if level_num in [7, 8, 9]:
      return self.level_7_to_9_rooms[room_num]
    return self.level_1_to_6_rooms[room_num]

  # def GetScreen(self, screen_num: ScreenNum) -> Screen:
  #   return self.overworld_screens[screen_num]

  def GetRoomItem(self, location: Location) -> Item:
    assert location.IsLevelRoom()
    if location.GetLevelNum() in [7, 8, 9]:
      return self.level_7_to_9_rooms[location.GetRoomNum()].GetItem()
    return self.level_1_to_6_rooms[location.GetRoomNum()].GetItem()

  def GetCaveItem(self, location: Location) -> Item:
    assert location.IsCavePosition()
    return self.overworld_caves[location.GetCaveNum()].GetItemAtPosition(location.GetPositionNum())

  def SetRoomItem(self, location: Location, item: Item) -> None:
    assert location.IsLevelRoom()
    if location.GetLevelNum() in [7, 8, 9]:
      self.level_7_to_9_rooms[location.GetRoomNum()].SetItem(item)
    else:
      self.level_1_to_6_rooms[location.GetRoomNum()].SetItem(item)

  def SetCaveItem(self, location: Location, item: Item) -> None:
    assert location.IsCavePosition()
    self.overworld_caves[location.GetCaveNum()].SetItemAtPosition(item, location.GetPositionNum())

  def ClearAllVisitMarkers(self) -> None:
    logging.debug("Clearing Visit markers")
    for room in self.level_1_to_6_rooms:
      room.ClearVisitMark()
    for room in self.level_7_to_9_rooms:
      room.ClearVisitMark()

  def WriteDataToRom(self) -> None:
    logging.debug("Beginning to write level/overworld data to disk.")
    self._WriteDataForLevelGrid(self.LEVEL_1_TO_6_DATA_START_ADDRESS, self.level_1_to_6_rooms)
    self._WriteDataForLevelGrid(self.LEVEL_7_TO_9_DATA_START_ADDRESS, self.level_7_to_9_rooms)
    self._WriteOverworldItemDataToRom()

  def _WriteDataForLevelGrid(self, start_address: int, rooms: List[Room]) -> None:
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data = rooms[room_num].GetRomData()
      assert len(room_data) == self.NUM_BYTES_OF_DATA_PER_ROOM

      for table_num in range(0, self.NUM_BYTES_OF_DATA_PER_ROOM):
        self.rom.WriteByte(
            address=start_address + table_num * self.LEVEL_TABLE_SIZE + room_num,
            data=room_data[table_num])

    # Write Triforce room location to update where the compass displays it in levels 1-8.
    # The room the compass points to in level 9 doesn't change.
    for level_num in range(1, 9):
      assert level_num in self.triforce_locations
      triforce_room_address = self._GetSpecialDataAddressForLevel("triforce_room", level_num)
      self.rom.WriteByte(triforce_room_address, self.triforce_locations[level_num])

  def _WriteOverworldItemDataToRom(self) -> None:
    for cave_num in Range.VALID_CAVE_NUMBERS:
      if cave_num == self.CAVE_NUMBER_REPRESENTING_ARMOS_ITEM:
        print( "writing %x to %x" % (self.ARMOS_ITEM_ADDRESS,
                           self.overworld_caves[cave_num].GetItemAtPosition(2)))
        self.rom.WriteByte(self.ARMOS_ITEM_ADDRESS,
                           self.overworld_caves[cave_num].GetItemAtPosition(2))
        continue
      if cave_num == self.CAVE_NUMBER_REPRESENTING_COAST_ITEM:
        print( "writing %x to %x" % (self.COAST_ITEM_ADDRESS,
                           self.overworld_caves[cave_num].GetItemAtPosition(2)))
        self.rom.WriteByte(self.COAST_ITEM_ADDRESS,
                           self.overworld_caves[cave_num].GetItemAtPosition(2))
        continue

      # Note that the Cave class is responsible for protecting bits 6 and 7 in its item data
      self.rom.WriteBytes(self.CAVE_ITEM_DATA_START_ADDRESS + (3 * cave_num),
                          self.overworld_caves[cave_num].GetItemData())
      self.rom.WriteBytes(self.CAVE_PRICE_DATA_START_ADDRESS + (3 * cave_num),
                          self.overworld_caves[cave_num].GetPriceData())

  def UpdateTriforceLocation(self, location: Location) -> None:
    room_num = location.GetRoomNum()
    room = self.GetRoom(location.GetLevelNum(), room_num)
    if room.IsItemStaircase():
      room_num = room.GetLeftExit()
    self.triforce_locations[location.GetLevelNum()] = room_num

  def _GetSpecialDataAddressForLevel(self, data_type: str, level: int) -> int:
    assert data_type in self.SPECIAL_DATA_ADDRESSES.keys()
    assert level in Range.VALID_LEVEL_NUMBERS
    return self.SPECIAL_DATA_ADDRESSES[data_type] + (level - 1) * self.SPECIAL_DATA_LEVEL_OFFSET

  # Gets the coordinates of the start screen for a level.
  #
  # Params:
  #   level_num: The (1-indexed) level number to get info for.
  # Returns:
  #   The number of the start room, e.g. 0x73 for level 1
  def GetLevelStartRoomNumber(self, level_num: LevelNum) -> RoomNum:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    address = self._GetSpecialDataAddressForLevel("start_room", level_num)
    return RoomNum(self.rom.ReadByte(address))

  # Gets a list of staircase rooms for a level.
  #
  # Note that this will include not just passage staircases between two
  # dungeon rooms but also item rooms with only one passage two and
  # from a dungeon room.
  #
  # Args:
  #  level_num: The 1-indexed level to get information for (int)
  # Returns:
  #  Zero or more bytes containing the staircase room numbers
  def GetLevelStaircaseRoomNumberList(self, level_num: LevelNum) -> List[RoomNum]:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    staircase_list_location = self._GetSpecialDataAddressForLevel("staircase_data", level_num)
    raw_bytes = self.rom.ReadBytes(staircase_list_location, 10)
    staircase_list: List[RoomNum] = []
    for byte in raw_bytes:
      if byte != self.STAIRCASE_ROOM_NUMBER_SENTINEL_VALUE:
        staircase_list.append(RoomNum(byte))

    # This is a hack needed in order to make vanilla L3 work.  For some reason,
    # the vanilla ROM's data for level 3 doesn't include a stairCASE room even
    # though there obviously is one in vanilla level 3.
    #
    # See http://www.romhacking.net/forum/index.php?topic=18750.msg271821#msg271821
    # for more information about why this is the case and this hack is necessary.
    if level_num == 3 and not staircase_list:
      staircase_list.append(self.LEVEL_3_RAFT_ROOM_NUMBER)

    return staircase_list
