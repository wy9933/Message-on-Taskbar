# https://www.wangxingyang.com/windowsfundplugin.html
import sys, requests, time, win32gui, json
import win32api, win32con
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pickle
import os
import base64
from functools import partial
from urllib.parse import quote
from imgpy import *
from pyqt_toast import Toast
import ctypes


img_up = "images/smiley.bmp"
class BackendThread(QObject):
    # 通过类成员对象定义信号
    update_date = pyqtSignal(str)
    fundCodes = []
    interval = 10
    fzkey = 0
    fzval = 0
    fzfh = 0
    currentPage = 1
    hot_currentPage = 1
    pageCount = 0
    fzlist = ['dwjz', 'gsz', 'gszzl']
    au9999 = {}
    sh000001 = {}
    display_list = ['fund', 'hot', 'mov']
    display_type = 0
    display_num = 0

    # if not os.path.exists('db.pkl'):
    #     try:
    #         file = open('db.pkl', 'w')
    #         file.close()
    #     except:
    #         win32api.MessageBox(0, "无法创建文件，没有权限！请检查", "提醒", win32con.MB_OK)
    #         sys.exit()

    # if os.path.getsize('db.pkl') > 0:
    #     pkl_file = open('db.pkl', 'rb+')
    #     fundCodes, interval, fzkey, fzval, fzfh, display_type, display_num = pickle.load(pkl_file)
    #     pkl_file.close()

    def refresh_fund(self):
        t = time.time()
        json_content = []
        status = "ok"
        msg = "success"
        headers = {
            'Host': 'hq.sinajs.cn',
            'Referer': 'https://finance.sina.com.cn/realstock/company/sh000001/nc.shtml'
        }
        ##  】上证指数
        apiUrl = "https://hq.sinajs.cn/rn=" + str(int(t)) + "&list=s_sh000001"
        try:
            retstr = requests.get(apiUrl, headers=headers).text
            retArrtmp = retstr.split('"')
            retArr = retArrtmp[1].split(",")
            self.sh000001 = {
                "name": retArr[0],
                "price": retArr[1]
            }
        except:
            self.sh000001 = {
                "name": "上证指数",
                "price": "获取异常"
            }
            print('获取上证指数异常')
        ## 黄金
        apiUrl = "https://api.jijinhao.com/quoteCenter/realTime.htm?codes=JO_71&_=" + str(int(t))
        try:
            retstr = requests.get(apiUrl).text
            retstr = retstr.replace("var quote_json =", "")
            jsonData = json.loads(retstr)
            self.au9999 = {
                "name": jsonData["JO_71"]["showName"],
                "price": jsonData["JO_71"]["q5"]
            }
        except:
            self.au9999 = {
                "name": "黄金9999",
                "price": "获取异常"
            }
            print('获取黄金异常')

        data_ret = {
            "status": status,
            "reminder": {
                "fzkey": self.fzlist[self.fzkey],
                "fzval": self.fzval,
                "fzfh": self.fzfh
            },
            "reference": {
                "AU9999": self.au9999,
                "SH000001": self.sh000001
            },
            "msg": msg,
            "type": self.display_type,
            "data": json_content
        }

        data_count = len(self.fundCodes)
        limit = 3
        if int(data_count % limit) == 0:
            self.pageCount = int(data_count / limit)
        else:
            self.pageCount = int(data_count / limit) + 1
        if self.currentPage > self.pageCount:
            self.currentPage = 1
        start_index = (self.currentPage - 1) * limit
        last_limit = 9999
        if self.currentPage == self.pageCount:
            last_limit = data_count % limit  # 最后一页的数据条数
        if last_limit == 0:
            last_limit = limit
        if last_limit != 9999:
            limit = last_limit
        end_index = start_index + limit
        list = self.fundCodes[start_index:end_index]
        num = 0
        for fundcode in list:
            apiUrl = "http://fundgz.1234567.com.cn/js/" + fundcode + ".js?rt=" + str(int(t))
            try:
                retstr = requests.get(apiUrl).text
                # print(retstr)
                retstr = retstr.replace("jsonpgz(", "").replace(");", "")
                # print(retstr)
                if retstr == "":
                    jsonData = {
                        "fundcode": fundcode,
                        "name": "暂无数据......",
                        "jzrq": "--",
                        "dwjz": "0.0",
                        "gsz": "0.0",
                        "gszzl": "0.0",
                        "gztime": "--"
                    }
                else:
                    jsonData = json.loads(retstr)
                json_content.append(jsonData)
            except requests.exceptions.ConnectionError:
                # print("网络连接异常......")
                jsonData = {
                    "fundcode": fundcode,
                    "name": "网络连接异常......",
                    "jzrq": "--",
                    "dwjz": "0.0",
                    "gsz": "0.0",
                    "gszzl": "0.0",
                    "gztime": "--"
                }
                json_content.append(jsonData)
            except requests.exceptions.ChunkedEncodingError:
                # print("Chunked编码异常......")
                jsonData = {
                    "fundcode": fundcode,
                    "name": "Chunked编码异常......",
                    "jzrq": "--",
                    "dwjz": "0.0",
                    "gsz": "0.0",
                    "gszzl": "0.0",
                    "gztime": "--"
                }
                json_content.append(jsonData)
            except:
                jsonData = {
                    "fundcode": fundcode,
                    "name": "未知异常......",
                    "jzrq": "--",
                    "dwjz": "0.0",
                    "gsz": "0.0",
                    "gszzl": "0.0",
                    "gztime": "--"
                }
                json_content.append(jsonData)
            num = num + 1
        # print(json.dumps(data_ret, indent=2))
        self.update_date.emit(json.dumps(data_ret, indent=2))
        self.currentPage = self.currentPage + 1
        time.sleep(self.interval)

    def refresh_hot(self):
        status = "ok"
        msg = "success"
        all_data = []
        try:
            apiUrl = "https://weibo.com/ajax/side/hotSearch"
            ret_json = requests.get(apiUrl).json()
            for data in ret_json["data"]["realtime"]:
                if "ad_info" in data:
                    all_data.append(data)
        except:
            print("获取热搜异常")

        data_count = (self.display_num * 3 + 3)
        limit = 3
        if int(data_count % limit) == 0:
            self.pageCount = int(data_count / limit)
        else:
            self.pageCount = int(data_count / limit) + 1
        if self.hot_currentPage > self.pageCount:
            self.hot_currentPage = 1
        start_index = (self.hot_currentPage - 1) * limit
        last_limit = 9999
        if self.hot_currentPage == self.pageCount:
            last_limit = data_count % limit  # 最后一页的数据条数
        if last_limit == 0:
            last_limit = limit
        if last_limit != 9999:
            limit = last_limit
        end_index = start_index + limit
        list = all_data[start_index:end_index]
        data_ret = {
            "status": status,
            "msg": msg,
            "type": self.display_type,
            "data": list
        }
        self.update_date.emit(json.dumps(data_ret, indent=2))
        # print(json.dumps(data_ret, indent=2))
        time.sleep(self.interval)
        self.hot_currentPage = self.hot_currentPage + 1

    def refresh_movie(self):
        status = "ok"
        msg = "success"
        all_data = []
        headers = {
            'Host': 'i.maoyan.com',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Mobile Safari/537.36'
        }
        try:
            apiUrl = "https://i.maoyan.com/api/mmdb/movie/v3/list/hot.json"
            ret_json = requests.get(apiUrl, headers=headers).json()
            # print(ret_json)
            for data in ret_json["data"]["hot"]:
                all_data.append(data)
        except:
            print("获取电影排行榜异常异常")

        data_count = (self.display_num * 3 + 3)
        limit = 3
        if int(data_count % limit) == 0:
            self.pageCount = int(data_count / limit)
        else:
            self.pageCount = int(data_count / limit) + 1
        if self.hot_currentPage > self.pageCount:
            self.hot_currentPage = 1
        start_index = (self.hot_currentPage - 1) * limit
        last_limit = 9999
        if self.hot_currentPage == self.pageCount:
            last_limit = data_count % limit  # 最后一页的数据条数
        if last_limit == 0:
            last_limit = limit
        if last_limit != 9999:
            limit = last_limit
        end_index = start_index + limit
        list = all_data[start_index:end_index]
        data_ret = {
            "status": status,
            "msg": msg,
            "type": self.display_type,
            "data": list
        }
        self.update_date.emit(json.dumps(data_ret, indent=2))
        # print(json.dumps(data_ret, indent=2))
        time.sleep(120)
        self.hot_currentPage = self.hot_currentPage + 1

    def run(self):
        while 1:
            if self.display_type == 0:
                self.refresh_hot()
            elif self.display_type == 1:
                self.refresh_fund()
            elif self.display_type == 2:
                self.refresh_movie()

    def set_interval(self, value):
        self.interval = value

    def set_fundCodes(self, value):
        self.fundCodes = value

    def set_fzkey(self, value):
        self.fzkey = value

    def set_fzval(self, value):
        self.fzval = value

    def set_fzfh(self, value):
        self.fzfh = value

    def set_display_type(self, value):
        self.display_type = value

    def set_display_num(self, value):
        self.display_num = value


