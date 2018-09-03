from typing import List
from constants import Range, LevelNum, RoomNum
from level_room import LevelRoom
from rom import Rom


class LevelDataTable(object):
  LEVEL_1_TO_6_DATA_START_ADDRESS = 0x18700
  LEVEL_7_TO_9_DATA_START_ADDRESS = 0x18A00
  LEVEL_TABLE_SIZE = 0x80
  LEVEL_ONE_START_ROOM_ADDRESS = 0x1942B
  LEVEL_1_STAIRWAY_DATA_ADDRESS = 0x19430
  LEVEL_3_RAFT_ROOM_NUMBER = RoomNum(0x0F)
  STAIRWAY_START_ROOM_LEVEL_OFFSET = 0xFC
  STAIRWAY_ROOM_NUMBER_SENTINEL_VALUE = 0xFF

  def __init__(self, rom: Rom) -> None:
    self.rom = rom
    self.level_1_to_6_level_rooms: List[LevelRoom] = []
    self.level_7_to_9_level_rooms: List[LevelRoom] = []

  def ReadLevelDataFromRom(self):
    # TODO: Refactor this to avoid duplicating code for the L1-6 and L7-9 tables.
    for room_num in Range.VALID_ROOM_NUMBERS:
      level_1_to_6_raw_data: List[RoomNum] = []
      level_7_to_9_raw_data: List[RoomNum] = []

      for table_num in Range.VALID_TABLE_NUMBERS:
        level_1_to_6_raw_data.append(
            self.rom.ReadByte(self.LEVEL_1_TO_6_DATA_START_ADDRESS +
                              table_num * self.LEVEL_TABLE_SIZE + room_num))
        level_7_to_9_raw_data.append(
            self.rom.ReadByte(self.LEVEL_7_TO_9_DATA_START_ADDRESS +
                              table_num * self.LEVEL_TABLE_SIZE + room_num))
      self.level_1_to_6_level_rooms.append(LevelRoom(level_1_to_6_raw_data))
      self.level_7_to_9_level_rooms.append(LevelRoom(level_7_to_9_raw_data))

  def WriteLevelDataToRom(self):
    for room_num in Range.VALID_ROOM_NUMBERS:
      level_1_6_room_data = self.level_1_to_6_level_rooms[room_num].GetRomData()
      level_7_9_room_data = self.level_7_to_9_level_rooms[room_num].GetRomData()
      assert len(level_1_6_room_data) == 6
      assert len(level_7_9_room_data) == 6

      for table_num in Range.VALID_TABLE_NUMBERS:
        self.rom.WriteByte(
            address=self.LEVEL_1_TO_6_DATA_START_ADDRESS + table_num * self.LEVEL_TABLE_SIZE +
            room_num,
            data=level_1_6_room_data[table_num])
        self.rom.WriteByte(
            address=self.LEVEL_7_TO_9_DATA_START_ADDRESS + table_num * self.LEVEL_TABLE_SIZE +
            room_num,
            data=level_7_9_room_data[table_num])

  def GetLevelRoom(self, level_num: LevelNum, room_num: RoomNum) -> LevelRoom:
    assert room_num in Range.VALID_ROOM_NUMBERS
    assert level_num in Range.VALID_LEVEL_NUMBERS
    if level_num in [7, 8, 9]:
      return self.level_7_to_9_level_rooms[room_num]
    return self.level_1_to_6_level_rooms[room_num]

  def ClearAllVisitMarkers(self):
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
        self.LEVEL_ONE_START_ROOM_ADDRESS + self.STAIRWAY_START_ROOM_LEVEL_OFFSET * (level_num - 1))
    return RoomNum(self.rom.ReadByte(address))

  # Gets a list of stairway rooms for a level.
  #
  # Note that this will include not just passage stairways between two
  # dungeon rooms but also item rooms with only one passage two and
  # from a dungeon room.
  #
  # Args:
  #  level_num: The 1-indexed level to get information for (int)
  # Returns:
  #  Zero or more bytes containing the stairway room numbers
  def GetLevelStairwayRoomNumberList(self, level_num: LevelNum) -> List[RoomNum]:
    assert level_num in Range.VALID_LEVEL_NUMBERS
    stairway_list_location = (self.LEVEL_1_STAIRWAY_DATA_ADDRESS +
                              self.STAIRWAY_START_ROOM_LEVEL_OFFSET * (level_num - 1))
    raw_bytes = self.rom.ReadBytes(stairway_list_location, 10)
    stairway_list: List[RoomNum] = []
    for byte in raw_bytes:
      if byte != self.STAIRWAY_ROOM_NUMBER_SENTINEL_VALUE:
        stairway_list.append(RoomNum(byte))

    # This is a hack needed in order to make vanilla L3 work.  For some reason,
    # the vanilla ROM's data for level 3 doesn't include a stairway room even
    # though there obviously is one in vanilla level 3.
    #
    # See http://www.romhacking.net/forum/index.php?topic=18750.msg271821#msg271821
    # for more information about why this is the case and this hack is necessary.
    if level_num == 3 and not stairway_list:
      stairway_list.append(self.LEVEL_3_RAFT_ROOM_NUMBER)

    return stairway_list
