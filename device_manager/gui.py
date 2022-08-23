import dataclasses
import typing

from PyQt5.QtWidgets import QTableView, QWidget, QListWidget, QListWidgetItem
from PyQt5.QtCore import QAbstractTableModel, QModelIndex
from PyQt5.QtCore import Qt

from .device_manager import global_device_manager

device_type_icon_mapping = {}

class DeviceModel(QAbstractTableModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices = list(global_device_manager.devices)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            return self.devices[index.row()][index.column()]
        if role == Qt.DecorationRole:
            device = self.devices[index.row()]
            icon = device_type_icon_mapping.get(type(device), None)
            return icon

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(global_device_manager.devices)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(list(global_device_manager.devices.values())[0])


    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        # No header here. We are basically using table class just for spacing.
        return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        ...


class DeviceDashboard(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_view = QTableView()
        self.table_view.setShowGrid(False)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setVisible(False)

        self.device_model = DeviceModel()
        self.table_view.setModel(DeviceModel)

        # self.list_widget = QListWidget()
        # for d in list(global_device_manager.devices.values()):
        #     QListWidgetItem()