'''
:@Author: wy9933
:@Date: 2023/9/13 23:09:37
:@LastEditors: wy9933
:@LastEditTime: 2023/9/13 23:09:37
:Description: 右键点击页面或按钮，在鼠标当前位置弹出menu
:Copyright: Copyright (©)}) 2023 wy9933. All rights reserved.
'''
import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("右键弹出Menu")
        self.setGeometry(500, 200, 500, 500)

        # 右键菜单
        self.rightMenu = QMenu(self)
        self.actionA = QAction("A", self)
        self.actionB = QAction("B", self)
        self.rightMenu.addAction(self.actionA)
        self.rightMenu.addAction(self.actionB)

        # *右键点击窗口本体弹出菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.init_rightMenu)

        # 加入一个按钮
        self.button = QPushButton("按钮", self)
        self.button.setGeometry(200, 100, 50, 50)

        # 按钮菜单
        self.buttonMenu = QMenu(self)
        self.actionC = QAction("C", self)
        self.actionD = QAction("D", self)
        self.buttonMenu.addAction(self.actionC)
        self.buttonMenu.addAction(self.actionD)

        # *右键点击按钮弹出菜单
        self.button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.button.customContextMenuRequested.connect(self.init_buttonMenu)

    def init_rightMenu(self):
        """初始化右键菜单
        """
        self.rightMenu.popup(QCursor.pos())

    def init_buttonMenu(self):
        """初始化按钮的右键菜单
        """
        self.buttonMenu.popup(QCursor.pos())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())