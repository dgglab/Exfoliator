import typing
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.Qt import QAbstractTableModel, QModelIndex

class MotionModel(QAbstractTableModel):
    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            return [
                ['1'] * 5,
                ['2'] * 5,
                ['3'] * 5
            ]
    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 5

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return 3

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Vertical:
            return ['a', 'b', 'c']
        elif orientation == Qt.Horizontal:
            return ['1','2','3']

class MotionControllerDashboard(QWidget):
    """
    Dashboard for motion controller. Key input/outputs
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_layout = QHBoxLayout(self)

        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        placeholder_button_names = ['bob', 'joe', 'sam']
        for p in placeholder_button_names:
            button_layout.addWidget(QPushButton(p))

        self.table_item_view = QTableView()
        self.table_item_view.setModel(MotionModel())
        self.table_item_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_item_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        main_layout.addWidget(self.table_item_view)
        main_layout.addWidget(button_container)


