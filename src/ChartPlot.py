import random
import re
from PyQt5.QtChart import QChart, QSplineSeries, QValueAxis
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen, QColor

"""
画图会有延时，都缓存在 self.data_save 中,取data_save中最后一个保持实时性
"""


class ChartPlot(QChart):
    send_labCH1 = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.axisX_data = 0
        self.axisY_data = 0
        self.data_max = float("-inf")
        self.data_min = float("inf")
        self.data_save = []
        self.data_term = ''
        self.show_flag = 1
        # 初始化图像
        self.series = QSplineSeries(self)
        self.series.setName('CH1')  # chart.setAcceptHoverEvents(True)
        colour = [random.randrange(0, 255),
                  random.randrange(0, 255),
                  random.randrange(0, 255)]
        series_pen = QPen(QColor(colour[0],
                                 colour[1],
                                 colour[2])
                          )
        series_pen.setWidth(2)  # 线宽
        self.series.setPen(series_pen)
        self.axisX = QValueAxis()  # QCategoryAxis ?
        self.axisX.setRange(0, 100)  # 1000
        self.axisX.setTickCount(10)  # 设置多少格 主要刻度
        # self.axisX.setMinorTickCount(3)  # 设置每格小刻度线的数目
        # 设置了小刻度 网格false 也是可见的
        self.axisX.setGridLineVisible(False)  # 网格不可见
        self.axisY = QValueAxis()
        self.axisY.setRange(0, 100)  # 5000
        self.axisY.setTickCount(10)  # 设置多少格
        # self.axisY.setMinorTickCount(3)  # 设置每格小刻度线的数目
        self.axisY.setGridLineVisible(False)
        self.series.append(self.axisX_data, self.axisY_data)
        self.addSeries(self.series)  # 添加到坐标轴中
        self.addAxis(self.axisX, Qt.AlignBottom)  # 底部
        self.addAxis(self.axisY, Qt.AlignLeft)
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)
        self.series.setUseOpenGL(True)  # 开启OpenGL

    def show_plot(self):
        if self.show_flag == 0:
            self.series.setVisible(True)
            self.show_flag = 1
        elif self.show_flag == 1:
            self.series.setVisible(False)
            self.show_flag = 0

    def get_term_data(self, data):
        self.data_term = data
        # (?<=...)  如果...出现在字符串前面才做匹配
        # \d 匹配任何十进制数字，和[0-9]相同（\D与\d相反，不匹配任何非数值型的数字）
        # + 匹配1次或多次前面出现的正则表达式
        # \d+匹配1次或者多次数字
        # \.?这个是匹配小数点的，可能有，也可能没有
        # \d* 这个是匹配小数点之后的数字的
        pattern = re.compile(r'(?<=CH1:)\d+\.?\d*')
        float_data = pattern.findall(self.data_term)
        if float_data:
            float_data = list(map(float, float_data))  # 一开始缓冲中有多余的数据
            # print('接收数据' + str(float_data))
            for plot_data in float_data:
                self.data_save.append(plot_data)
                if plot_data >= self.data_max:
                    self.data_max = plot_data
                    # print('data_max '+str(self.data_max))
                if plot_data <= self.data_min:
                    self.data_min = plot_data
                    # print('data_min '+str(self.data_min))
            self.axisX_data += 1
            self.axisY_data = self.data_save[-1]  # 前面缓存较多 取最后一个保证实时性
            # print(self.data_save)     # 第一个 数据 确实不正确
            # print('X is ' + str(self.axisX_data) + ' Y is ' + str(self.axisY_data))
            self.series.append(self.axisX_data, self.axisY_data)
            # self.series.setName(str(int(self.axisY_data)))
            self.send_labCH1.emit(str(int(self.axisY_data)))
            # self.scroll(8, 0)
            self.axisX.setRange(max(0, self.axisX_data - 1000), self.axisX_data)
            self.axisY.setRange(self.data_min - 50, self.data_max + 50)
            if self.series.count() > 1500:
                self.series.removePoints(0, self.series.count() - 1500)