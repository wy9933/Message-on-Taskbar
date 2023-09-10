'''
:@Author: wy9933
:@Date: 2023/9/11 00:12:09
:@LastEditors: wy9933
:@LastEditTime: 2023/9/11 00:36:48
:Description: show some message in win10 taskbar
:Copyright: Copyright © 2023 VQuish. All rights reserved.
'''
import sys
from PyQt5 import QtGui
import win32api, win32con, win32gui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class TaskbarWidget(QWidget):
    def __init__(self) -> None:
        """初始化TaskbarWidget
        """
        super().__init__()

        # 获取win10本身taskbar的各级window
        m_hTaskbar = win32gui.FindWindow("Shell_TrayWnd", None)
        m_hBar = win32gui.FindWindowEx(m_hTaskbar, 0, "ReBarWindow32", None)
        m_hMin = win32gui.FindWindowEx(m_hBar, 0, "MSTaskSwWClass", None)
        
        # 将显示应用图标的window缩短长度
        b = win32gui.GetWindowRect(m_hBar)
        win32gui.MoveWindow(m_hMin, 0, 0, b[2] - b[0] - 300, b[3] - b[1], True)

        # 设定TaskbarWidget的位置和长度，并指定parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(b[2] - b[0] - 300, 0, 300, b[3] - b[1])
        win32gui.SetParent(int(self.winId()), m_hBar)

        # 右键菜单
        self.rightMenu = QMenu(self)
        self.actionA = QAction("退出", self)
        # *右键点击弹出菜单的设置和绑定
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.init_rightMenu)

    def exitapp(self):
        """退出
        """
        app = QApplication.instance()
        app.quit()

    def init_rightMenu(self):
        """初始化右键菜单
        """
        self.rightMenu.addAction(self.actionA)
        self.actionA.triggered.connect(self.exitapp)
        self.rightMenu.popup(QCursor.pos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tw = TaskbarWidget()
    tw.show()
    sys.exit(app.exec_())
    pass