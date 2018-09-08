import os
import random
import sys
from absl import app
from absl import flags
from PyQt5.QtWidgets import QApplication
from constants import TextSpeed
from item_randomizer import ItemRandomizer
from item_shuffler import ItemShuffler
from level_data_table import LevelDataTable
from logic_validator import LogicValidator
from rom import Rom
from text_data_table import TextDataTable
from z1r_ui import Z1rUI


flags.DEFINE_integer(name='seed', default=random.randint(1, 999999999), help='The seed number to initialize RNG with.')
flags.DEFINE_string(
    name='input_filename', default='', help='The filename of the vanilla ROM to randomize.')
flags.DEFINE_string(
    name='output_location', default='', help='The location to put the randomized ROM.')
flags.DEFINE_enum(
    'text_speed',
    'normal',
    ['very_fast', 'fast', 'normal', 'slow', 'very_slow', 'random'],
    'How fast the text speed will go. Fast speed is, well, fast, but slower speed allows for '
    'resetting door repair charges.',
)

FLAGS = flags.FLAGS


class Z1Randomizer(object):
  def __init__(self):
    self.input_filename: str = None
    self.output_location: str = None
    self.seed: int = 0
    self.text_speed: str = None

  def SetFlags(self, input_filename: str, output_location: str, seed: int, text_speed: str) -> None:
    self.input_filename = input_filename
    self.output_location = output_location
    self.seed = seed
    self.text_speed = text_speed

  def Run(self):
    input_rom = Rom(self.input_filename, add_nes_header_offset=True)
    input_rom.OpenFile()
    (input_path, input_full_filename) = os.path.split(self.input_filename)
    (input_filename, input_extension) = os.path.splitext(input_full_filename)

    output_filename = os.path.join(
        self.output_location or input_path,
        "%s-randomized-%d%s" % (input_filename, self.seed, input_extension or ".nes"))
    output_rom = Rom(output_filename, src=self.input_filename, add_nes_header_offset=True)
    output_rom.OpenFile(write_mode=True)

    seed = self.seed - 1
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

    converted_text_speed = TextSpeed.NORMAL
    if (self.text_speed == 'random'):
      converted_text_speed = random.choice(list(TextSpeed))
    else:
      converted_text_speed = TextSpeed[self.text_speed.upper()]

    text_data_table.WriteTextSpeedToRom(converted_text_speed)


class Z1RandomizerApp(Z1rUI):
  def __init__(self, parent=None) -> None:
    super(Z1RandomizerApp, self).__init__(parent)

    self.input_filename_flag = ""
    self.output_location_flag = ""
    self.seed_flag = 0

  # Override
  def _RunRandomizer(self) -> None:
    z1r = Z1Randomizer()
    z1r.SetFlags(self.input_filename_flag, self.output_location_flag, self.seed_flag, "normal")
    z1r.Run()


def main(unused_argv) -> None:
  if FLAGS.input_filename == '' and FLAGS.seed == 0:
    print("Command-line flags not specified, entering GUI mode.")
    gui = QApplication(sys.argv)
    window = Z1RandomizerApp()
    window.show()
    gui.exec_()
    sys.exit(0)

  z1randomizer = Z1Randomizer()
  z1randomizer.SetFlags(FLAGS.input_filename, FLAGS.output_location, FLAGS.seed, FLAGS.text_speed)
  z1randomizer.Run()


if __name__ == '__main__':
  app.run(main)
