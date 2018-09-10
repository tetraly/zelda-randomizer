import random

from randomizer.constants import TextSpeed

class Flags():
  LEVEL_TEXT_OPTIONS = [
      'level-', 'house-', 'block-', 'random', 'cage_-',
      'home_-', 'castle'
  ]

  def __init__(self) -> None:
    self.text_speed = TextSpeed.NORMAL
    self.level_text = 'level-'

  def set_random_level_text(self) -> None:
    self.level_text = random.choice(self.LEVEL_TEXT_OPTIONS)

  def correct_level_text(self) -> None:
    self.level_text = self.level_text.ljust(6, '_')

  def set_random_text_speed(self) -> None:
    self.text_speed = random.choice(list(TextSpeed))
