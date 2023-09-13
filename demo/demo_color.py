'''
:@Author: wy9933
:@Date: 2023/9/13 23:09:37
:@LastEditors: wy9933
:@LastEditTime: 2023/9/13 23:09:37
:Description: 设置QWidget的颜色
:Copyright: Copyright (©)}) 2023 wy9933. All rights reserved.
'''
import sys
import typing
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

import numpy as np

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("设置QWidget颜色")
        self.setGeometry(500, 200, 500, 500)

        # 加入一个按钮
        self.button = QPushButton("修改颜色", self)
        self.button.setGeometry(150, 100, 200, 50)
        self.button.clicked.connect(self.changeColor)

        # 设置颜色 R G B alpha
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(255, 255, 255, 255))
        self.setPalette(palette)


    def changeColor(self):
        # 随机获得一个颜色
        new_color = np.random.randint(0, 255, 4)
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(new_color[0], new_color[1], new_color[2], new_color[3]))
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())