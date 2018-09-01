# zeldarandomizer-private

An open-source randomizer for Zelda 1.  Is such a thing even possible?  Yes, it is!


This Z1R code is designed to only be compatible with Python 3 and make liberal use of type annotations in order to get as close to a static typing experience as Python can provide. 

Class overview:  

Rom:  A very bare bones helper for reading from and writing raw daa to a ROM file.  It's pretty much identical to that of smb2r and is agnostic of what game this is (i.e. there's no Zelda-specific logic). 

LevelDataTable:  A layer on top of the ROM that accesses data from the places where it knows it's kept in a Zelda ROM.  It contains a List consiting of:
  -- LevelRoom: This is a "smart" object representing a single room in a level and knows how exactly to interpret and modify the raw data for that room.

ItemRandomizer: An additional layer above the LevelDataTable, it does the work of traversing through levels recursively and reading the level data get pairs of room numbers and the item numbers.  It stores these in a:
  -- ItemShuffler: Where the real randomization is done!  This is where the lists of items and locations (rooms/levels) are stored and shuffled around.
  
Eventually, there will also be a logic checker that will operate on the LevelDataTable, getting room data and determining if there are any circular item dependencies that would prevent a seed from being beatable.

