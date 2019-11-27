#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2017年12月28日
@author: Irony."[讽刺]
@site: https://pyqt5.com , https://github.com/892768447
@email: 892768447@qq.com
@file: charts.line.LineStack
@description: like http://echarts.baidu.com/demo.html#line-stack
"""
import re
import sys

from PyQt5.QtChart import QChart, QChartView, QLegend, QLineSeries, QSplineSeries, QValueAxis
from PyQt5.QtCore import QPoint, QPointF, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QApplication, QGraphicsLineItem, QWidget, \
    QHBoxLayout, QLabel, QVBoxLayout, QGraphicsProxyWidget


class ToolTipItem(QWidget):

    def __init__(self, color, text, parent=None):
        super(ToolTipItem, self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        clabel = QLabel(self)
        clabel.setMinimumSize(12, 12)
        clabel.setMaximumSize(12, 12)
        clabel.setStyleSheet("border-radius:6px;background: rgba(%s,%s,%s,%s);" % (
            color.red(), color.green(), color.blue(), color.alpha()))
        layout.addWidget(clabel)
        self.textLabel = QLabel(text, self, styleSheet="color:white;")
        layout.addWidget(self.textLabel)

    def setText(self, text):
        self.textLabel.setText(text)


class ToolTipWidget(QWidget):
    Cache = {}

    def __init__(self, *args, **kwargs):
        super(ToolTipWidget, self).__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "ToolTipWidget{background: rgba(50, 50, 50, 100);}")
        layout = QVBoxLayout(self)
        self.titleLabel = QLabel(self, styleSheet="color:white;")
        layout.addWidget(self.titleLabel)

    def updateUi(self, title, points):
        self.titleLabel.setText(title)
        for serie, point in points:
            if serie not in self.Cache:
                item = ToolTipItem(
                    serie.color(),
                    (serie.name() or "-") + ":" + str(point.y()), self)
                self.layout().addWidget(item)
                self.Cache[serie] = item
            else:
                self.Cache[serie].setText(
                    (serie.name() or "-") + ":" + str(point.y()))
            self.Cache[serie].setVisible(serie.isVisible())  # 隐藏那些不可用的项
        self.adjustSize()  # 调整大小


class GraphicsProxyWidget(QGraphicsProxyWidget):

    def __init__(self, *args, **kwargs):
        super(GraphicsProxyWidget, self).__init__(*args, **kwargs)
        self.setZValue(999)
        self.tipWidget = ToolTipWidget()
        self.setWidget(self.tipWidget)
        self.hide()

    def width(self):
        return self.size().width()

    def height(self):
        return self.size().height()

    def show(self, title, points, pos):
        self.setGeometry(QRectF(pos, self.size()))
        self.tipWidget.updateUi(title, points)
        super(GraphicsProxyWidget, self).show()


class ChartView(QChartView):

    def __init__(self, *args, **kwargs):
        super(ChartView, self).__init__(*args, **kwargs)
        # self.resize(800, 600)
        self.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        self.initChart()

        # 提示widget
        self.toolTipWidget = GraphicsProxyWidget(self._chart)

        # line
        self.lineItem = QGraphicsLineItem(self._chart)
        pen = QPen(Qt.gray)
        pen.setWidth(1)
        self.lineItem.setPen(pen)
        self.lineItem.setZValue(998)
        self.lineItem.hide()

        # 一些固定计算，减少mouseMoveEvent中的计算量
        # 获取x和y轴的最小最大值
        axisX, axisY = self._chart.axisX(), self._chart.axisY()
        self.min_x, self.max_x = axisX.min(), axisX.max()
        self.min_y, self.max_y = axisY.min(), axisY.max()

        self.axisX_data = 0
        self.axisY_data = 0
        self.data_max = float("-inf")
        self.data_min = float("inf")
        self.data_save = []  # 很蠢的方法，待会优化

    def resizeEvent(self, event):
        super(ChartView, self).resizeEvent(event)
        # 当窗口大小改变时需要重新计算
        # 坐标系中左上角顶点
        self.point_top = self._chart.mapToPosition(
            QPointF(self.min_x, self.max_y))
        # 坐标原点坐标
        self.point_bottom = self._chart.mapToPosition(
            QPointF(self.min_x, self.min_y))
        self.step_x = (self.max_x - self.min_x) / \
                      (self._chart.axisX().tickCount() - 1)

    def mouseMoveEvent(self, event):
        super(ChartView, self).mouseMoveEvent(event)
        pos = event.pos()
        # 把鼠标位置所在点转换为对应的xy值
        x = self._chart.mapToValue(pos).x()
        y = self._chart.mapToValue(pos).y()
        index = round((x - self.min_x) / self.step_x)
        # 得到在坐标系中的所有正常显示的series的类型和点
        points = [(serie, serie.at(index))
                  for serie in self._chart.series()
                  if self.min_x <= x <= self.max_x and
                  self.min_y <= y <= self.max_y]
        if points:
            pos_x = self._chart.mapToPosition(
                QPointF(index * self.step_x + self.min_x, self.min_y))
            self.lineItem.setLine(pos_x.x(), self.point_top.y(),
                                  pos_x.x(), self.point_bottom.y())
            self.lineItem.show()
            title = ""
            t_width = self.toolTipWidget.width()
            t_height = self.toolTipWidget.height()
            # 如果鼠标位置离右侧的距离小于tip宽度
            x = pos.x() - t_width if self.width() - \
                                     pos.x() - 20 < t_width else pos.x()
            # 如果鼠标位置离底部的高度小于tip高度
            y = pos.y() - t_height if self.height() - \
                                      pos.y() - 20 < t_height else pos.y()
            self.toolTipWidget.show(
                title, points, QPoint(x, y))
        else:
            self.toolTipWidget.hide()
            self.lineItem.hide()

    def handleMarkerClicked(self):
        marker = self.sender()  # 信号发送者
        if not marker:
            return
        visible = not marker.series().isVisible()
        #         # 隐藏或显示series
        marker.series().setVisible(visible)
        marker.setVisible(True)  # 要保证marker一直显示
        # 透明度
        alpha = 1.0 if visible else 0.4
        # 设置label的透明度
        brush = marker.labelBrush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setLabelBrush(brush)
        # 设置marker的透明度
        brush = marker.brush()
        color = brush.color()
        color.setAlphaF(alpha)
        brush.setColor(color)
        marker.setBrush(brush)
        # 设置画笔透明度
        pen = marker.pen()
        color = pen.color()
        color.setAlphaF(alpha)
        pen.setColor(color)
        marker.setPen(pen)

    def handleMarkerHovered(self, status):
        # 设置series的画笔宽度
        marker = self.sender()  # 信号发送者
        if not marker:
            return
        series = marker.series()
        if not series:
            return
        pen = series.pen()
        if not pen:
            return
        pen.setWidth(pen.width() + (1 if status else -1))
        series.setPen(pen)

    def handleSeriesHoverd(self, point, state):
        # 设置series的画笔宽度
        series = self.sender()  # 信号发送者
        pen = series.pen()
        if not pen:
            return
        pen.setWidth(pen.width() + (1 if state else -1))
        series.setPen(pen)

    def initChart(self):
        self._chart = QChart()  # QChart(title="折线图堆叠")
        self._chart.setAcceptHoverEvents(True)
        # Series动画
        self._chart.setAnimationOptions(QChart.SeriesAnimations)
        # dataTable = ["CH1", "CH2", "CH3", "CH4", "CH5"]  # 暂时不会五个
        dataTable = ["CH1"]
        for series_name in dataTable:
            series = QLineSeries(self._chart)  # QLineSeries QSplineSeries
            # for j, v in enumerate(data_list):#enumerate() 函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据和数据下标
            #     series.append(j, v)
            series.setName(series_name)
            # series.setPointsVisible(True)  # 显示圆点
            series.hovered.connect(self.handleSeriesHoverd)  # 鼠标悬停
            self._chart.addSeries(series)
        self._chart.createDefaultAxes()  # 创建默认的轴
        # self._chart.series.setUseOpenGL(True)  # 开启OpenGL
        axisX = self._chart.axisX()  # x轴
        axisX.setTickCount(1000)  # x轴设置7个刻度
        axisX.setGridLineVisible(False)  # 隐藏从x轴往上的线条
        axisX.setRange(0, 1000)  # 设置y轴范围
        axisY = self._chart.axisY()
        axisY.setTickCount(7)  # y轴设置7个刻度
        axisY.setRange(0, 5000)  # 设置y轴范围
        # chart的图例
        legend = self._chart.legend()
        # 设置图例由Series来决定样式
        legend.setMarkerShape(QLegend.MarkerShapeFromSeries)
        # 遍历图例上的标记并绑定信号
        for marker in legend.markers():
            # 点击事件
            marker.clicked.connect(self.handleMarkerClicked)
            # 鼠标悬停事件
            marker.hovered.connect(self.handleMarkerHovered)
        self.setChart(self._chart)

    def get_plot_data(self, data):
        # (?<=...)  如果...出现在字符串前面才做匹配
        # \d 匹配任何十进制数字，和[0-9]相同（\D与\d相反，不匹配任何非数值型的数字）
        # + 匹配1次或多次前面出现的正则表达式
        # \d+匹配1次或者多次数字
        # \.?这个是匹配小数点的，可能有，也可能没有
        # \d * 这个是匹配小数点之后的数字的
        ch_data = re.compile(r'(?<=CH1:)\d+\.?\d*')
        ch_data = ch_data.findall(data)
        for ser in self._chart.series():
            if ch_data:
                float_data = list(map(float, ch_data))  # 一开始缓冲中有多余的数据
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
                print('X is ' + str(self.axisX_data) + ' Y is ' + str(self.axisY_data))
                ser.append(self.axisX_data, self.axisY_data)
                if ser.count() > 1500:
                    ser.removePoints(0, ser.count() - 1500)
                # axisX = self._chart.axisX()
                # axisX.setRange(max(0, self.axisX_data - 1000), self.axisX_data)
            # axisY = self._chart.axisY()
            # axisY.setRange(self.data_min - 50, self.data_max + 50)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = ChartView()
    view.show()
    sys.exit(app.exec_())
