import argparse
import io
import sys

from randomizer.randomizer.randomizer import Z1Randomizer
from randomizer.randomizer.flags import Flags

def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument('--input_filename', type=str, required=True, help='Rom to randomize')
  parser.add_argument('--output_location', type=str, required=True, help='Where to put the thing')
  parser.add_argument('--seed', type=int, required=True, help='RNG seed')
  args = parser.parse_args()
  
  if not args.input_filename.endswith('.nes'):
    print("Filename must end with '.nes'")
    exit()
  output_filename = args.input_filename[:-4] + '_zora.nes'
  
  with open(args.input_filename, 'rb') as f:
      input_rom_data = io.BytesIO(f.read())

  z1randomizer = Z1Randomizer(input_rom_data, args.seed, Flags())
  
  patch = z1randomizer.GetPatch()
  output_rom_data = io.BytesIO(input_rom_data.getvalue())
  for address in patch.GetAddresses():
    output_rom_data.seek(address)
    output_rom_data.write(bytes(patch.GetData(address)))

  with open(output_filename, 'wb') as f:
      f.write(output_rom_data.getvalue())

if __name__ == '__main__':
  main()
