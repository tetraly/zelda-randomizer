import os
import random
import traceback
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from ui_dialog import Ui_Dialog


class Z1rUI(QMainWindow, Ui_Dialog):
  def __init__(self, parent=None) -> None:
    super(Z1rUI, self).__init__(parent)
    self.setupUi(self)
    self.rom_file = None
    self.chosen_location = None

    self.updating_checkboxes = False
    self._GenerateRandomSeedNumber()

    self.new_seed_button.clicked.connect(self._GenerateRandomSeedNumber)
    self.choose_file_button.clicked.connect(self._OpenFile)
    self.choose_output_button.clicked.connect(self._ChooseOutputLocation)
    self.randomize_button.clicked.connect(self._RandomizeButtonClicked)

  # Action Handlers
  def _OpenFile(self) -> None:
    self.input_filename.clear()
    self.rom_file = QFileDialog.getOpenFileName(self, "Open file", os.path.dirname(__file__),
                                                "NES ROMs (*.nes)")[0]
    if self.rom_file:
      self.input_filename.setText(self.rom_file)

  def _ChooseOutputLocation(self) -> None:
    self.output_location.clear()
    self.chosen_location = QFileDialog.getExistingDirectory(self, "Choose directory",
                                                            os.path.dirname(__file__),
                                                            QFileDialog.ShowDirsOnly)
    if self.chosen_location:
      self.output_location.setText(self.chosen_location)

  def _GenerateRandomSeedNumber(self) -> None:
    self.seed_number.setText(str(random.randint(1, 999999999)))

  def _RandomizeButtonClicked(self) -> None:
    # Getting flags from the UI and doing basic validation of them.
    if len(self.seed_number.text()) > 9:
      QMessageBox.about(self, "Error", "Please enter a seed number with 9 digits or less")
      return
    try:
      seed_number = int(self.seed_number.text())
    except Exception as e:  # TODO: Narrow the casting exception down.
      QMessageBox.about(self, "Error", "Error: Please enter an integer seed number. "
                        "Debug info: {}".format(e))
      return
    self.input_filename_flag = self.input_filename.text()
    self.seed_flag = seed_number
    self.output_location_flag = self.output_location.text()

    try:
      self._RunRandomizer()
    except Exception as e:
      QMessageBox.about(self, "Error", ("Some mysterious error has occurred. :( "
                                        "Please contact the developers with information about "
                                        "what happened%s") % traceback.format_exc())
      return
    QMessageBox.about(self, "Success", "Your ROM has been randomized. GLHF!")
