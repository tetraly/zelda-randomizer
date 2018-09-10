from randomizer.settings.flags import Flags

class Settings():
  def __init__(self) -> None:
    self.input_filename = ''
    self.output_location = '' # Directory
    self.seed = 0
    self.flags = Flags()
