"""The Main Z1R App."""
import sys
from PyQt5.QtWidgets import QApplication

from z1randomizer import Z1Randomizer
from z1r_ui import Z1rUI


class Z1rApp(Z1rUI):
  def __init__(self, parent=None) -> None:
    super(Z1rApp, self).__init__(parent)

    self.input_filename_flag = ""
    self.output_location_flag = ""
    self.seed_flag = 0

    # self._UpdateFlagString()

  # Override
  def _RunRandomizer(self) -> None:
    z1r = Z1Randomizer()
    z1r.SetFlags(self.input_filename_flag, self.output_location_flag, self.seed_flag, "normal")
    z1r.Run()


def main() -> None:
  app = QApplication(sys.argv)
  window = Z1rApp()
  window.show()
  app.exec_()


if __name__ == "__main__":
  main()
