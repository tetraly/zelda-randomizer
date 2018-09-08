import sys

from absl import app
from absl import flags
from PyQt5.QtWidgets import QApplication

from randomizer.randomizer import Z1Randomizer

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

FLAGS = flags.FLAGS

class Z1RandomizerApp(Z1rUI):
  def __init__(self, parent=None) -> None:
    super(Z1RandomizerApp, self).__init__(parent)

    self.input_filename_flag = ""
    self.output_location_flag = ""
    self.seed_flag = 0

  # Override
  def _RunRandomizer(self) -> None:
    z1r = Z1Randomizer()
    z1r.SetFlags(self.input_filename_flag, self.output_location_flag, self.seed_flag, "normal")
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
  z1randomizer.SetFlags(FLAGS.input_filename, FLAGS.output_location, FLAGS.seed, FLAGS.text_speed)
  z1randomizer.Run()


if __name__ == '__main__':
  app.run(main)
