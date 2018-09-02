import random
from absl import app
from absl import flags
from item_shuffler import ItemShuffler
from item_randomizer import ItemRandomizer
from level_data_table import LevelDataTable
from rom import Rom


# TODO: Add actual logic checks here
class LogicChecker(object):
  def DoesSeedPassAllLogicChecks(self):
    return True


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
  level_table = LevelDataTable(rom)
  level_table.ReadLevelDataFromRom()
  shuffler = ItemShuffler()
  logic_checker = LogicChecker()
  item_randomizer = ItemRandomizer(level_table, shuffler)

  # Loop-a-dee-doo until our Check() returns True
  seed_passes_logic_checks = False
  while not seed_passes_logic_checks:
    seed += 1
    random.seed(seed)
    level_table.ReadLevelDataFromRom()
    item_randomizer.ReadItemsAndLocationsFromTable()
    item_randomizer.ShuffleItems()
    item_randomizer.WriteItemsAndLocationsToTable()
    seed_passes_logic_checks = logic_checker.DoesSeedPassAllLogicChecks()
  level_table.WriteLevelDataToRom()


if __name__ == '__main__':
  app.run(main)
