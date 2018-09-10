import re
import sys

from absl import app
from absl import flags
from PyQt5.QtWidgets import QApplication

from randomizer.randomizer import Z1Randomizer
from randomizer.settings.settings import Settings

from z1r_ui import Z1rUI


flags.DEFINE_integer(name='seed', default=0, help='The seed number to initialize RNG with.')
flags.DEFINE_string(
    name='input_filename', default='', help='The filename of the vanilla ROM to randomize.')
flags.DEFINE_string(
    name='output_location', default='', help='The location to put the randomized ROM.')
flags.DEFINE_enum(
    'text_speed',
    'normal',
    ['very_fast', 'fast', 'normal', 'slow', 'very_slow', 'random'],
    'How fast the text speed will go. Fast speed is, well, fast, but slower speed allows for '
    'resetting door repair charges.',
)

flags.DEFINE_string(
    'level_text',
    'level-',
    'What are the dungeons called? This is strictly for fun.'
)

def is_level_text_valid(value: str) -> bool:
  if len(value) > 6:
    return False

  if value == '*':
    return True

  pattern = re.compile("([\\w~,!'&\\.\\\"\\?-]){1,6}")
  return pattern.match(value)

flags.register_validator(
    'level_text',
    is_level_text_valid,
    message='This text must fit a pattern no bigger than six characters.'
)

FLAGS = flags.FLAGS

def generate_base_settings(input_filename: str, output_location: str, seed: int) -> Settings:
  settings = Settings()
  settings.input_filename = input_filename
  settings.output_location = output_location
  settings.seed = seed
  return settings

class Z1RandomizerApp(Z1rUI):
  def __init__(self, parent=None) -> None:
    super(Z1RandomizerApp, self).__init__(parent)
    self.settings = Settings()

  # Override
  def _RunRandomizer(self) -> None:
    z1r = Z1Randomizer()
    z1r.SetFlags(self.settings)
    z1r.Run()

def main(unused_argv) -> None:
  if FLAGS.input_filename == '' and FLAGS.seed == 0:
    print("Command-line flags not specified, entering GUI mode.")
    gui = QApplication(sys.argv)
    window = Z1RandomizerApp()
    window.show()
    gui.exec_()
    sys.exit(0)

  z1randomizer = Z1Randomizer()
  settings = generate_base_settings(FLAGS.input_filename, FLAGS.output_location, FLAGS.seed)
  settings.flags.text_speed = FLAGS.text_speed
  settings.flags.level_text = FLAGS.level_text

  z1randomizer.SetFlags(settings)
  z1randomizer.Run()


if __name__ == '__main__':
  app.run(main)
