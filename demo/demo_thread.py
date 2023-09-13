'''
:@Author: wy9933
:@Date: 2023/9/13 23:34:31
:@LastEditors: wy9933
:@LastEditTime: 2023/9/13 23:34:31
:Description: 开启一个线程，更新窗口内容
:Copyright: Copyright (©)}) 2023 wy9933. All rights reserved.
'''

import sys
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

class ColorThread(QThread):
    _signal = pyqtSignal(int, int, int)
    def __init__(self) -> None:
        super().__init__()

    def run(self):
        """线程执行逻辑
        """
        while True:
            time.sleep(1)
            # 随机获得一个颜色
            new_color = np.random.randint(0, 255, 3)
            self._signal.emit(new_color[0], new_color[1], new_color[2])


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("开启线程修改窗口颜色及文字")
        self.setGeometry(500, 200, 500, 500)

        # 加入一个按钮
        self.lineEdit = QLineEdit("当前颜色：255 255 255", self)
        self.lineEdit.setGeometry(150, 100, 200, 50)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setAlignment(Qt.AlignCenter)

        # 设置颜色 R G B
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(255, 255, 255))
        self.setPalette(palette)

        # 设置线程并开启
        self.colorThread = ColorThread()
        self.colorThread._signal.connect(self.changeColor)
        self.colorThread.start()


    def changeColor(self, R, G, B):
        # 更改颜色
        palette = self.palette()
        palette.setColor(QPalette.Background, QColor(R, G, B))
        self.setPalette(palette)

        # 更改文字
        self.lineEdit.setText("当前颜色：%d %d %d" % (R, G, B))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())