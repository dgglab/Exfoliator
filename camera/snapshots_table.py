import os

from PyQt5.QtWidgets import QTableView, QApplication, QWidget, QFrame, QPushButton, QHBoxLayout, QVBoxLayout,\
    QDialog, QLabel, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QPixmap
import random, time

from typing import List
import typing

import sqlite3
import numpy
from PIL import Image

CREATE_TABLE_SQL = '''CREATE TABLE snapshots
                       (name text, timestamp text, filepath)'''
INSERT_TEMPLATE = '''
INSERT INTO snapshots values ("{name}", "{timestamp}", "{filepath}")'''



class SnapshotModel(QAbstractTableModel):
    headers = ['name', 'timestamp', 'filepath']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = sqlite3.connect(":memory:")
        cur = self.conn.cursor()
        # Create table
        cur.execute(CREATE_TABLE_SQL)
        cur.execute(INSERT_TEMPLATE.format(**dict(name="test", timestamp="test", filepath="test")))
        self.conn.commit()

    @property
    def values(self) -> List[tuple]:
        return list(self.conn.execute("SELECT * FROM snapshots"))

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole:
            return self.values[index.row()][index.column()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(list(self.conn.execute("SELECT * FROM snapshots")))

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 3

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal:
            return self.headers[section]
        # elif orientation == Qt.Vertical:
        #     return self.values[section][0]


class SnapshotsTable(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout(self)
        
        self.table_view = QTableView()
        self.model = SnapshotModel()
        self.table_view.setModel(self.model)

        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)

        view_img_btn = QPushButton("View Image")
        view_img_btn.clicked.connect(self.on_view_img_click)

        del_img_btn = QPushButton("Delete Image")
        del_img_btn.clicked.connect(self.on_del_img_click)

        add_img_btn = QPushButton("Add Image")
        add_img_btn.clicked.connect(self.on_add_img_click)

        for i in [view_img_btn, del_img_btn, add_img_btn]:
            btn_layout.addWidget(i)
        btn_frame.setLayout(btn_layout)
        
        main_layout.addWidget(self.table_view)
        main_layout.addWidget(btn_frame)

        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        
    def on_view_img_click(self):
        selected = self.model.values[self.table_view.selectedIndexes()[0].row()][-1]
        from image_viewer import QImageViewer
        self.d = QImageViewer()
        print('set open')
        self.d.set_open(selected)
        self.d.fitToWindowAct.setChecked(True)
        self.d.fitToWindow()
        self.d.show()
        print('shown')

    def on_del_img_click(self):
        selected = self.table_view.selectedIndexes()
        selected = list(set([s.row() for s in selected]))

        values = self.model.values
        print(values)
        self.model.beginRemoveRows(QModelIndex(), selected[0], selected[-1])
        for s in selected:
            row = values[s]
            self.model.conn.execute(f'DELETE FROM snapshots WHERE name="{row[0]}"')
            self.model.conn.commit()
            path: str = str(row[-1])
            print(path)
            os.remove(path)
        self.model.endRemoveRows()
        print("removed rows")

    def on_add_img_click(self):
        print("ADDING IMAGE")
        name = f"img_{random.randint(1, 10000)}"
        timestamp = str(time.time())
        filepath = f'{name}.png'
        random_img_data = dict(name=f"My image {name}", timestamp=timestamp, filepath=filepath)

        imarray = numpy.random.rand(100, 100, 3) * 255
        im = Image.fromarray(imarray.astype('uint8')).convert('RGBA')
        im.save(filepath)

        msg = INSERT_TEMPLATE.format(**random_img_data)
        print(msg)
        self.model.beginInsertRows(self.model.index(self.model.rowCount(), 0), 0, 0)
        self.model.conn.execute(msg)
        self.model.conn.commit()
        self.model.endInsertRows()



if __name__ == "__main__":
    app = QApplication([])
    table = SnapshotsTable()
    table.show()
    app.exec()
