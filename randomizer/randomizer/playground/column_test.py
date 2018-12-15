
class ColumnTest(object):
  def __init__(self) -> None:
    self.screen_raw_data = list(
        open("randomizer/randomizer/data/overworld-screen-data.bin", 'rb').read(0x7C0))
    self.column_raw_data = list(
        open("randomizer/randomizer/data/overworld-column-data.bin", 'rb').read(0x3C4))
    self.screen_column_definitions: Dict[int, List[int]] = {}
    self.column_tile_codes: Dict(int, List[int]) = {}

  def GetBooleanColumnData(self, column_num: int) -> List[bool]:
    boolean_data: List[int] = []
    for tile_code in self.column_tile_codes[column_num]:
      if GetAsciiCharacterForTileCode(tile_code) == ' ':
        boolean_data.append(True)
      else:
        boolean_data.append(True)
    assert len(to_be_returned) == 11
    return boolean_data

  def IsStartOfColumn(self, data: int) -> bool:
    assert data & 0x80 == 0x00 or data & 0x80 == 0x80
    return data & 0x80 == 0x80

  def GetAsciiCharacterForTileCode(self, tile_code: int) -> chr:
    if tile_code in [0x05, 0x06, 0x07, 0x08, 0x09, 0x15, 0x16, 0x17, 0x18, 0x2e, 0x2f]: # Water codes
      return '~'
    elif int(tile_code/16) == 0 or tile_code == 0x37:
      return ' '
    else:
      return 'X'
    print ("What are you doing here?  You shouldn't be here!")

  def DoStuff(self) -> None:
    print("")
    print("Hello World")
    print("")

    column_group_starting_addresses: List[int] = [
        0x00, 0x35, 0x66, 0xa8, 0xec, 0x11e, 0x15a, 0x195, 0x1d0, 0x20e,
        0x24f, 0x294, 0x2d1, 0x307, 0x349, 0x37d]

    for column_group_number in range(0, 0x10):
      # Figure out what addresses column definitions start on
      # Start addresses are denoted by having a 1 for the MSB of the data
      searching_address = column_group_starting_addresses[column_group_number]
      column_start_addresses: List[int] = []
      for column_number in range (0, 0x0A):
        while True:
          found_start = self.IsStartOfColumn(self.column_raw_data[searching_address])
          if found_start:
            column_start_addresses.append(searching_address)
          searching_address += 1
          if found_start:
            break

      for column_number in range(0, 0x0A):
        column_start_address = column_start_addresses[column_number]
        tile_codes: List[int] = []
        num_tile_codes_read: int = 0
        addr = column_start_address
        assert self.column_raw_data[addr] & 0x80 == 0x80
        while num_tile_codes_read < 11:
          tile_code = self.column_raw_data[addr] & 0x3F
          if self.column_raw_data[addr] & 0x40 == 0x40:
            tile_codes.extend([tile_code, tile_code])
            num_tile_codes_read += 2
          else:
            tile_codes.append(tile_code)
            num_tile_codes_read += 1
          addr += 1
        assert num_tile_codes_read == 11

        column_number = 0x10 * column_group_number + column_number
        self.column_tile_codes[column_number] = tile_codes

    # Now, we have all of our tile data.  Time to parse the screen definitions

    for screen_code in range(0, 0x7D):
      screen_column_definition = (
          self.screen_raw_data[0x10 * screen_code : 0x10 * (screen_code + 1)])
      screen_column_definitions[screen_code] = screen_column_definition

    for screen_code in range (0, 0x7A):
      print ("")
      print ("Screen code %d / %x" % (screen_code, screen_code))
      for y in range(0, 0xB):
        edge_passability[(screen_code, Direction.LEFT)]
        for x in range(0, 0x10):
          column_num = self.screen_column_definitions[screen_code][x]
          #print("%02x" % column_num)
          tile_code = self.column_tile_codes[column_num][y]
          #print("%s" % "  " if int(tile_code/16) == 0 else "XX", end ="")
          #print("%02x" % tile_code, end="")
          print("%s" % self.GetAsciiCharacterForTileCode(tile_code), end ="")
        print("")
        # Screen 38, 45, 66, 81: corner of river should be transparent
        # Screens 40-42: Make polka dot desert thing transparent


  def GetTileCode(self, screen_code: int, x_coord: int, y_coord: int) -> int:
    column_num = self.screen_column_definitions[screen_code][x_coord]
    return self.column_tile_codes[column_num][y_coord]

  def IsPassable(self, start_screen_code: int, dest_screen_code: int,
                 is_vertical: bool, is_north_or_east: bool):
    if not is_vertical:
      for tile_num in range(0, 12):
        tile_code = self.GetTileCode(0)
        if GetAsciiCharacterForTileCode()


def main() -> None:
  column_test = ColumnTest()
  column_test.DoStuff()

if __name__ == '__main__':
  main()
