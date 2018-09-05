from absl import app
from absl import flags
from z1randomizer import Z1Randomizer

flags.DEFINE_integer(name='seed', default=0, help='The seed number to initialize RNG with.')
flags.DEFINE_string(
    name='input_filename', default='', help='The filename of the vanilla ROM to randomize.')
flags.DEFINE_string(
    name='output_location', default='', help='The location to put the randomized ROM.')
flags.register_validator(
    'input_filename', lambda value: value != '', message='Input filename must be specified.')
flags.DEFINE_enum(
    'text_speed',
    'normal',
    ['very_fast', 'fast', 'normal', 'slow', 'very_slow', 'random'],
    'How fast the text speed will go. Fast speed is, well, fast, but slower speed allows for resetting door repair charges.',
)

FLAGS = flags.FLAGS


def main(unused_argv) -> None:
  z1randomizer = Z1Randomizer()
  z1randomizer.SetFlags(FLAGS.input_filename, FLAGS.output_location, FLAGS.seed, FLAGS.text_speed)
  z1randomizer.Run()


if __name__ == '__main__':
  app.run(main)
