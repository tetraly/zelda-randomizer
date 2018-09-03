import random
from absl import app
from absl import flags
from item_shuffler import ItemShuffler
from item_randomizer import ItemRandomizer
from level_data_table import LevelDataTable
from rom import Rom
from logic_validator import LogicValidator

flags.DEFINE_integer(name='seed', default=0, help='The seed number to initialize RNG with.')
flags.DEFINE_string(
    name='input_filename', default='', help='The filename of the vanilla ROM to randomize.')
flags.register_validator(
    'input_filename', lambda value: value != '', message='Input filename must be specified.')

FLAGS = flags.FLAGS


def main(unused_argv) -> None:
  rom = Rom(FLAGS.input_filename, add_nes_header_offset=True)
  rom.OpenFile(write_mode=True)
  seed = FLAGS.seed - 1
  level_data_table = LevelDataTable(rom)
  level_data_table.ReadLevelDataFromRom()
  shuffler = ItemShuffler()
  item_randomizer = ItemRandomizer(level_data_table, shuffler)
  logic_validator = LogicValidator(level_data_table)

  # Loop-a-dee-doo until our Check() returns True
  is_valid_seed = False
  while not is_valid_seed:
    seed += 1
    random.seed(seed)
    level_data_table.ReadLevelDataFromRom()
    item_randomizer.ReadItemsAndLocationsFromTable()
    item_randomizer.ShuffleItems()
    item_randomizer.WriteItemsAndLocationsToTable()
    is_valid_seed = logic_validator.Validate()
  level_data_table.WriteLevelDataToRom()


if __name__ == '__main__':
  app.run(main)
