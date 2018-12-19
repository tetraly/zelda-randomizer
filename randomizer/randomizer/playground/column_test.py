from typing import List
from enum import IntEnum
from .screen import Screen

class Direction(IntEnum):
  NORTH = -0x10
  SOUTH = 0x10
  STAIRCASE = 0x00
  WEST = -0x1
  EAST = 0x1

# Goal:
  # Keep generating totally random overworlds
  # Alg to start on start screen, then do recursive search to see what caves you can get to
class ColumnTest(object):
  COLUMN_GROUP_STARTING_ADDRESSES: List[int] = [
      0x00, 0x35, 0x66, 0xa8, 0xec, 0x11e, 0x15a, 0x195, 0x1d0, 0x20e,
      0x24f, 0x294, 0x2d1, 0x307, 0x349, 0x37d]

  def __init__(self) -> None:
    self.screen_raw_data = list(
        open("randomizer/randomizer/data/overworld-screen-data.bin", 'rb').read(0x7C0))
    self.column_raw_data = list(
        open("randomizer/randomizer/data/overworld-column-data.bin", 'rb').read(0x3C4))

    self.overworld_raw_data = list(
        open("randomizer/randomizer/data/overworld-data.bin", 'rb').read(0x300))
    self.overworld_screens: List[Screen] = []

    # Screen code -> List of 16 integer column codes for the screen
    self.screen_column_codes: Dict[int, List[int]] = {}
    # Column code -> List of 11 integer tile codes
    self.column_tile_codes: Dict(int, List[int]) = {}
    # Screen_code and edge of screen -> int representing passability mask
    self.screen_edge_masks: Dict((int, Direction), int) = {}

  def _ReadDataForOverworldGrid(self) -> None:
    for screen_num in Range.VALID_ROOM_NUMBERS:
      screen_data: List[int] = []
      for byte_num in [0, 1, 2, 3, 5]:
        screen_data.append(
            self.overworld_raw_data[byte_num * self.LEVEL_TABLE_SIZE + screen_num])
      self.overworld_screens.append(Screen(screen_data))

  def ShuffleOverworld(self) -> None:
    random.shuffle(self.overworld_screens)


  def PrintOutOverworldInfo(self) -> None:
    self._RecursivelyTraverseOverworldScreen(0x77, Direction.NORTH)

  def _RecursivelyTraverseOverworldScreen(
      self, screen_num: int, direction: Direction) -> None:
    if screen_num > 0 or screen_num >= 0x80:
      return
    screen = self.overworld_screens[screen_num]
    if screen.IsMarkedAsVisited():
      return
    screen.MarkAsVisited()

    if screen.HasEntrance():
      screen.PrintSomeStuffAboutEntrance()

    for direction in [Direction.WEST, Direction.NORTH, Direction.EAST, Direction.SOUTH]:
      src_screen_code = screen.GetCode()
      dst_screen = self.overworld_screens[screen_num + direction]
      dst_screen_code = dst_screen.GetCode()
      if CanMove(src_screen_code, dst_screen_code, direction):
        self._RecursivelyTraverseOverworldScreen(screen_num + direction)


  def DoScreenEdgesMatch(self, src_screen_code: int, dst_screen_code: int,
                        direction: Direction) -> bool:
    src_edge_mask = self.screen_edge_masks[(src_screen_code, direction)]
    dst_edge_mask = self.screen_edge_masks[(dst_screen_code, -1 * direction)]
    return ((src_edge_mask == 0 and dst_edge_mask == 0) or
            (src_edge_mask | dst_edge_mask > 0))

  def CanMove(self, src_screen_code: int, dst_screen_code: int,
                        direction: Direction) -> bool:
    src_edge_mask = self.screen_edge_masks[(src_screen_code, direction)]
    dst_edge_mask = self.screen_edge_masks[(dst_screen_code, -1 * direction)]
    return (src_edge_mask | dst_edge_mask > 0)


  # Given a list of either 11 or 16 tile codes, returns their integer mask
  def GetIntegerMaskForTileCodes(self, tile_codes: List[int]) -> int:
    num_tile_codes = len(tile_codes)
    assert num_tile_codes in [11, 16]
    mask: int = 0
    #print("GetIntegerMaskForTileCodes")
    for tile_code_num in range(0, num_tile_codes):
      #print("Doing stuff for tile_code_num: %d" % tile_code_num)
      if self.IsPassable(tile_codes[tile_code_num]):
        #print("  Mask was %d" % mask)
        mask += 2 ** tile_code_num
        #print("  Now it's %d" % mask)
        #print("")
    assert mask < 2 ** 16
    return mask

  def IsStartOfColumn(self, data: int) -> bool:
    assert data & 0x80 == 0x00 or data & 0x80 == 0x80
    return data & 0x80 == 0x80

  def IsPassable(self, tile_code: int) -> bool:
    if self.GetAsciiCharacterForTileCode(tile_code) == ' ':
      return True
    return False

  def GetAsciiCharacterForTileCode(self, tile_code: int) -> chr:
    if tile_code in [0x05, 0x06, 0x07, 0x08, 0x09, 0x15, 0x16, 0x17, 0x18, 0x2e, 0x2f]: # Water codes
      return '~'
    elif int(tile_code/16) == 0 or tile_code == 0x37:
      return ' '
    else:
      return 'X'
    print ("What are you doing here?  You shouldn't be here!")



  # Now, we have all of our tile data.  Time to parse the screen definitions
  def PrintScreenData(self) -> None:
    for screen_code in range(0, 0x7D):
      screen_column_definition = (
          self.screen_raw_data[0x10 * screen_code : 0x10 * (screen_code + 1)])
      self.screen_column_codes[screen_code] = screen_column_definition

    for screen_code in range (0, 0x7A):
      print ("")
      print ("Screen code %d / %x" % (screen_code, screen_code))
      for y in range(0, 0xB):
      #  edge_passability[(screen_code, Direction.LEFT)]
        for x in range(0, 0x10):
          column_num = self.screen_column_codes[screen_code][x]
          #print("%02x" % column_num)
          tile_code = self.column_tile_codes[column_num][y]
          #print("%s" % "  " if int(tile_code/16) == 0 else "XX", end ="")
          #print("%02x" % tile_code, end="")
          print("%s" % self.GetAsciiCharacterForTileCode(tile_code), end ="")
        print("")
        # Screen 38, 45, 66, 81: corner of river should be transparent
        # Screens 40-42: Make polka dot desert thing transparent


  def GetTileCode(self, screen_code: int, x_coord: int, y_coord: int) -> int:
    column_num = self.screen_column_codes[screen_code][x_coord]
    return self.column_tile_codes[column_num][y_coord]

  #def IsPassable(self, start_screen_code: int, dest_screen_code: int,
#                 is_vertical: bool, is_north_or_east: bool):
#    if not is_vertical:
#      for tile_num in range(0, 12):
#        tile_code = self.GetTileCode(0)
#        if GetAsciiCharacterForTileCode()


def main() -> None:
  column_test = ColumnTest()
  column_test._ReadDataForOverworldGrid()
  column_test.ReadColumnTileCodes()
  column_test.ReadScreenStuff()
  column_test.GenerateScreenEdgeMasks()

if __name__ == '__main__':
  main()
