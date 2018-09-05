Open Source Zelda 1 Randomizer

This is an open-source item randomizer for Zelda 1 written by tetraly. If you're looking for the Zelda Randomizer written by fcoughlin, please see https://sites.google.com/site/zeldarandomizer/

This code is was written and tested with Python 3.6.4. It probably will not be backwards compatible with Python 2.x. Currently, it requires the open-source Abseil library, as well as the PyQt5 for the GUI to run. Coming soon will be a self-contained .EXE file for Windows and .App file for MacOS. But if you're comfortable with command-line tools and want to try it out, clone this repository and run:

pip install pipenv
pipenv install
pipenv shell
python z1randomizer_cli.py \
 --input_filename=/path/to/zelda/rom.nes
--output_location=/path/to/put/randomized/rom/
--seed=12345

You can also run the GUI version:

python z1randomizer_app.py

A design/class overview for programmers:

Z1randomizer: Has the main() method for the randomizer. Sets up objects and has the while loop to generate a seed and attempt to validate it until a valid seed is produced.

Rom: A very bare bones helper for reading from and writing raw daa to a ROM file. It's pretty much identical to that of smb2r and is agnostic of what game this is (i.e. there's no Zelda-specific logic).

LevelDataTable: A layer on top of the ROM that accesses data from the places where it knows it's kept in a Zelda ROM. It contains a List consiting of:
-- LevelRoom: A "smart" object representing a single room in a level and knows how exactly to interpret and modify the raw data for that room.

ItemRandomizer: An additional layer above the LevelDataTable, it does the work of traversing through levels recursively and reading the level data get pairs of room numbers and the item numbers. It stores these in a:
-- ItemShuffler: Where the real randomization is done! This is where the lists of items and locations (rooms/levels) are stored and shuffled around.

Logic Validator: This class traverses through the LevelRooms in the LevelDataTable running various checks to ensure that the seed is beatable.

If you have questions or comments, please feel free to reach out to tetraly@ on Twitter or tetraly#1131 on Discord.
