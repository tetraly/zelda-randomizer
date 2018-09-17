from typing import List, Set

from randomizer.constants import Item, LevelNum, Range
from randomizer.cave import Cave


class Inventory(object):
  def __init__(self) -> None:
    self.still_making_progress_bit = False
    self.Reset()

  def Reset(self) -> None:
    self.items: Set[Item] = set()
    self.still_making_progress_bit = False
    self.num_heart_containers = 3
    self.num_tringles = 0
    self.num_keys = 0

  def SetStillMakingProgressBit(self) -> None:
    print("Still making progress!")
    self.still_making_progress_bit = True

  def ClearMakingProgressBit(self) -> None:
    self.still_making_progress_bit = False

  def StillMakingProgress(self) -> bool:
    return self.still_making_progress_bit

  def AddMultipleItems(self, items: List[Item]) -> None:
    for item in items:
      self.AddItem(item)

  def AddItem(self, item: Item) -> None:
    if item in [
        Item.OVERWORLD_NO_ITEM, Item.MAP, Item.COMPASS, Item.MAGICAL_SHIELD, Item.BOMBS,
        Item.FIVE_RUPEES, Item.RUPEE, Item.SINGLE_HEART
    ]:
      return
    assert item in range(0, 0x21)  # Includes red potion 0x20
    if item == Item.HEART_CONTAINER:
      self.num_heart_containers += 1
    elif item == Item.TRINGLE:
      self.num_tringles += 1
    elif item == Item.KEY:
      self.num_keys += 1
    elif item in self.items:
      return
    else:
      print("----------------------------   Adding %s to inventory" % item)
      self.SetStillMakingProgressBit()
      self.items.add(item)

  def GetHeartCount(self) -> int:
    return self.num_heart_containers

  def GetTriforceCount(self) -> int:
    return self.num_tringles

  def HasKey(self) -> bool:
    return self.Has(Item.ANY_KEY) or self.num_keys > 0

  def UseKey(self) -> None:
    assert self.HasKey()
    if self.Has(Item.ANY_KEY):
      return
    self.num_keys -= 1

  def HasSword(self) -> bool:
    return (Item.WOOD_SWORD in self.items or Item.WHITE_SWORD in self.items
            or Item.MAGICAL_SWORD in self.items)

  def HasBowAndArrows(self) -> bool:
    return (Item.BOW in self.items
            and (Item.WOOD_ARROWS in self.items or Item.SILVER_ARROWS in self.items))

  def HasCandle(self) -> bool:
    return Item.BLUE_CANDLE in self.items or Item.RED_CANDLE in self.items

  def HasRing(self) -> bool:
    return Item.BLUE_RING in self.items or Item.RED_RING in self.items

  def HasBoomerang(self) -> bool:
    return Item.LORD_BANANA in self.items or Item.INFERIOR_MODEL in self.items

  def HasBowSilverArrowsAndSword(self) -> bool:
    return self.HasSword() and Item.SILVER_ARROWS in self.items

  def HasSwordOrWand(self) -> bool:
    return self.HasSword() or Item.WAND in self.items

  def HasReusableWeaponOrBoomerang(self) -> bool:
    return self.HasReusableWeapon() or self.HasBoomerang()

  def HasReusableWeapon(self) -> bool:
    return self.HasSwordOrWand() or Item.RED_CANDLE in self.items

  def HasRecorderAndReusableWeapon(self) -> bool:
    return Item.RECORDER in self.items and self.HasReusableWeapon()

  def Has(self, item: Item) -> bool:
    return item in self.items

  def CanEnterLevel(self, level_num: LevelNum) -> bool:
    if level_num == 4:
      return self.Has(Item.RAFT)
    elif level_num == 7:
      return self.Has(Item.RECORDER)
    elif level_num == 8:
      return self.HasCandle()
    elif level_num == 9:
      return self.num_tringles >= 8
    return True
