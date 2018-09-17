from absl import logging

from randomizer.constants import CaveNum, LevelNum, PositionNum, Range, RoomNum


class Location(object):
  def __init__(self, level_num=None, cave_num=None, room_num=None, position_num=None):
    if level_num is not None:
      assert level_num in Range.VALID_LEVEL_NUMBERS
      assert room_num in Range.VALID_ROOM_NUMBERS
      assert cave_num is None
      assert position_num is None
      self.level_id = level_num
      self.sub_id = room_num

    elif cave_num is not None:
      assert cave_num in Range.VALID_CAVE_NUMBERS
      assert position_num in Range.VALID_CAVE_POSITION_NUMBERS
      assert level_num is None
      assert room_num is None
      self.level_id = cave_num + 15
      self.sub_id = position_num

    else:
      logging.fatal("Location: level or cave number must be specified")

  @classmethod
  def LevelRoom(cls, level_num, room_num):
    return cls(level_num=level_num, room_num=room_num)

  @classmethod
  def CavePosition(cls, cave_num, position_num):
    return cls(cave_num=cave_num, position_num=position_num)

  def IsLevelRoom(self) -> bool:
    return self.level_id in range(1, 10)

  def IsCavePosition(self) -> bool:
    return self.level_id in range(0x10, 0x25)

  def GetLevelNum(self) -> LevelNum:
    assert self.IsLevelRoom()
    return self.level_id

  def GetRoomNum(self) -> RoomNum:
    assert self.IsLevelRoom()
    return self.sub_id

  def GetCaveNum(self) -> CaveNum:
    assert self.IsCavePosition()
    return self.level_id - 15

  def GetPositionNum(self) -> PositionNum:
    assert self.IsCavePosition()
    return self.sub_id


#class RoomLocation(Location):
# def __init__(self, cave_num, position_num):
#  assert cave_num in range (1, 22) # 1-indexed
# assert position_num in range (1, 4) # 1-indexed
#self.level_id = cave_num + 15
#self.sub_id = position_num
