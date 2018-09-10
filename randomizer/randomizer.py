import os
import random

from randomizer.constants import TextSpeed
from randomizer.item_randomizer import ItemRandomizer
from randomizer.item_shuffler import ItemShuffler
from randomizer.level_data_table import LevelDataTable
from randomizer.logic_validator import LogicValidator
from randomizer.rom import Rom
from randomizer.settings.settings import Settings
from randomizer.text.text_data_table import TextDataTable

class Z1Randomizer():
  def __init__(self):
    self.settings = None

  def SetFlags(self, settings: Settings) -> None:
    self.settings = settings

  def Run(self):
    input_rom = Rom(self.settings.input_filename, add_nes_header_offset=True)
    input_rom.OpenFile()
    (input_path, input_full_filename) = os.path.split(self.settings.input_filename)
    (input_filename, input_extension) = os.path.splitext(input_full_filename)

    output_filename = os.path.join(
        self.settings.output_location or input_path,
        "%s-randomized-%d%s" % (input_filename, self.settings.seed, input_extension or ".nes"))
    output_rom = Rom(output_filename, src=self.settings.input_filename, add_nes_header_offset=True)
    output_rom.OpenFile(write_mode=True)

    seed = self.settings.seed - 1
    level_data_table = LevelDataTable(output_rom)
    level_data_table.ReadLevelDataFromRom()
    item_shuffler = ItemShuffler()
    item_randomizer = ItemRandomizer(level_data_table, item_shuffler)
    logic_validator = LogicValidator(level_data_table)
    text_data_table = TextDataTable(output_rom)

    # Main loop: Try a seed, if it isn't valid, try another one until it is valid.
    is_valid_seed = False
    while not is_valid_seed:
      seed += 1
      random.seed(seed)
      item_shuffler.ResetState()
      level_data_table.ReadLevelDataFromRom()
      item_randomizer.ReadItemsAndLocationsFromTable()
      item_randomizer.ShuffleItems()
      item_randomizer.WriteItemsAndLocationsToTable()
      is_valid_seed = logic_validator.Validate()
    level_data_table.WriteLevelDataToRom()

    if self.settings.flags.text_speed == 'random':
      self.settings.flags.set_random_text_speed()
    else: # Coerce the string to an int.
      self.settings.flags.text_speed = TextSpeed[self.settings.flags.text_speed.upper()]

    if self.settings.flags.level_text == '*':
      self.settings.flags.set_random_level_text()
    else:
      self.settings.flags.correct_level_text()

    text_data_table.WriteTextSpeedToRom(self.settings.flags.text_speed)
    text_data_table.WriteLevelNameToRom(self.settings.flags.level_text)
