from typing import List
from rom import Rom
from level_room import LevelRoom
from zelda_constants import RoomNum, LevelNum


class LevelDataTable(object):

  NES_FILE_OFFSET = 0x10
  LEVEL_1_TO_6_DATA_START_ADDRESS = 0x18700
  LEVEL_7_TO_9_DATA_START_ADDRESS = 0x18A00
  NUM_ROOMS_IN_TABLE = 0x80
  LEVEL_TABLE_SIZE = 0x80
  NUM_TABLES = 6

  LEVEL_ONE_START_ROOM_LOCATION = 0x1942B
  LEVEL_1_STAIRWAY_DATA_ADDRESS = 0x19430
  STAIRWAY_START_ROOM_LEVEL_OFFSET = 0xFC

  def __init__(self, rom: Rom) -> None:
    self.rom = rom
    self.level_1_to_6_level_rooms = []  # type: List[LevelRoom]
    self.level_7_to_9_level_rooms = []  # type: List[LevelRoom]

  def ReadLevelDataFromRom(self):
    for room_num in range(0, self.NUM_ROOMS_IN_TABLE):
      level_1_to_6_raw_data = []  # type: List[RoomNum]
      level_7_to_9_raw_data = []  # type: List[RoomNum]

      for table_num in range(0, self.NUM_TABLES):
        level_1_to_6_raw_data.append(
            self.rom.ReadByte(self.LEVEL_1_TO_6_DATA_START_ADDRESS +
                              table_num * self.LEVEL_TABLE_SIZE + room_num))
        level_7_to_9_raw_data.append(
            self.rom.ReadByte(self.LEVEL_7_TO_9_DATA_START_ADDRESS +
                              table_num * self.LEVEL_TABLE_SIZE + room_num))
      self.level_1_to_6_level_rooms.append(LevelRoom(level_1_to_6_raw_data))
      self.level_7_to_9_level_rooms.append(LevelRoom(level_7_to_9_raw_data))

  def WriteLevelDataToRom(self):
    for room_num in range(0, self.NUM_ROOMS_IN_TABLE):
      for table_num in range(0, self.NUM_TABLES):
        self.rom.WriteBytes(
            self.LEVEL_1_TO_6_DATA_START_ADDRESS + table_num * self.LEVEL_TABLE_SIZE + room_num,
            self.level_1_to_6_level_rooms[room_num].GetRawData(table_num))
        self.rom.WriteBytes(
            self.LEVEL_7_TO_9_DATA_START_ADDRESS + table_num * self.LEVEL_TABLE_SIZE + room_num,
            self.level_7_to_9_level_rooms[room_num].GetRawData(table_num))

  def GetLevelRoom(self, level_num: LevelNum, room_num: RoomNum) -> LevelRoom:
    print("GetLevelRoom called for level %d room_num %d" % (level_num, room_num))
    assert (room_num >= 0x00 and room_num <= 0x7F)
    assert (level_num >= 1 and level_num <= 9)
    if level_num in [7, 8, 9]:
      return self.level_7_to_9_level_rooms[room_num]
    return self.level_1_to_6_level_rooms[room_num]

  # Gets the coordinates of the start screen for a level.
  #
  # Params:
  #   level_num: The (1-indexed) level number to get info for.
  # Returns:
  #   The number of the start room, e.g. 0x73 for level 1
  def GetLevelStartRoomNumber(self, level_num: LevelNum) -> RoomNum:
    assert (level_num >= 1 and level_num <= 9)
    address = (self.LEVEL_ONE_START_ROOM_LOCATION +
               self.STAIRWAY_START_ROOM_LEVEL_OFFSET * (level_num - 1))
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
    assert (level_num >= 1 and level_num <= 9)
    stairway_list_location = (self.LEVEL_1_STAIRWAY_DATA_ADDRESS +
                              self.STAIRWAY_START_ROOM_LEVEL_OFFSET * (level_num - 1))
    raw_bytes = self.rom.ReadBytes(stairway_list_location, 10)
    stairway_list = []  # type: List[RoomNum]
    for byte in raw_bytes:
      if not byte == 0xFF:
        stairway_list.append(RoomNum(byte))

    # This is a hack needed in order to make vanilla L3 work.  For some reason,
    # the vanilla ROM's data for level 3 doesn't include a stairway room even
    # though there obviously is one in vanilla level 3.
    #
    # See http://www.romhacking.net/forum/index.php?topic=18750.msg271821#msg271821
    # for more information about why this is the case and this hack is necessary.
    if level_num == 3 and not stairway_list:
      stairway_list.append(RoomNum(0x0F))

    return stairway_list
