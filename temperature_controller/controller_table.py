import enum
import random
import traceback
import typing

from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableView, QPushButton, QStyledItemDelegate, QDoubleSpinBox, \
    QVBoxLayout, QDialog, QHeaderView, QAbstractItemView, QApplication, QMainWindow
from PyQt5.QtCore import Qt, QMutexLocker
from PyQt5 import QtCore
from PyQt5.Qt import QAbstractTableModel, QModelIndex



from temperature_controller.ctc100 import Channel
from temperature_controller.ctc100_manager import global_ctc_100_manager
from temperature_controller.poller import ChannelPoller, PollResponse
from temperature_controller.table_utils import Field, DDict
from temperature_controller.switch_button import Switch
from temperature_controller.log_widget import logger

POLL_FREQUENCY_S = 1  # frequency (in seconds) at which to poll CTC channels for updates
STABLE_THRESHOLD_C = 0.01  # absolute value in celsius between target and current temp
STANDBY_TEMP_C = 30.0

class ControllerState(typing.NamedTuple):
    on: bool = False  # is pid enabled
    parity: int = 0  # Is this guy ramping
    standby: bool = False

    def __str__(self):
        if not self.on:
            return "Off"
        elif self.standby:
            return "On/Standby"
        elif self.parity == 0:
            return "On/Stable"
        elif self.parity == 1:
            return "On/Ramping Up"
        else:
            return "On/Ramping Down"


