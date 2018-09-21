#from django import forms

#from .models import MODES

# List of option checkbox fields for dynamic page generation.
FLAGS = (
    ('shuffle_white_sword', 'Shuffle White Sword', 'Adds the White Sword to the item shuffle pool'),
    ('shuffle_magical_sword', 'Shuffle Magical Sword', 'Adds the Magical Sword to the item shuffle pool'),
    ('shuffle_letter', 'Shuffle Letter', 'Adds the letter for the potion shop to the item shuffle.'),
    ('shuffle_armos_item',  'Shuffle the Armos Item', 'Adds the Power Bracelet to the item shuffle pool.'),
    ('shuffle_coast_item', 'Shuffle the Coast Item', 'Adds the coast heart container to the item shuffle pool.'),
    ('shuffle_shop_items', 'Shuffle Shop Items', 'Adds the blue candle, blue ring, wood arrows, and both baits to the item shuffle pool.'),
    ('select_swap', 'Enable Item Swap with Select', 'Pressing select will cycle through your B button inventory instead of pause the game.'),
    ('randomize_level_text', 'Randomize Level Text', 'Changes the "LEVEL-#" text displayed in dungeons.'),
    ('speed_up_text', 'Speed Up Text', 'Increases the scrolling speed of text displayed in caves and dungeons.')
)


#class GenerateForm(forms.Form):
#    region = forms.Field(required=False)
#    seed = forms.Field(required=False)
#    mode = forms.ChoiceField(required=True, choices=MODES)
#    debug_mode = forms.BooleanField(required=False, initial=False)

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)

#        for flag in FLAGS:
#            self.fields[flag[0]] = forms.BooleanField(required=False, initial=False)

