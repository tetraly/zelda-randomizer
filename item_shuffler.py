
[randomizer logic] -> item location manger
[zelda_rom] -> LevelRooms (get/set) levelroom.set(room_num, level_num, item_code)
[rom]


class ItemAndLocationManager(object):
  NO_ITEM_NUMBER = 0x03  # Actually code for mags, but that's how they did it!
  ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS = [0x16, 0x17, 0x1B] # Compass, map, tringle

  def __init__(self) -> None:
    self.item_locations = {} # type: Dict[int, List[int]]
    self.item_num_list = [] # type: List[int]
    self.per_level_item_lists = {} # Dict int -> list[item]

  def AddLocationAndItem(self, level_num: int, room_num: int, item_num) -> None:
    assert level_num in range(1, NUM_LEVELS + 1)
    assert item_num in range(0, 0x20)
    if item_num == self.NO_ITEM_NUMBER:
      return
    if item_num in self.ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS:
      return
      
    self.item_locations[level_num] = room_num
    self.item_num_list.append(item_num)
    
  def ShuffleItemsGlobally(self) -> None:
    random.shuffle(self.item_num_list)
  
  def ShuffleItemsWithinLevels(self) -> None:
    for level_num in range(1, NUM_LEVELS + 1):
      self.per_level_item_lists[level_num].extend(ITEMS_TO_SHUFFLE_ONLY_WITHIN_LEVELS)
      for unused_location in self.item_locations[level_num]:
        self.per_level_item_lists[level_num].append(self.item_num_list.pop())
      random.shuffle(self.item_locations[level_num])

  def GetAllLocationAndItemData(self) -> Iterable[Tuple[int, int, int]]:
    for level_num in range(1, NUM_LEVELS + 1):
       yield (level_num,
              self.item_locations[level_num].pop(), # room_num 
              self.per_level_item_lists[level_num].pop()) # item_num
      





shuffle all items around all levels.  
Constraint: each level must have 1 triforce, map, and compass

shuffle across all levels all items except those codes
Then, for each level:
  Re-shuffle among only the level all the items
  

Reading in data, keep per-level lists of locations, items

List[List[int]]
level, list[locations]
***Dict[level -> list[locations]]***

List[int]
items that should be shuffled over all levels