class CheatButton(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.switch = Switch()
        layout = QVBoxLayout()
        layout.addWidget(self.switch)
        self.setLayout(layout)

class ControllerTableRowControlButtons(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        # Reference to model required to trigger layoutChanged.emit() in the clicked() handlers
        # The clicked handlers are defined in the Item class.
        # The buttons can't be defined directly in the Item class because it is not a Widget
        # The model can't be passed to the item class because it is not a QObject.
        layout = QHBoxLayout(self)
        self.holdBtn = QPushButton('Hold')
        self.setBtn = QPushButton('Set')
        self.resetBtn = QPushButton("Reset")
        for i in [self.holdBtn, self.setBtn, self.resetBtn]:
            layout.addWidget(i)
        self.layout = layout

class GoHoldButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEnabled(False)
        self.setText("Go")

class ControllerTableRow:
    """
    A row in the dashboard table. Rows are comprised of fields.
    Fields are indexed in 2 ways:
        1) order index -- successive integer ordering of fields starting from 0
        2) key index -- index fields by key word
    """
    def __init__(self, name, parent: QWidget, channel: Channel):
        self.name = name
        self.parent = parent
        self.channel = channel
        # Note that parent needs to be a qwidget.
        self.switch_toggle = CheatButton(parent)
        self.switch_toggle.switch.clicked.connect(self.on_clicked)

        self.hold_go_btn = GoHoldButton(parent)
        self.hold_go_btn.clicked.connect(self.on_go_hold)

        self.fields = [
            Field("on", "PID ON", None, widget=self.switch_toggle),
            Field('name', 'Channel Name', self.name),
            Field('value', 'Current Temp (C)'),
            Field('setpoint', 'Target Temp (C)', readonly=False),
            Field('ramp_rate', 'Ramp\nRate (C/s)'),
            Field('working_setpoint', 'Working\nSetpoint (C)'),
            Field('current_output', 'Current\nOutput (V)'),
            Field('max_output', 'Max. Output (V)'),
            Field('go_hold', 'Controls', None, widget=self.hold_go_btn),
            Field("state", "Status", ControllerState())
        ]
        self.order_index = {k: v for k, v in enumerate(self.fields)}
        self.field_key_index = DDict({k: v for k, v in [(x.key, x) for x in self.fields]})

    def on_clicked(self, c):
        with QMutexLocker(self.channel.pid.mutex):
            if not c:
                logger.info(f"{self.name} - toggle off")
                self.channel.pid.send('Off')
            else:
                logger.info(f"{self.name} - toggle on")
                self.channel.pid.send('pid.mode=On')

    def on_go_hold(self):
        if self.hold_go_btn.text() == "Go":
            with QMutexLocker(self.channel.pid.mutex):
                msg = f'pid.setpoint={self.field_key_index.setpoint.value}'
                self.channel.pid.send(msg)
            self.hold_go_btn.setText("Hold")

        elif self.hold_go_btn.text() == "Hold":
            with QMutexLocker(self.channel.pid.mutex):
                msg = f'pid.setpoint={self.field_key_index.value.value}'
                self.channel.pid.send(msg)
                self.field_key_index.setpoint.value = self.field_key_index.value.value
            self.hold_go_btn.setText("Go")
            self.hold_go_btn.setEnabled(False)





class TemperatureControllerTableModel(QAbstractTableModel):

    def __init__(self, rows, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not rows:
            rows = [ControllerTableRow("-", None, None)]
        self.rows = rows

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        row = self.rows[index.row()]
        field = row.order_index[index.column()]
        state: ControllerState = row.field_key_index.state.value

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if field.widget:
                return None
            else:
                return field.value

        # Off
        if not state.on:
            if role == Qt.ForegroundRole:
                return QColor('darkGray')
            if role == Qt.BackgroundColorRole:
                return QColor('White')

        # 1. Stable: when channel is active and current temp is within 0.01 C of target for 30s
        elif abs(row.field_key_index.value.value - row.field_key_index.working_setpoint.value) <= STABLE_THRESHOLD_C:
            if role == Qt.BackgroundColorRole:
                return QColor('lightGreen')

        # 2. Stand-by: When channel is active and current temp, target temp and working setpoint are all below 30C
        elif all(row.field_key_index[x].value < STANDBY_TEMP_C for x in ['value', 'working_setpoint']):
            if role == Qt.BackgroundColorRole:
                if not field.widget:
                    if field.readonly:
                        return QColor('lightGray')
        # 4. Ramping
        else:
            if role == Qt.BackgroundColorRole:
                return QColor('lightBlue')


    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.rows[0].order_index)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.rows)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.rows[0].order_index[section].display_name
            # else:
            #     return self.rows[section].name

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.EditRole:
            row = self.rows[index.row()]
            field = row.order_index[index.column()]
            if field.value != value:
                field.value = value
                row.hold_go_btn.setEnabled(True)
            return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        row = self.rows[index.row()]
        field = row.order_index[index.column()]
        flags = QAbstractTableModel.flags(self, index) & ~Qt.ItemIsSelectable
        if not field.readonly:
            flags |= Qt.ItemIsEditable
        return flags


class TemperatureControllerTableDelegate(QStyledItemDelegate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0.0)
        editor.setMaximum(100.0)
        editor.setDecimals(3)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        value = index.model().data(index, Qt.EditRole)
        if value:
            editor.setValue(value)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def displayText(self, value: typing.Any, locale: QtCore.QLocale) -> str:
        if type(value) is float:
            return f"{value:0.3f}"
        elif value is None:
            return ''
        else:
            return str(value)


class TemperatureControllerTableView(QTableView):
    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self.edit(self.currentIndex())
        else:
            QTableView.keyPressEvent(self, e)


class ConfigureRowsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Configure Temperature Dashboard")
        self.show()


class TemperatureControllerTable(QWidget):
    def __init__(self, controllers: typing.List[Channel], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialized = False

        # Table items
        self.table_rows = [ControllerTableRow(c.name, self, c) for c in controllers]

        # For updating status
        logger.info("Controller Table - Starting Poller")
        self.poller = ChannelPoller(controllers)
        self.poller.updateReady.connect(self.update_ready)
        self.poller.start()


        self.model = TemperatureControllerTableModel(self.table_rows)
        self.table_item_view = TemperatureControllerTableView()
        self.table_item_view.setModel(self.model)
        self.delegate = TemperatureControllerTableDelegate()
        self.table_item_view.setItemDelegate(self.delegate)
        self.table_item_view.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.EditKeyPressed
        )
        self.table_item_view.setMouseTracking(True)
        self.table_item_view.horizontalHeader().setStyleSheet(
            "::section {background-color: black; font-weight:900; color:white; border: 1px solid #6c6c6c}")
        for i, item in enumerate(self.table_rows):
            for j, field in item.order_index.items():
                if field.widget:
                    index = self.model.index(i, j)
                    self.table_item_view.setIndexWidget(index, field.widget)
                else:
                    self.table_item_view.horizontalHeader().setSectionResizeMode(j, QHeaderView.Stretch)
            #
            # buttons = ControllerTableRowControlButtons(self.model)
            # index = self.model.index(i, len(item.order_index) - 1)
            # self.table_item_view.setIndexWidget(index, buttons)
        self.table_item_view.resizeColumnsToContents()
        self.table_item_view.resizeRowsToContents()
        # self.table_item_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QHBoxLayout()
        layout.addWidget(self.table_item_view)
        self.setLayout(layout)


    def update_ready(self, new_values: typing.Dict[str, PollResponse]):
        for row in self.table_rows:
            try:
                v = new_values[row.name]
                row.field_key_index.value.value = v.value
                row.field_key_index.ramp_rate.value = v.ramp_rate
                row.field_key_index.working_setpoint.value = v.working_setpoint
                row.field_key_index.current_output.value = v.current_output

                if not self.initialized:
                    logger.info("Initializing Controller Table")
                    row.field_key_index.setpoint.value = v.setpoint
                    row.field_key_index.max_output.value = v.max_output
                    switch = row.switch_toggle.switch
                    switch.setChecked(v.pid_on)
                    self.initialized = True

                # update state.
                on = v.pid_on


                if abs(v.value - v.working_setpoint) <= STABLE_THRESHOLD_C:
                    parity = 0
                elif v.value < v.setpoint:
                    parity = 1
                else:
                    parity = -1
                standby = all([x < STANDBY_TEMP_C for x in [v.value, v.setpoint, v.working_setpoint]])
                row.field_key_index.state.value = ControllerState(on, parity, standby)

            except Exception:
                traceback.print_exc()
        self.model.layoutChanged.emit()



if __name__ == "__main__":
    app = QApplication([])
    controllers = global_ctc_100_manager.controllers
    window = QMainWindow()
    table = TemperatureControllerTable(controllers)
    window.setCentralWidget(table)
    window.show()
    app.exec()









