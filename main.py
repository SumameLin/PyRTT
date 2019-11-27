import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtChart import QChart, QChartView, QLegend
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QPainter
from PyQt5.QtWidgets import qApp, QGridLayout
import pylink
import time
import _thread as thread

from MainWindow import Ui_MainWindow
from ConfigWindow import Ui_Dialog
from src.ChartPlot import ChartPlot
from src.LineStack import ChartView


class RttTool(QtWidgets.QMainWindow, Ui_MainWindow):
    send_rtt_data = pyqtSignal(str)
    send_print_data = pyqtSignal(str)
    send_plot_data = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RttTool, self).__init__(parent=parent)
        self.configWindow = Config()
        self.jlink = pylink.JLink()
        self.setupUi(self)
        self.setWindowTitle('PyRTT')
        self.setWindowIcon(QIcon('./ico/them.ico'))
        self.actionlianjie.setIcon(QIcon('./ico/open.png'))
        self.actionlianjie.setShortcut('F5')
        self.actionduankai.setIcon(QIcon('./ico/close.png'))
        self.actionduankai.setShortcut('F6')
        self.actionduankai.setEnabled(False)
        self.actiontuichu.setIcon(QIcon('./ico/exit.png'))
        self.actiontuichu.setShortcut('Alt+F4')  # 快捷键
        self.actionqingchu.setIcon(QIcon('./ico/clean.png'))
        self.actionqingchu.setShortcut('F7')
        self.actionshowLog.setIcon(QIcon('./ico/AJ.png'))
        self.actionshowLog.setShortcut('Alt+l')
        self.textLog.setMaximumSize(QtCore.QSize(16777215, 16777215))  # 设置TextBrowser缓存大小
        self.textTerminal.setMaximumSize(QtCore.QSize(16777215, 16777215))
        # 变量
        self.show_log_flag = 0
        self.term_data = []

        self.init()
        chartWindow = ChartPlot()
        chartWindow.legend().hide()  # 隐藏legend
        # NoAnimation
        # AllAnimations
        # SeriesAnimations 在缩放窗口大小时可以用动画进行美化
        chartWindow.setAnimationOptions(QChart.NoAnimation)
        self.widget.setChart(chartWindow)
        self.widget.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        # self.widget.setRubberBand(QChartView.RectangleRubberBand)  # axisY.setRange 不能固定
        chartWindow.send_labCH1.connect(lambda p: self.labCH1.setText(p))
        self.send_rtt_data.connect(lambda p: chartWindow.get_term_data(p))
        # 显示LineStack
        chart_view = ChartView()
        baseLayout = QGridLayout()
        baseLayout.addWidget(chart_view)
        self.widget_plot.setLayout(baseLayout)
        self.send_plot_data.connect(lambda p: chart_view.get_plot_data(p))
        # 信号与槽初始化

    def init(self):
        # 清除发送
        self.btnClean.clicked.connect(self.data_send_clean)
        # 退出
        self.actiontuichu.triggered.connect(qApp.quit)
        self.actionlianjie.triggered.connect(self.configWindowShow)
        # 连接
        self.configWindow.start_connect.connect(lambda decice, speed: self.rtt_connect(decice, speed))
        # 断开
        self.actionduankai.triggered.connect(self.rtt_disconnect)
        # 清除 terminal窗口数据
        self.actionqingchu.triggered.connect(self.terminal_clean)
        # 不显示Log 窗口
        self.actionshowLog.triggered.connect(self.hide_logWindow)
        # 发送RTT数据
        self.send_print_data.connect(lambda p: self.print_data(p))

    # 发送框清除
    def data_send_clean(self):
        self.textSend.setText('')

    # 清除terminal窗口数据
    def terminal_clean(self):
        self.textTerminal.setText('')

    # 连接窗口显示
    def configWindowShow(self):
        self.configWindow.show()

    # 隐藏Log TabWidget
    def hide_logWindow(self):
        if self.show_log_flag == 0:
            # 显示隐藏某一个Tab不会 removeTab 删除就要添加一模一样的
            # self.tabWidget.removeTab(0)
            # https://stackoverflow.com/questions/34377663/how-to-hide-a-tab-in-qtabwidget-and-show-it-when-a-button-is-pressed
            self.actionshowLog.setIcon(QIcon(''))
            self.show_log_flag = 1
        else:
            self.actionshowLog.setIcon(QIcon('ico/AJ.png'))
            self.show_log_flag = 0

    # 打印Log 到TextBrowser
    def print_log(self, text):
        # 获取textLog 光标
        text_cursor = self.textLog.textCursor()
        if text_cursor != text_cursor.End:
            # 滚动到底部
            text_cursor.movePosition(text_cursor.End)
            # 设置光标到text中
            self.textLog.setTextCursor(text_cursor)
        self.textLog.setTextColor(QColor(100, 184, 255))
        self.textLog.setFontPointSize(12)
        self.textLog.insertPlainText(text)  # append（）函数进行字符串显示，容易造成显示分段错误
        text_cursor = self.textLog.textCursor()
        text_cursor.movePosition(text_cursor.End)
        self.textLog.setTextCursor(text_cursor)

    # 打印数据到TextBrowser
    def print_data(self, data):
        # 先把光标移到最后
        # 获取textLog 光标
        text_cursor = self.textTerminal.textCursor()
        if text_cursor != text_cursor.End:  # 一定要先寻找光标在显示 要不然先显示 在移动光标会导致Textbrowers里面内容正确
            # 滚动到底部
            text_cursor.movePosition(text_cursor.End)
            # 设置光标到text中
            self.textTerminal.setTextCursor(text_cursor)
        # 显示内容
        self.textTerminal.insertPlainText(data)
        # 最后再将光标移到最后
        text_cursor = self.textTerminal.textCursor()
        text_cursor.movePosition(text_cursor.End)
        self.textTerminal.setTextCursor(text_cursor)

    # 读取rtt数据缓冲
    def read_rtt(self):
        while True:
            try:
                num_up = self.jlink.rtt_get_num_up_buffers()
                num_down = self.jlink.rtt_get_num_down_buffers()
                self.print_log('RTT started, %d up bufs, %d down bufs...\r\n' % (num_up, num_down))
                break
            except pylink.errors.JLinkRTTException:
                time.sleep(0.1)
        try:
            while self.jlink.connected():
                self.actionlianjie.setEnabled(False)
                self.actionduankai.setEnabled(True)
                # 读取通道0的缓冲数据 RTT supports multiple channels in both directions
                terminal_bytes = self.jlink.rtt_read(0, 1024)  # terminal_bytes <class 'list'>
                if terminal_bytes:  # terminal_bytes 里面是ASCII 用的是 SEGGER_RTT_printf
                    self.term_data = "".join(map(chr, terminal_bytes))  # str
                    # self.print_data(self.term_data)
                    self.send_print_data.emit(self.term_data)
                    self.send_rtt_data.emit(self.term_data)
                    # self.send_plot_data.emit(self.term_data)  # 太卡了 且不能跟随移动 数据处理应该单独
                #     sys.stdout.write("".join(map(chr, terminal_bytes)))
                #     sys.stdout.flush()
                # time.sleep(0.01)  # S 单位
            else:
                self.print_log('J-Link is disconnected...\r\n')
                self.actionlianjie.setEnabled(True)
                self.actionduankai.setEnabled(False)
                thread.exit()
                self.proce_read.terminate()
        except Exception:
            self.print_log('IO read thread exception, exiting...\r\n')
            thread.interrupt_main()
            raise

    # 连接Segger RTT
    def rtt_connect(self, target_device, target_speed):
        # self.jlink.set_max_speed(target_speed)
        self.print_log('connecting to JLink...\r\n')
        self.print_log('connecting to %s...\r\n' % target_device)
        self.jlink.open()
        self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        try:
            self.jlink.connect(target_device)
            self.print_log('connected, starting RTT...\r\n')
            self.jlink.rtt_start()
            # 开启读取RTT线程
            thread.start_new_thread(self.read_rtt, ())
        except:
            self.print_log('target_device is not true or disconnect...\r\n')
            pass

    # 断开Segger RTT
    def rtt_disconnect(self):
        self.print_log('J-Link close...\r\n')
        self.jlink.close()
        self.actionlianjie.setEnabled(True)
        self.actionduankai.setEnabled(False)


class Config(QtWidgets.QDialog, Ui_Dialog):
    start_connect = pyqtSignal([str, str])  # 芯片系列 SWD速度

    def __init__(self, parent=None):
        super(Config, self).__init__(parent=parent)
        self.setupUi(self)
        self.setFixedSize(402, 168)  # 固定窗口大小
        self.setWindowTitle('Config')
        self.setWindowIcon(QIcon('ico/config.png'))
        self.groupBox.setTitle('目标芯片 & 速度')
        self.cmbSpeed.setCurrentText('40000KHz')
        self.init()

    # 信号与槽初始化
    def init(self):
        self.btnCancel.clicked.connect(self.hide)
        self.btnOK.clicked.connect(self.send_connect_data)

    # 发送系列和数据
    def send_connect_data(self):
        print('Target : ' + self.cmbTarget.currentText() + ' Speed : '
              + self.cmbSpeed.currentText())
        self.start_connect[str, str].emit(self.cmbTarget.currentText(), self.cmbSpeed.currentText())
        self.hide()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = RttTool()
    mainWindow.show()
    sys.exit(app.exec_())
