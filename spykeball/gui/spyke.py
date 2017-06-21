"""Spykeball Graphical User Interface."""

import sys

from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QLineEdit,
    QInputDialog,
    QApplication,
    QMainWindow
    )

from PyQt5.QtGui import QIcon


class SpykeballMainWindow(QMainWindow):
    """Main Window Object for the Spykeball GUI."""

    def __init__(self):
        """Initialize Main Object."""
        QMainWindow.__init__(self)

        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        self.btn = QPushButton('Dialog', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.draw_username_dialog)

        self.le = QLineEdit(self)
        self.le.move(130, 22)

        self.statusBar().showMessage('Ready')

        self.setGeometry(300, 300, 1000, 350)
        self.setWindowTitle('spykeball')
        self.show()

    def draw_username_dialog(self):
        """Draw the Username dialog."""
        text, ok = QInputDialog.getText(
            self, 'Input Dialog', 'username:')

        if ok:
            self.le.setText(str(text))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setApplicationName('spykeball')
    app.setWindowIcon(QIcon('../../resources/images/spikeballicon.png'))

    smw = SpykeballMainWindow()

    sys.exit(app.exec_())
