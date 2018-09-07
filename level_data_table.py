from typing import Dict, List
from absl import logging
from constants import Range, LevelNum, RoomNum
from level_room import LevelRoom
from rom import Rom


class LevelDataTable(object):
  LEVEL_1_TO_6_DATA_START_ADDRESS = 0x18700
  LEVEL_7_TO_9_DATA_START_ADDRESS = 0x18A00
  LEVEL_TABLE_SIZE = 0x80
  LEVEL_1_START_ROOM_ADDRESS = 0x1942B
  LEVEL_1_TRIFORCE_ROOM_ADDRESS = 0x1942C
  LEVEL_1_STAIRCASE_DATA_ADDRESS = 0x19430
  LEVEL_3_RAFT_ROOM_NUMBER = RoomNum(0x0F)
  STAIRCASE_START_ROOM_LEVEL_OFFSET = 0xFC
  STAIRCASE_ROOM_NUMBER_SENTINEL_VALUE = 0xFF

  def __init__(self, rom: Rom) -> None:
    self.rom = rom
    self.level_1_to_6_level_rooms: List[LevelRoom] = []
    self.level_7_to_9_level_rooms: List[LevelRoom] = []
    self.triforce_locations: Dict[LevelNum, RoomNum] = {}

  def _ClearTables(self) -> None:
    self.level_1_to_6_level_rooms = []
    self.level_7_to_9_level_rooms = []
    self.triforce_locations = {}

  def _ReadLevelDataForLevelGrid(self, table_start_address: int) -> List[LevelRoom]:
    level_rooms: List[LevelRoom] = []
    for room_num in Range.VALID_ROOM_NUMBERS:
      raw_data = []
      for table_num in Range.VALID_TABLE_NUMBERS:
        raw_data.append(
            self.rom.ReadByte(table_start_address + table_num * self.LEVEL_TABLE_SIZE + room_num))
      level_rooms.append(LevelRoom(raw_data))
    return level_rooms

  def ReadLevelDataFromRom(self):
    self._ClearTables()
    self.level_1_to_6_level_rooms = self._ReadLevelDataForLevelGrid(
        self.LEVEL_1_TO_6_DATA_START_ADDRESS)
    self.level_7_to_9_level_rooms = self._ReadLevelDataForLevelGrid(
        self.LEVEL_7_TO_9_DATA_START_ADDRESS)

  def _WriteLevelDataForLevelGrid(self, table_start_address, level_rooms) -> None:
    for room_num in Range.VALID_ROOM_NUMBERS:
      room_data = level_rooms[room_num].GetRomData()
      assert len(room_data) == len(Range.VALID_TABLE_NUMBERS)

      assert len(Range.VALID_TABLE_NUMBERS) == 6  # !!! Take out

      for table_num in Range.VALID_TABLE_NUMBERS:
        self.rom.WriteByte(
            address=table_start_address + table_num * self.LEVEL_TABLE_SIZE + room_num,
            data=room_data[table_num])

    # Write Triforce room location to update where the compass displays it in levels 1-8.
    # The room the compass points to in level 9 doesn't change.
    for level_num in range(1, 9):
      assert level_num in self.triforce_locations
      triforce_room_address = (self.LEVEL_1_TRIFORCE_ROOM_ADDRESS +
                               self.STAIRCASE_START_ROOM_LEVEL_OFFSET * (level_num - 1))
      self.rom.WriteByte(triforce_room_address, self.triforce_locations[level_num])

  def WriteLevelDataToRom(self):
    logging.debug("Beginning to write level data to disk.")
    self._WriteLevelDataForLevelGrid(self.LEVEL_1_TO_6_DATA_START_ADDRESS,
                                     self.level_1_to_6_level_rooms)
    self._WriteLevelDataForLevelGrid(self.LEVEL_7_TO_9_DATA_START_ADDRESS,
                                     self.level_7_to_9_level_rooms)

  def UpdateTriforceLocation(self, level_num: LevelNum, room_num: RoomNum):
    self.triforce_locations[level_num] = room_num

  def GetLevelRoom(self, level_num: LevelNum, room_num: RoomNum) -> LevelRoom:
    assert room_num in Range.VALID_ROOM_NUMBERS
    assert level_num in Range.VALID_LEVEL_NUMBERS
    if level_num in [7, 8, 9]:
      return self.level_7_to_9_level_rooms[room_num]
    return self.level_1_to_6_level_rooms[room_num]

  def ClearAllVisitMarkers(self):
    logging.debug("Clearing Visit markers")
    for level_room in self.level_1_to_6_level_rooms:
      level_room.ClearVisitMark()
    for level_room in self.level_7_to_9_level_rooms:
      level_room.ClearVisitMark()

  # Gets the coordinates of the start screen for a level.
  #
  # Params:
  #   level_num: The (1-indexed) level number to get info for.
  # Returns:
  #   The number of the start room, e.g. 0x73 for level 1
  def GetLevelStartRoomNumber(self, level_num: LevelNum) -> RoomNum:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    address = (
        self.LEVEL_1_START_ROOM_ADDRESS + self.STAIRCASE_START_ROOM_LEVEL_OFFSET * (level_num - 1))
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
    staircase_list_location = (self.LEVEL_1_STAIRCASE_DATA_ADDRESS +
                               self.STAIRCASE_START_ROOM_LEVEL_OFFSET * (level_num - 1))
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
