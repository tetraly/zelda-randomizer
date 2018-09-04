from absl import app
from absl import flags
from z1randomizer import Z1Randomizer


flags.DEFINE_integer(name='seed', default=0, help='The seed number to initialize RNG with.')
flags.DEFINE_string(
    name='input_filename', default='', help='The filename of the vanilla ROM to randomize.')
flags.register_validator(
    'input_filename', lambda value: value != '', message='Input filename must be specified.')

FLAGS = flags.FLAGS


def main(unused_argv) -> None:
  z1randomizer = Z1Randomizer()
  z1randomizer.SetFlags(FLAGS.input_filename, FLAGS.output_filename, FLAGS.seed)
  z1randomizer.Run()


if __name__ == '__main__':
  app.run(main)
