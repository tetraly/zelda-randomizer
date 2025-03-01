import io
import os
import random

from typing import List
from .data_table import DataTable
from .item_randomizer import ItemRandomizer
from .patch import Patch
from rom_reader import RomReader
from .text_data_table import TextDataTable
from .validator import Validator
from .flags import Flags

class Z1Randomizer():
#  def __init__(self) -> None:
#    self.rom: Rom
#    self.seed: int = 0
#    self.flags: Flags
#    self.settings: Settings

#  def ConfigureSettings(self, seed: int, settings: Settings) -> None:
#    self.seed = seed
#    self.settings = settings

  def __init__(self, rom_bytes: io.BytesIO, seed: int, flags: Flags) -> None:
    self.rom_reader = RomReader(rom_bytes)
    self.seed = seed
    self.flags = flags

  def GetPatch(self) -> Patch:
    random.seed(self.seed)
    data_table = DataTable(self.rom_reader)
    item_randomizer = ItemRandomizer(data_table, self.flags)
    validator = Validator(data_table, self.flags)

    # Main loop: Try a seed, if it isn't valid, try another one until it is valid.
    is_valid_seed = False

    num_iterations = 0
    while not is_valid_seed:
      seed = random.randint(0, 9999999999)
      num_iterations += 1
      while True:
        data_table.ResetToVanilla()
        item_randomizer.ResetState()
        item_randomizer.ReadItemsAndLocationsFromTable()
        item_randomizer.ShuffleItems()
        if item_randomizer.HasValidItemConfiguration():
          break
      
      item_randomizer.WriteItemsAndLocationsToTable()
      is_valid_seed = validator.IsSeedValid()
    patch = data_table.GetPatch()
    print("Number of iterations: %d" % num_iterations)

    if self.flags.progressive_items: # New progressive item code 
      patch.AddData(0x6D06, [0x18, 0x79, 0x57, 0x06, 0xEA])

      # Fix for Ring/tunic colors from zora/randomizer.py
      patch.AddData(0x6BFB, [0x20, 0xE4, 0xFF])
      patch.AddData(0x1FFF4, [0x8E, 0x02, 0x06, 0x8E, 0x72, 0x06, 0xEE, 0x4F, 0x03, 0x60])

    # Old progressive item code
    """if self.flags.progressive_items: 
      patch.AddData(0x6B49, [0x11, 0x12, 0x13])  # Swords
      patch.AddData(0x6B4E, [0x11, 0x12])  # Candles
      patch.AddData(0x6B50, [0x11, 0x12])  # Arrows
      patch.AddData(0x6B5A, [0x11, 0x12])  # Rings """


    if self.flags.speed_up_dungeon_transitions:
      # For fast scrolling. Puts NOPs instead of branching based on dungeon vs. Level 0 (OW)
      for addr in [0x141F3, 0x1426B, 0x1446B, 0x14478, 0x144AD]:
        patch.AddData(addr, [0xEA, 0xEA])


    if self.flags.max_hp_enemies:
       for addr in range(0x1FB5E, 0x1FB5E + 36):
         patch.AddData(addr, 0xFF)

    # For Mags patch
    patch.AddData(0x1785F, [0x0E])

    # Include everything above in the hash code.
    hash_code = patch.GetHashCode()
    patch.AddData(0xAFD0, hash_code)
    patch.AddData(0xA4CD, [0x4C, 0x90, 0xAF])
    patch.AddData(0xAFA0, [
        0xA2, 0x0A, 0xA9, 0xFF, 0x95, 0xAC, 0xCA, 0xD0, 0xFB, 0xA2, 0x04, 0xA0, 0x60, 0xBD, 0xBF,
        0xAF, 0x9D, 0x44, 0x04, 0x98, 0x69, 0x1B, 0xA8, 0x95, 0x70, 0xA9, 0x20, 0x95, 0x84, 0xA9,
        0x00, 0x95, 0xAC, 0xCA, 0xD0, 0xE9, 0x20, 0x9D, 0x97, 0xA9, 0x14, 0x85, 0x14, 0xE6, 0x13,
        0x60, 0xFF, 0xFF, 0x1E, 0x0A, 0x06, 0x01
    ])
    patch.AddData(
        0x1A129,
        [0x0C, 0x18, 0x0D, 0x0E, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24, 0x24])

    if self.flags.select_swap:
      patch.AddData(0x1EC4C, [0x4C, 0xC0, 0xFF])
      patch.AddData(0x1FFD0, [
          0xA9, 0x05, 0x20, 0xAC, 0xFF, 0xAD, 0x56, 0x06, 0xC9, 0x0F, 0xD0, 0x02, 0xA9, 0x07, 0xA8,
          0xA9, 0x01, 0x20, 0xC8, 0xB7, 0x4C, 0x58, 0xEC
      ])

    if self.flags.randomize_level_text or self.flags.speed_up_text:
      random_level_text = random.choice(
          ['palace', 'house-', 'block-', 'random', 'cage_-', 'home_-', 'castle'])
      text_data_table = TextDataTable(
          "very_fast" if self.flags.speed_up_text else "normal", random_level_text
          if self.flags.randomize_level_text else "level-")
      patch += text_data_table.GetPatch()
    return patch