class SetDialog(QWidget):
    def __init__(self):
        super(SetDialog, self).__init__()
        self.backendSD = ""
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(210, 200)
        self.setWindowTitle('设置')
        fund_codes = []
        interval1 = 10
        fzkey = 0
        fzval = 0.3
        fzfh = 0
        display_type = 0
        display_num = 0
        self.setWindowFlags(Qt.FramelessWindowHint)

        # if os.path.getsize('db.pkl') > 0:
        #     pkl_file = open('db.pkl', 'rb+')
        #     fund_codes, interval1, fzkey, fzval, fzfh, display_type, display_num = pickle.load(pkl_file)
        #     pkl_file.close()
        # -------- 更新时间
        self.interval = QLabel(self)
        self.interval.setText("刷新时间:")
        self.interval.setGeometry(10, 5, 60, 20)

        pngData = base64.b64decode(img_settings)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.setWindowIcon(QIcon(pix))

        self.val = QLabel(self)
        self.val.setText(str(interval1) + "s")
        self.val.setGeometry(185, 5, 60, 20)

        self.sld = QSlider(Qt.Horizontal, self)
        self.sld.setMinimum(10)
        self.sld.setMaximum(180)
        self.sld.setValue(interval1)
        self.sld.setGeometry(70, 5, 110, 20)
        self.sld.valueChanged[int].connect(self.changevalue)

        # --------基金列表操作

        self.fundlist = QLabel(self)
        self.fundlist.setText("基金列表:")
        self.fundlist.setGeometry(10, 35, 60, 20)
        self.listView = QListWidget(self)
        self.listView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        for code in fund_codes:
            self.listView.addItem(code)
        self.listView.setGeometry(70, 35, 55, 65)

        self.total_label = QLabel(self)
        self.total_label.setText("总数: " + str(self.listView.count()))
        self.total_label.setGeometry(135, 30, 60, 20)
        self.total_label.setStyleSheet("color: blue;font-size:10px")

        self.code = QLineEdit(self)
        self.code.setPlaceholderText("基金代码")
        reg = QRegExp('[0-9]{6}$')
        validator = QRegExpValidator(self)
        validator.setRegExp(reg)
        self.code.setValidator(validator)
        self.code.setGeometry(135, 50, 70, 20)

        self.minus = QPushButton(self)
        pngData = base64.b64decode(img_minus)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.minus.setIcon(QIcon(pix))
        self.minus.setIconSize(QSize(15, 15))  # 设置icon大小
        self.minus.setGeometry(160, 75, 15, 15)
        self.minus.setFlat(True)
        self.minus.clicked.connect(self.minus_fund)

        self.plus = QPushButton(self)
        pngData = base64.b64decode(img_plus)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.plus.setIcon(QIcon(pix))
        self.plus.setIconSize(QSize(15, 15))
        self.plus.setGeometry(185, 75, 15, 15)
        self.plus.setFlat(True)
        self.plus.clicked.connect(self.add_fund)
        # --- 设置提醒功能

        self.btnclock = QPushButton(self)
        pngData = base64.b64decode(img_clock)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.btnclock.setIcon(QIcon(pix))
        self.btnclock.setFlat(True)
        self.btnclock.setGeometry(5, 110, 20, 20)

        self.remind = QLabel(self)
        self.remind.setText("提醒:")
        self.remind.setGeometry(25, 110, 60, 20)

        self.cb = QComboBox(self)
        self.cb.addItems(['单位净值', '估算净值', '估算涨幅'])
        self.cb.setCurrentIndex(fzkey)

        # 'QWidget{background-color:rgb(0,0,0)}'
        self.cb.setStyleSheet("QComboBox::drop-down{border:none;background: transparent; }\
                              QComboBox::down-arrows{border:none; background: transparent;}\
                              QComboBox::down-arrow:pressed { background: transparent; }")
        self.cb.setGeometry(55, 110, 75, 20)

        self.cb1 = QComboBox(self)
        self.cb1.addItems(['>=', '<='])
        self.cb1.setCurrentIndex(fzfh)
        self.cb1.setStyleSheet("QComboBox::drop-down{border:none;background: transparent; }\
                                      QComboBox::down-arrows{border:none; background: transparent;}\
                                      QComboBox::down-arrow:pressed { background: transparent; }")
        self.cb1.setGeometry(135, 110, 35, 20)

        self.fz = QLineEdit(self)
        self.fz.setPlaceholderText("阈值")
        self.fz.setText(str(fzval))
        reg = QRegExp('^(\-|\+)?\d+(\.\d+)?$')
        validator = QRegExpValidator(self)
        validator.setRegExp(reg)
        self.fz.setValidator(validator)
        self.fz.setGeometry(175, 110, 30, 20)

        self.btndisplay = QPushButton(self)
        pngData = base64.b64decode(img_monitor)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.btndisplay.setIcon(QIcon(pix))
        self.btndisplay.setFlat(True)
        self.btndisplay.setGeometry(5, 140, 20, 20)

        self.display = QLabel(self)
        self.display.setText("显示:")
        self.display.setGeometry(25, 140, 60, 20)

        self.cb_type = QComboBox(self)
        self.cb_type.addItems(['热搜', '基金', '电影'])
        self.cb_type.setCurrentIndex(display_type)
        self.cb_type.setStyleSheet("QComboBox::drop-down{border:none;background: transparent; }\
                                      QComboBox::down-arrows{border:none; background: transparent;}\
                                      QComboBox::down-arrow:pressed { background: transparent; }")
        self.cb_type.setGeometry(55, 140, 50, 20)
        self.cb_type.currentIndexChanged.connect(self.selectionchange)

        self.display0 = QLabel(self)
        self.display0.setText("条数:")
        self.display0.setGeometry(110, 140, 60, 20)

        self.cb_num = QComboBox(self)
        self.cb_num.addItems(['3', '6', '9', '12', '15', '18'])
        self.cb_num.setCurrentIndex(display_num)
        self.cb_num.setStyleSheet("QComboBox::drop-down{border:none;background: transparent; }\
                                              QComboBox::down-arrows{border:none; background: transparent;}\
                                              QComboBox::down-arrow:pressed { background: transparent; }")
        self.cb_num.setGeometry(140, 140, 35, 20)

        if self.cb_type.currentText() == "基金":
            self.cb_num.hide()
            self.display0.hide()
        elif self.cb_type.currentText() == "热搜":
            self.cb_num.show()
            self.display0.show()



        self.btn = QPushButton('保存', self)  # 设置按钮和按钮名称
        pngData = base64.b64decode(img_disk)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.btn.setIcon(QIcon(pix))
        self.btn.setGeometry(90, 170, 50, 20)  # 前面是按钮左上角坐标，后面是按钮大小
        self.btn.clicked.connect(self.slot_btn_function)  # 将信号连接到槽

        self.btnclose = QPushButton('关闭', self)  # 设置按钮和按钮名称
        pngData = base64.b64decode(img_logout)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.btnclose.setIcon(QIcon(pix))
        self.btnclose.setGeometry(150, 170, 50, 20)  # 前面是按钮左上角坐标，后面是按钮大小
        self.btnclose.clicked.connect(self.close_setting)  # 将信号连接到槽

    def close_setting(self):
        self.close()

    def selectionchange(self):
        if self.cb_type.currentText() == "基金":
            self.cb_num.hide()
            self.display0.hide()
        elif self.cb_type.currentText() == "热搜":
            self.cb_num.show()
            self.display0.show()


    def changevalue(self, value):
        self.val.setText(str(value) + "s")

    def minus_fund(self):
        item = self.listView.currentItem()
        self.listView.takeItem(self.listView.row(item))
        self.total_label.setText("总数: " + str(self.listView.count()))

    def add_fund(self):
        if self.code.text() == "":
            return
        if self.listView.count() < 9:
            items = self.listView.findItems(self.code.text(), Qt.MatchContains)
            if len(items) <= 0:
                if self.listView.selectedItems():
                    self.listView.insertItem(self.listView.currentIndex().row(), self.code.text())
                else:
                    self.listView.addItem(self.code.text())
                self.code.setText("")
                self.total_label.setText("总数: " + str(self.listView.count()))
            else:
                QMessageBox.warning(self, "警告", "已经添加代码为 [" + self.code.text() + "] 的基金", QMessageBox.Cancel)

        else:
            QMessageBox.warning(self, "警告", "目前只能添加九只基金！", QMessageBox.Cancel)

    def slot_btn_function(self):
        # print(self.sld.value())
        widgetres = []
        # 获取listwidget中条目数
        count = self.listView.count()
        # 遍历listwidget中的内容
        for i in range(count):
            widgetres.append(self.listView.item(i).text())
        # print(widgetres)
        self.backendSD.set_fundCodes(widgetres)
        self.backendSD.set_interval(self.sld.value())
        self.backendSD.set_fzkey(self.cb.currentIndex())
        self.backendSD.set_fzfh(self.cb1.currentIndex())
        self.backendSD.set_fzval(self.fz.text())
        self.backendSD.set_display_type(self.cb_type.currentIndex())
        self.backendSD.set_display_num(self.cb_num.currentIndex())

        pickle_file = open('db.pkl', 'wb')
        pickle.dump((widgetres, self.sld.value(),
                     self.cb.currentIndex(),
                     self.fz.text(),
                     self.cb1.currentIndex(),
                     self.cb_type.currentIndex(),
                     self.cb_num.currentIndex()
                     ), pickle_file)
        pickle_file.close()
        self.close()


