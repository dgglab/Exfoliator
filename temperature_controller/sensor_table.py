# For sensor table, no custom delegate is required since we do not need to edit anything
# Similarly, we don't need a custom view to override selection behavior.
# All that is required is a custom model.

# We will re-use the same mechanism from the Controller table, which is to define a row class, whose fields define the
# column values.
import traceback

from PyQt5.QtWidgets import QHeaderView

from temperature_controller.table_utils import Field, DDict
from PyQt5 import QtWidgets
from PyQt5.Qt import QAbstractTableModel, QModelIndex
import typing
from temperature_controller.ctc100 import Channel
from PyQt5.QtCore import Qt, QMutexLocker
from temperature_controller.log_widget import logger
from temperature_controller.poller import ChannelPoller, PollResponse


class SensorTableRow:
    fields = [
        Field("name", "Name"),
        Field("value", "Value", 0.0)
    ]

    def __init__(self, channel: Channel):
        # TODO: Hack - fix this
        self.channel = channel
        if channel:
            self.name = channel.name
            with QMutexLocker(channel.mutex):
                self.value = float(channel.send("?"))
            self.fields = [
                self.name, self.value
            ]
        # self.field_key_index = DDict({k: v for k, v in [(x.key, x) for x in self.fields]})
        # self.field_key_index.name.value = self.name
        # self.field_key_index.value.value = self.channel.send('value?')

    def __str__(self):
        return "Row" + self.name
    def __repr__(self):
        return self.__str__()



class TemperatureSensorTableModel(QAbstractTableModel):
    def __init__(self, rows, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not rows:
            rows = [SensorTableRow(None)]
        self.rows = rows

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        row = self.rows[index.row()]
        field = row.fields[index.column()]
        if role == Qt.DisplayRole:
            return field

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.rows)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(SensorTableRow.fields)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        return ""

class TemperatureSensorTable(QtWidgets.QTableView):
    def __init__(self, sensors: typing.List[Channel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        rows = [SensorTableRow(s) for s in sensors]
        self.model = TemperatureSensorTableModel(rows)
        self.setModel(self.model)
        # self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        logger.info("Sensor Table - Starting poller")
        # TODO: Hack. Remove this.
        if rows:
            self.poller = ChannelPoller(sensors)
            self.poller.updateReady.connect(self.update_ready)
            self.poller.start()

    def update_ready(self, new_values: typing.Dict[str, PollResponse]):
        for row in self.model.rows:
            try:
                v = new_values[row.name]
                row.fields[1] = float(v.value)
            except Exception:
                traceback.print_exc()
        self.model.layoutChanged.emit()




if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    from ctc100_manager import global_ctc_100_manager
    sensors = global_ctc_100_manager.sensors
    obj = TemperatureSensorTable(sensors)
    obj.show()
    app.exec()

