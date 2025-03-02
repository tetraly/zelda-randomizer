from enum import Enum

class FlagsEnum(Enum):
    PROGRESSIVE_ITEMS = (
        'progressive_items',
        'Progressive swords, rings, arrows, and candles',
        'If enabled, there will be three wood swords, two wood arrows, two blue rings, and two blue candles in the item pool. Collecting multiples of each will upgrade the item.'
    )
    SHUFFLE_WHITE_SWORD = (
        'shuffle_white_sword',
        'Shuffle White Sword',
        'Adds the White Sword to the item shuffle pool'
    )
    SHUFFLE_MAGICAL_SWORD = (
        'shuffle_magical_sword',
        'Shuffle Magical Sword',
        'Adds the Magical Sword to the item shuffle pool. Important Note: If the Magical Sword is shuffled into a room that normally has a standing floor item, it will become a drop item. You will need to defeat all enemies in the room for the Magical Sword to appear.'
    )
    SHUFFLE_LETTER = (
        'shuffle_letter',
        'Shuffle Letter',
        'Adds the letter for the potion shop to the item shuffle.'
    )
    SHUFFLE_ARMOS_ITEM = (
        'shuffle_armos_item',
        'Shuffle the Armos Item',
        'Adds the Power Bracelet to the item shuffle pool.'
    )
    SHUFFLE_COAST_ITEM = (
        'shuffle_coast_item',
        'Shuffle the Coast Item',
        'Adds the coast heart container to the item shuffle pool.'
    )
    SHUFFLE_SHOP_ITEMS = (
        'shuffle_shop_items',
        'Shuffle Shop Items',
        'Adds the blue candle, blue ring, wood arrows, and both baits to the item shuffle pool.'
    )
    SHUFFLE_MINOR_DUNGEON_ITEMS = (
        'shuffle_minor_dungeon_items',
        'Shuffle Minor Dungeon Items',
        'Adds minor items (five rupees, bombs, keys, maps, and compasses) to the item shuffle pool.'
    )
    AVOID_REQUIRED_HARD_COMBAT = (
        'avoid_required_hard_combat',
        'Avoid Requiring "Hard" Combat',
        'The logic will not require killing any Blue Darknuts, Blue Wizzrobes, Gleeoks, or Patras to progress without making at least one sword upgrade and at least one ring available in logic.'
    )
    SELECT_SWAP = (
        'select_swap',
        'Enable Item Swap with Select',
        'Pressing select will cycle through your B button inventory instead of pausing the game.'
    )
    RANDOMIZE_LEVEL_TEXT = (
        'randomize_level_text',
        'Randomize Level Text',
        'Chooses a random value (either literally or figuratively) for the "level-#" text displayed in dungeons.'
    )
    SPEED_UP_TEXT = (
        'speed_up_text',
        'Speed Up Text',
        'Increases the scrolling speed of text displayed in caves and dungeons.'
    )
    SPEED_UP_DUNGEON_TRANSITIONS = (
        'speed_up_dungeon_transitions',
        'Speed Up Dungeon Transitions',
        'Speeds up dungeon room transitions to be as fast as overworld screen transitions'
    )
    PACIFIST_MODE = (
        'pacifist_mode',
        'Pacifist Mode',
        'Auto-opens shutter doors and makes blocks pushable. Also gives more (infinite?) HP to enemies or something?'
    )
    
    
    def __init__(self, value, display_name, help_text):
        self._value_ = value
        self.display_name = display_name
        self.help_text = help_text

    @classmethod
    def get_flag_list(cls):
        return [(flag.value.lower(), flag.display_name, flag.help_text) for flag in cls]


class Flags:
    def __init__(self):
        self.flags = {flag.value: flag for flag in FlagsEnum}

    def __getattr__(self, flag_value):
        return self.flags[flag_value]

    def get(self, flag_value):
        return self.flags[flag_value]

    def set(self, flag_value, state: bool):
        if flag_value in self.flags:
            self.flags[flag_value] = state
        else:
            raise KeyError(f"Flag '{flag_value}' not found.")

        
