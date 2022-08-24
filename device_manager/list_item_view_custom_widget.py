from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QApplication, QComboBox
from PyQt5.QtCore import Qt
from .switch_button import Switch

from typing import NamedTuple

class ConnectionStatus(NamedTuple):
    label: str
    button_action: str

class ConnectionStatuses:
    CONNECTED = ConnectionStatus("Connected", "Disconnect")
    NOT_CONNECTED = ConnectionStatus('Not Connected', "Connect")
    ERROR = ConnectionStatus("Error", "")

class ConnectionStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.connection_status = ConnectionStatuses.NOT_CONNECTED
        self.status_label = QLabel(f"Status: {self.connection_status.label}")
        self.connection_button = QPushButton(self.connection_status.button_action)
        layout.addWidget(self.status_label)
        layout.addWidget(self.connection_button)
        self.setLayout(layout)

        self.connection_button.clicked.connect(self.onConnectionButtonClick)

    def onConnectionButtonClick(self):
        if self.connection_status == ConnectionStatuses.CONNECTED:
            self.connection_status = ConnectionStatuses.NOT_CONNECTED
        elif self.connection_status == ConnectionStatuses.NOT_CONNECTED:
            self.connection_status = ConnectionStatuses.CONNECTED
        self.status_label.setText(self.connection_status.label)
        self.connection_button.setText(self.connection_status.button_action)


class MyCustomWidget(QWidget):
    def __init__(self, name, parent=None):
        super(MyCustomWidget, self).__init__(parent)

        self.row = QHBoxLayout()

        self.name = QLabel(name)
        self.name.setAlignment(Qt.AlignCenter)
        self.com_selector = QComboBox(self)
        for i in range(5):
            self.com_selector.addItem(f"COM{i}")

        self.row.addWidget(Switch())
        self.row.addWidget(self.name)
        self.row.addWidget(self.com_selector)
        self.row.addWidget(ConnectionStatusWidget())
        self.setLayout(self.row)


class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        # Create the list
        layout = QHBoxLayout()
        self.mylist = QListWidget()

        # Add to list a new item (item is simply an entry in your list)
        self.item = QListWidgetItem(self.mylist)
        self.mylist.addItem(self.item)

        # Instanciate a custom widget
        self.row = MyCustomWidget('bob')
        self.item.setSizeHint(self.row.minimumSizeHint())


        self.mylist.setItemWidget(self.item, self.row)
        layout.addWidget(self.mylist)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication([])
    db = Dashboard()
    db.show()
    app.exec()
