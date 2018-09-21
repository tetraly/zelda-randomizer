import os
import random

from typing import List
from randomizer.item_randomizer import ItemRandomizer
from randomizer.data_table import DataTable
from randomizer.rom import Rom
from randomizer.text.text_data_table import TextDataTable
from randomizer.validator import Validator
from randomizer.patch import Patch


class Z1Randomizer():
  def __init__(self):
    self.input_filename: str = None
    self.output_location: str = None
    self.seed: int = 0
    self.text_speed: str = None
    self.level_text: str = None

  def SetFlags(self, input_filename: str, output_location: str, seed: int, text_speed: str,
               level_text: str) -> None:
    self.input_filename = input_filename
    self.output_location = output_location
    self.seed = seed
    self.text_speed = text_speed
    self.level_text = level_text

  def Run(self) -> None:
    (input_path, input_full_filename) = os.path.split(self.input_filename)
    (input_filename, input_extension) = os.path.splitext(input_full_filename)
    output_filename = os.path.join(
        self.output_location or input_path,
        "%s-randomized-%d%s" % (input_filename, self.seed, input_extension or ".nes"))
    output_rom = Rom(output_filename, src=self.input_filename, add_nes_header_offset=True)
    output_rom.OpenFile(write_mode=True)

    patch = self.GetPatch()

    for address in patch.GetAddresses():
      data: List[int]
      data = patch.GetData(address)
      output_rom.WriteBytes(address, data)

    text_data_table = TextDataTable(self.text_speed, self.level_text)
    patch += text_data_table.GetPatch()

    # Select Swap
    output_rom.WriteBytes(0x1EC3C, [0x4C, 0xC0, 0xFF])
    output_rom.WriteBytes(0x1FFC0, [
        0xA9, 0x05, 0x20, 0xAC, 0xFF, 0xAD, 0x56, 0x06, 0xC9, 0x0F, 0xD0, 0x02, 0xA9, 0x07, 0xA8,
        0xA9, 0x01, 0x20, 0xC8, 0xB7, 0x4C, 0x58, 0xEC
    ])

  def GetPatch(self) -> Patch:
    seed = self.seed - 1
    data_table = DataTable()
    item_randomizer = ItemRandomizer(data_table)
    validator = Validator(data_table)

    # Main loop: Try a seed, if it isn't valid, try another one until it is valid.
    is_valid_seed = False
    while not is_valid_seed:
      seed += 1
      random.seed(seed)
      data_table.ResetToVanilla()
      item_randomizer.ResetState()
      item_randomizer.ReadItemsAndLocationsFromTable()
      item_randomizer.ShuffleItems()
      item_randomizer.WriteItemsAndLocationsToTable()
      is_valid_seed = validator.IsSeedValid()
    return data_table.GetPatch()
