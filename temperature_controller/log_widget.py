import logging

from PyQt5.QtWidgets import QTextEdit
from PyQt5 import QtGui


class LogEditor(logging.Handler):
    editor: QTextEdit

    def connect_editor(self, editor: QTextEdit):
        self.editor = editor
        font = QtGui.QFont()
        font.setPointSize(8)
        self.editor.setFont(font)

        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
        self.setFormatter(formatter)

    def emit(self, record):
        self.editor.append(self.format(record))


logger = logging.getLogger("temperature")
log_editor = LogEditor()
