import random
from typing import IO, List
from shutil import copyfile
from absl import logging


class Rom():
  """A class representing a video game ROM file stored in a binary file."""

  NES_HEADER_OFFSET = 0x10

  def __init__(self, rom_filename: str, src: str = None,
               add_nes_header_offset: bool = False) -> None:
    self.rom_filename = rom_filename
    self.rom_file: IO[bytes]
    self.write_mode = False
    self.add_nes_header_offset = add_nes_header_offset
    if src:
      copyfile(src, rom_filename)
    self.address = -1

  # Opens a ROM file for reading
  def OpenFile(self, write_mode: bool = False):
    self.write_mode = write_mode
    print("Opening %s %s ...\n\n" % (self.rom_filename, "for writing" if write_mode else ""))
    self.rom_file = open(self.rom_filename, "r+b" if write_mode else "rb")

  def ShuffleRanges(self, start_locations: List[int], num_bytes: int) -> None:
    """Randomly shuffles up the specified blocks/ranges of data. """
    shuffled_ranges = []
    for location in start_locations:
      shuffled_ranges.append(self.ReadBytes(location, num_bytes))
    random.shuffle(shuffled_ranges)
    for shuffled_range, location in zip(shuffled_ranges, start_locations):
      self.WriteBytes(location, shuffled_range)

  def ReadBytes(self, address: int, num_bytes: int = 1) -> List[int]:
    """Reads one or more bytes (represented as Python ints) from the ROM file."""
    assert self.rom_file, "Need to run OpenFile() first."
    assert num_bytes > 0, "Can't read zero or a negative number of bytes."
    self.rom_file.seek(address + self.NES_HEADER_OFFSET if self.add_nes_header_offset else address)
    int_data: List[int] = []
    for read_byte in self.rom_file.read(num_bytes):
      int_data.append(read_byte)
    return int_data

  def ReadByte(self, address: int) -> int:
    return self.ReadBytes(address, 1)[0]

  def WriteBytes(self, address: int, data: List[int]) -> None:
    """Writes one or more bytes (represented as Python ints) to the ROM file."""
    assert self.rom_file, "Need to run OpenFile(write_mode=True) first."
    assert self.write_mode, "Needs to be in write mode!"
    assert data is not None, "Need at least one byte to write."

    offset = 0
    for byte in data:
      self.rom_file.seek((address + self.NES_HEADER_OFFSET
                          if self.add_nes_header_offset else address) + offset)
      self.rom_file.write(bytes([byte]))
      offset = offset + 1

  def WriteByte(self, address: int, data: int) -> None:
    return self.WriteBytes(address, [data])

  # Helper methods for reading from a particular area of the ROM
  def Peek(self) -> int:
    return_value = self.ReadBytes(self.address, 1)[0]
    return return_value

  def ReadMultipleBytes(self, num_bytes: int) -> List[int]:
    return_value = self.ReadBytes(self.address, num_bytes)
    self.address += num_bytes
    return return_value

  def Read(self) -> int:
    return_value = self.ReadMultipleBytes(1)[0]
    return return_value

  def WriteMultipleBytes(self, bytes_to_write: List[int]) -> None:
    self.WriteBytes(self.address, bytes_to_write)
    self.address += len(bytes_to_write)

  def Write(self, byte_to_write: int) -> None:
    self.WriteMultipleBytes([byte_to_write])

  def SetAddress(self, address: int) -> None:
    logging.debug("Setting address to 0x%x" % address)
    self.address = address

  def GetAddress(self) -> int:
    return self.address
