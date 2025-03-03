import argparse
import io
import logging
import sys

from randomizer.randomizer.randomizer import Z1Randomizer
from randomizer.randomizer.flags import Flags

def setup_logging(debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_filename', type=str, required=True, help='Rom to randomize')
  parser.add_argument('--output_location', type=str, required=True, help='Where to put the thing')
  parser.add_argument('--seed', type=int, required=True, help='RNG seed')
  parser.add_argument('--debug', action='store_true', help='Enable debug logging')
  args = parser.parse_args()
  
  setup_logging(args.debug)
  
  if not args.input_filename.endswith('.nes'):
    print("Filename must end with '.nes'")
    exit()
  output_filename = args.input_filename[:-4] + '_zora.nes'
  
  with open(args.input_filename, 'rb') as f:
      input_rom_data = io.BytesIO(f.read())

  flags = Flags()
  flags.set("shuffle_minor_dungeon_items", False)
  flags.set("avoid_required_hard_combat", False)
  flags.set("randomize_level_text", False)
  flags.set("select_swap", False)
  
  z1randomizer = Z1Randomizer(input_rom_data, args.seed, flags)
  
  patch = z1randomizer.GetPatch()
  output_rom_data = io.BytesIO(input_rom_data.getvalue())
  for address in patch.GetAddresses():
    output_rom_data.seek(address)
    output_rom_data.write(bytes(patch.GetData(address)))
  logging.debug("Output filename is %s" % output_filename)
  with open(output_filename, 'wb') as f:
      f.write(output_rom_data.getvalue())

if __name__ == '__main__':
  main()