class AboutDialog(QWidget):
    def __init__(self):
        super(AboutDialog, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(265, 190)
        self.setWindowTitle('关于')
        self.border_width = 8
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        label0 = QLabel(self)
        label0.setAlignment(Qt.AlignCenter)
        label0.setGeometry(8, 8, 250, 40)
        label0.setText("基金/热搜看板")
        label0.setStyleSheet("color:blue;font-size:18px;font-weight:bold;background: rgba(0,0,0,0.1);")

        label1 = QLabel(self)
        label1.setAlignment(Qt.AlignLeft)
        label1.setGeometry(13, 53, 240, 90)
        label1.setText("  这是一个能在任务栏即时查看基金变化的插件，能够添监控九只基金。当然也可以更多，代码中可以自己修改。"
                       "可以设置阈值，当达到阈值是会有弹窗提醒，可以修改更新时间，增加删除相关基金等等"
                       "同时也能够查看当前热搜")
        label1.setWordWrap(True)

        label2 = QLabel(self)
        label2.setAlignment(Qt.AlignCenter)
        label2.setGeometry(0, 128, 240, 13)

        label2.setText("作者：彤爸比")

        label3 = QLabel(self)
        label3.setAlignment(Qt.AlignCenter)
        label3.setGeometry(0, 147, 240, 13)
        label3.setStyleSheet("color:blue;font-size:12px;font-weight:bold;")
        label3.setText("<a style='color: red; text-decoration: none' href=https://www.wangxingyang.com>https://www.wangxingyang.com")
        label3.setOpenExternalLinks(True)

        about_close = QPushButton('关闭', self)  # 设置按钮和按钮名称
        about_close.setStyleSheet("background-color: transparent")
        about_close.setCursor(Qt.PointingHandCursor)
        pngData = base64.b64decode(img_logout)
        pix = QPixmap()
        pix.loadFromData(pngData)
        about_close.setIcon(QIcon(pix))
        about_close.setGeometry(108, 160, 50, 20)  # 前面是按钮左上角坐标，后面是按钮大小
        about_close.clicked.connect(self.close_about)  # 将信号连接到槽

    def paintEvent(self, event):
        # 阴影
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        bg_color = QColor(102, 204, 255, 255)
        pat = QPainter(self)
        pat.setRenderHint(pat.Antialiasing)

        pat.fillPath(path, QBrush(bg_color))

        color = QColor(192, 192, 192, 50)

        for i in range(10):
            i_path = QPainterPath()
            i_path.setFillRule(Qt.WindingFill)
            ref = QRectF(10 - i, 10 - i, self.width() - (10 - i) * 2, self.height() - (10 - i) * 2)
            # i_path.addRect(ref)
            i_path.addRoundedRect(ref, self.border_width, self.border_width)
            color.setAlpha(150 - i ** 0.5 * 50)
            pat.setPen(color)
            pat.drawPath(i_path)

        # 圆角
        pat2 = QPainter(self)
        pat2.setRenderHint(pat2.Antialiasing)  # 抗锯齿
        #pat2.setBrush(Qt.white)
        #pat2.setPen(Qt.transparent)

        pat2.setBrush(bg_color)
        pat2.setPen(bg_color)


        rect = self.rect()
        rect.setLeft(9)
        rect.setTop(9)
        rect.setWidth(rect.width() - 9)
        rect.setHeight(rect.height() - 9)
        pat2.drawRoundedRect(rect, 4, 4)

    def close_about(self):
        self.close()


class TaskWidget(QWidget):
    fzdcit = {'dwjz': "单位净值", 'gsz': "估算净值", 'gszzl': '估算涨幅'}
    refresh_count = 0
    tb_width = 0
    def __init__(self):
        super().__init__()
        print("开始 初始化任务栏小组件")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        m_hTaskbar = win32gui.FindWindow("Shell_TrayWnd", None)
        m_hBar = win32gui.FindWindowEx(m_hTaskbar, 0, "ReBarWindow32", None)
        m_hMin = win32gui.FindWindowEx(m_hBar, 0, "MSTaskSwWClass", None)

        b = win32gui.GetWindowRect(m_hBar)
        self.setGeometry(b[2] - b[0] - 300, 0, 300, b[3] - b[1])
        win32gui.MoveWindow(m_hMin, 0, 0, b[2] - b[0] - 300, b[3] - b[1], True)
        win32gui.SetParent(int(self.winId()), m_hBar)

        # WndProcType = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int)
        # GWL_WNDPROC = -4
        # oldWndProc = win32gui.SetWindowLong(m_hBar, win32con.GWL_WNDPROC, self.MyWndProc)
        # ctypes.windll.user32.SetWindowLongW(m_hBar, GWL_WNDPROC, WndProcType(self.MyWndProc))

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.create_rightmenu)  # 连接到菜单显示函数

        label1 = QLabel(self)
        label1.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label1.setObjectName("label1")
        label1.setGeometry(14, 1, 260, 13)
        label1.setText("Loading.....")
        label1.setToolTip("Loading.....")

        labelimg1 = QLabel(self)
        labelimg1.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        labelimg1.setObjectName("labelimg1")
        labelimg1.setGeometry(0, 1, 13, 13)
        png_data = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(png_data)
        labelimg1.setPixmap(pix)
        labelimg1.setScaledContents(True)

        label2 = QLabel(self)
        label2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label2.setObjectName("label2")
        label2.setGeometry(14, 14, 260, 13)
        label2.setText("Loading.....")
        label2.setToolTip("Loading.....")

        labelimg2 = QLabel(self)
        labelimg2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        labelimg2.setObjectName("labelimg2")
        labelimg2.setGeometry(0, 14, 13, 13)
        png_data = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(png_data)
        labelimg2.setPixmap(pix)
        labelimg2.setScaledContents(True)

        label3 = QLabel(self)
        label3.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label3.setObjectName("label3")
        label3.setGeometry(14, 27, 260, 13)
        label3.setText("Loading.....")
        label3.setToolTip("Loading.....")

        labelimg3 = QLabel(self)
        labelimg3.setAlignment(Qt.AlignCenter| Qt.AlignVCenter)
        labelimg3.setObjectName("labelimg3")
        labelimg3.setGeometry(0, 27, 13, 13)
        png_data = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(png_data)
        labelimg3.setPixmap(pix)
        labelimg3.setScaledContents(True)

        labelweather = QLabel(self)
        labelweather.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        labelweather.setObjectName("labelweather")
        labelweather.setGeometry(260, 0, 40, 40)
        # labelweather.setStyleSheet('background-color: #ebedee')
        png_data = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(png_data)
        labelweather.setPixmap(pix)
        # movie = QMovie('img/loading.gif')
        # labelweather.setMovie(movie)
        # movie.start()
        labelweather.setScaledContents(True)

        # label4 = QLabel(self)
        # label4.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # label4.setObjectName("label4")
        # label4.setGeometry(260, 30, 40, 10)
        # label4.setText("20  30")

        self.groupBox_menu = QMenu(self)
        pngData = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.actionC = QAction(QIcon(pix), u'关于', self)
        pngData = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(pngData)
        self.actionA = QAction(QIcon(pix), u'设置', self)

        pngData = base64.b64decode(img_up)
        pix = QPixmap()
        pix.loadFromData(pngData)

        self.actionB = QAction(QIcon(pix), u'退出程序', self)

        self.thread = QThread()
        self.backend = BackendThread()
        self.backend.update_date.connect(self.handleDisplay)
        self.backend.moveToThread(self.thread)
        self.thread.started.connect(self.backend.run)
        self.thread.start()
        print("结束 初始化任务栏小组件")

    def MyWndProc(hwnd, msg, wParam, lParam):  # wParam 值为鼠标按键的信息，而 lParam 则储存鼠标的坐标
        print(msg)

    def exitapp(self):
        app = QApplication.instance()
        app.quit()

    def setting(self):
        self.settingDialog = SetDialog()
        self.settingDialog.show()
        self.settingDialog.backendSD = self.backend

    def aboutme(self):
        self.about_dialog = AboutDialog()
        self.about_dialog.show()
        pass

    def create_rightmenu(self):
        #print("create_rightmenu")
        #self.actionA.setShortcut('Ctrl+S')  # 设置快捷键
        self.groupBox_menu.addAction(self.actionA)  # 基金列表
        self.groupBox_menu.addAction(self.actionC)  # 基金列表
        self.groupBox_menu.addAction(self.actionB)  # 更新频率
        self.actionA.triggered.connect(self.setting)
        self.actionB.triggered.connect(self.exitapp)
        self.actionC.triggered.connect(self.aboutme)
        self.groupBox_menu.popup(QCursor.pos())

    def changeContent(self, text, timer):
        toast = Toast(text=text, duration=2)
        toast.show()
        toast.setPosition(QPoint(self.x() + 90, self.y() - 20))
        timer.stop()
        timer.deleteLater()
        pass

    def display_fund(self, data):
        print("开始 更新基金信息")
        num = 0
        timeTick = 0
        jsonDatas = json.loads(data)
        if jsonDatas["status"] != "ok":
            for i in range(1, 4):
                label = self.findChild(QLabel, "label" + str(i))
                label.setAlignment(Qt.AlignLeft)
                label.setText(jsonDatas["msg"])
                label.setStyleSheet('color: blue')
            return
        fzkey = jsonDatas["reminder"]["fzkey"]
        fzval = jsonDatas["reminder"]["fzval"]
        fzfh = jsonDatas["reminder"]["fzfh"]

        auname = jsonDatas["reference"]["AU9999"]["name"]
        auprice = jsonDatas["reference"]["AU9999"]["price"]

        shname = jsonDatas["reference"]["SH000001"]["name"]
        shprice = jsonDatas["reference"]["SH000001"]["price"]

        for jsonData in jsonDatas["data"]:
            label = self.findChild(QLabel, "label" + str(num + 1))
            labelimg = self.findChild(QLabel, "labelimg" + str(num + 1))
            label.setAlignment(Qt.AlignLeft)

            gszzl = jsonData['gszzl']
            fundcode = jsonData['fundcode']
            name = jsonData['name']
            dwjz = jsonData['dwjz']
            gsz = jsonData['gsz']
            gztime = jsonData['gztime']

            if fzfh == 0:
                if float(jsonData[fzkey]) >= float(fzval):
                    msgtext = name + " | 基金" + self.fzdcit[fzkey] + "涨到阈值[ " + fzval + " ]了！"
                    timer = QTimer()
                    timer.timeout.connect(partial(self.changeContent, msgtext, timer))
                    timer.start(3000 * int(timeTick))
                    timeTick = timeTick + 1
            else:
                if float(jsonData[fzkey]) <= float(fzval):
                    msgtext = name + " | 基金" + self.fzdcit[fzkey] + "跌到阈值[ " + fzval + " ]了！"
                    timer = QTimer()
                    timer.timeout.connect(partial(self.changeContent, msgtext, timer))
                    timer.start(3000 * int(timeTick))
                    timeTick = timeTick + 1
            tmp_str = gszzl if float(gszzl) < 0 else "+" + gszzl
            label.setText(tmp_str + " | " + fundcode + " - " + name)
            label.setToolTip(auname + " : " + str(auprice) +
                             "\n" + shname + "  : " + shprice +
                             "\n----------------------------" +
                             "\n" + fundcode + " - " + name +
                             "\n单位净值: " + dwjz +
                             "\n净值估算: " + gsz +
                             "\n估算涨幅: " + gszzl +
                             "\n更新日期: " + gztime)
            gsz = float(gszzl)
            text_color = label.palette().windowText().color().name()
            # print(text_color)
            pix = QPixmap()
            if gsz < 0:  # and text_color != "#008000"
                # print("< update...")
                png_data = base64.b64decode(img_up)
                label.setStyleSheet('color: green')
                pix.loadFromData(png_data)
                labelimg.setPixmap(pix)
            if gsz >= 0:  # and text_color != "#ff0000"
                # print(">= update...")
                png_data = base64.b64decode(img_up)
                label.setStyleSheet('color: red')
                pix.loadFromData(png_data)
                labelimg.setPixmap(pix)
            labelimg.setStyleSheet("background: transparent;")
            num = num + 1

        for i in range(num, 3):
            label = self.findChild(QLabel, "label" + str(i + 1))
            labelimg = self.findChild(QLabel, "labelimg" + str(i + 1))
            png_data = base64.b64decode(img_pig)
            pix.loadFromData(png_data)
            labelimg.setPixmap(pix)
            label.setText("去设置添加基金....")
            label.setToolTip("")
            label.setStyleSheet('color: black')
            labelimg.setStyleSheet("background: transparent;")
        print("结束 更新基金信息")

    def display_hot(self, data):
        print("开始 更新微博热搜")
        num = 0
        jsonDatas = json.loads(data)
        if jsonDatas["status"] != "ok":
            return
        for jsonData in jsonDatas["data"]:
            label = self.findChild(QLabel, "label" + str(num + 1))
            labelimg = self.findChild(QLabel, "labelimg" + str(num + 1))

            label.setAlignment(Qt.AlignLeft)
            label.setOpenExternalLinks(True)
            show_text = "<a style='color: red; text-decoration: none' href='https://s.weibo.com/weibo?q=" + quote(jsonData["word_scheme"]) + "'>" + str(jsonData["realpos"]) + ". " + jsonData["word"]
            label.setText(show_text)
            label.setToolTip("")
            if "icon_desc" in jsonData and "icon_desc_color" in jsonData:
                labelimg.setText(jsonData["icon_desc"])
                labelimg.setToolTip(jsonData["icon_desc"])
                labelimg.setStyleSheet("background: " + jsonData["icon_desc_color"] + ";font-size: 11px;border-radius:3px;")
            else:
                labelimg.setText(" ")
                labelimg.setStyleSheet("background: transparent;font-size: 11px;border-radius:3px;")
            num = num + 1
        print("结束 更新微博热搜")

    def display_movie(self, data):
        print("开始 更新电影信息")
        num = 0
        jsonDatas = json.loads(data)
        if jsonDatas["status"] != "ok":
            return
        for jsonData in jsonDatas["data"]:
            label = self.findChild(QLabel, "label" + str(num + 1))
            labelimg = self.findChild(QLabel, "labelimg" + str(num + 1))

            label.setAlignment(Qt.AlignLeft)
            label.setOpenExternalLinks(True)
            show_text = "<a style='color: red; text-decoration: none' href='" + jsonData["videourl"] + "'>" + str(
                jsonData["sc"]) + " | " + jsonData["nm"]
            label.setText(show_text)

            tip_text = "片名:" + jsonData["nm"] + "\n" + \
                       "类型:" + jsonData["cat"] + "\n" + \
                       "" + jsonData["desc"] + "\n" + \
                       "导演:" + jsonData["dir"] + "\n" + \
                       "上映:" + jsonData["pubDesc"] + "\n" + \
                       "明星:" + jsonData["star"] + "\n" + \
                       "信息:" + jsonData["boxInfo"]
            label.setToolTip(tip_text)

            url = jsonData["img"]
            res = requests.get(url)
            img = QImage.fromData(res.content)
            labelimg.setPixmap(QPixmap.fromImage(img))
            # labelimg.setText(" ")
            # labelimg.setStyleSheet("background: transparent;font-size: 11px;border-radius:3px;")
            num = num + 1
        print("结束 更新电影信息")

    def display_weather(self):
        # http://www.nmc.cn/rest/position?_=1660633779937 获得地址
        # http://www.nmc.cn/rest/weather?stationid=58238&_=1660633779939 获得天气
        t = time.time()
        headers = {
            'Host': 'www.nmc.cn',
            'Referer': 'http://www.nmc.cn/publish/forecast/AJS/nanjing.html'
        }
        apiUrl = "http://www.nmc.cn/rest/position?_=" + str(int(t))
        code = ""
        try:
            retjson = requests.get(apiUrl, headers=headers).json()
            code = retjson["code"]
        except:
            print('获取位置异常....')

        headers = {
            'Host': 'www.nmc.cn',
            'Referer': 'http://www.nmc.cn/publish/forecast/AJS/nanjing.html'
        }
        apiUrl = "http://www.nmc.cn/rest/weather?stationid=" + code + "&_=" + str(int(t))
        try:
            retjson = requests.get(apiUrl, headers=headers).json()
            weatherjson = retjson["data"]["real"]["weather"]
            img = weatherjson["img"]
            img_url = "http://image.nmc.cn/assets/img/w/40x40/4/" + img + ".png"
            res = requests.get(img_url)
            img = QImage.fromData(res.content)
            labelimg = self.findChild(QLabel, "labelweather")
            tip_text = "天气: " + str(weatherjson["info"]) + "\n" + \
                       "温度: " + str(weatherjson["temperature"]) + "\n" + \
                       "湿度: " + str(weatherjson["humidity"]) + "\n" + \
                       "体感: " + str(weatherjson["feelst"])
            alert = str(retjson["data"]["real"]["warn"]["alert"])
            if "warn" in retjson["data"]["real"]:
                if "9999" != alert:
                    tip_text = tip_text + "\n" + "预警: " + alert
            tip_text = tip_text + "\n" + "更新时间: " + str(retjson["data"]["real"]["publish_time"])
            labelimg.setToolTip(tip_text)
            labelimg.setPixmap(QPixmap.fromImage(img))
        except:
            print('获取天气异常....')

        pass

    def handleDisplay(self, data):
        # 更新基金信息
        print("    ")
        print("更新时间 :" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        jsonDatas = json.loads(data)
        dispaly_type = jsonDatas["type"]
        if dispaly_type == 0:
            self.display_hot(data)
        elif dispaly_type == 1:
            self.display_fund(data)
        elif dispaly_type == 2:
            self.display_movie(data)

        if (self.refresh_count % 72) == 0:
            print("更新天气信息.....")
            self.display_weather()
            self.refresh_count = 0
        self.refresh_count = self.refresh_count + 1

        m_hTaskbar = win32gui.FindWindow("Shell_TrayWnd", None)
        m_hBar = win32gui.FindWindowEx(m_hTaskbar, 0, "ReBarWindow32", None)
        b = win32gui.GetWindowRect(m_hBar)
        if b[2] != self.tb_width and self.tb_width != 0:
            print("更新 组件位置")
            m_hMin = win32gui.FindWindowEx(m_hBar, 0, "MSTaskSwWClass", None)
            self.setGeometry(b[2] - b[0] - 300, 0, 300, b[3] - b[1])
            win32gui.MoveWindow(m_hMin, 0, 0, b[2] - b[0] - 300, b[3] - b[1], True)
            self.tb_width = b[2]
        if self.tb_width == 0:
            print("初始化组件宽度值")
            self.tb_width = b[2]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TaskWidget()
    ex.show()
    sys.exit(app.exec_())