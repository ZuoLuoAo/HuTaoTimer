# -*- coding: utf-8 -*-
"""统计页签"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen

from pomodoro import models


class ChartWidget(QWidget):
    """手绘柱状图控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(480, 240)
        self.setStyleSheet("background: white; border: 1px solid #ddd;")
        self._counts = []
        self._days = []

    def set_data(self, days, counts):
        self._days = days
        self._counts = counts
        self.update()

    def paintEvent(self, event):
        if not self._days:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_left = 35
        pad_bottom = 35
        pad_top = 20
        chart_w = w - pad_left - 15
        chart_h = h - pad_top - pad_bottom

        max_count = max(self._counts) if max(self._counts) > 0 else 1
        gap = chart_w / 7
        bar_w = gap * 0.55
        baseline_y = pad_top + chart_h

        today = self._days[-1] if self._days else None

        # 基线
        painter.setPen(QPen(QColor("#999"), 1))
        painter.drawLine(
            int(pad_left), int(baseline_y),
            int(pad_left + chart_w), int(baseline_y),
        )

        for i, (d, c) in enumerate(zip(self._days, self._counts)):
            x = pad_left + gap * i + (gap - bar_w) / 2
            bar_h_px = (c / max_count) * chart_h if max_count else 0
            y = baseline_y - bar_h_px

            color = QColor("#e74c3c") if d == today else QColor("#3498db")
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(x, y, bar_w, bar_h_px))

            if c > 0:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                painter.drawText(
                    QRectF(x, y - 18, bar_w, 16),
                    Qt.AlignmentFlag.AlignCenter, str(c),
                )

            painter.setPen(QColor("#666"))
            painter.setFont(QFont("Arial", 9))
            painter.drawText(
                QRectF(x, baseline_y + 4, bar_w, 14),
                Qt.AlignmentFlag.AlignCenter,
                f"{d.month}/{d.day}",
            )

        painter.end()


class StatsTab(QWidget):
    """番茄统计与图表"""

    def __init__(self, window):
        super().__init__()
        self._window = window
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # 统计数值行
        info_layout = QHBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.today_label = QLabel("今日\n0")
        self.today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_label.setStyleSheet(
            "font-size: 14px; color: #e74c3c; font-weight: bold;"
        )
        info_layout.addWidget(self.today_label)
        info_layout.addSpacing(50)

        self.week_label = QLabel("本周\n0")
        self.week_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.week_label.setStyleSheet(
            "font-size: 14px; color: #2980b9; font-weight: bold;"
        )
        info_layout.addWidget(self.week_label)
        info_layout.addSpacing(50)

        self.total_label = QLabel("累计\n0")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label.setStyleSheet(
            "font-size: 14px; color: #27ae60; font-weight: bold;"
        )
        info_layout.addWidget(self.total_label)

        layout.addLayout(info_layout)
        layout.addSpacing(15)

        # 图表标题
        title = QLabel("近 7 天番茄数")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(title)

        # 柱状图
        self.chart = ChartWidget()
        layout.addWidget(self.chart, stretch=1)

        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.refresh)
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)

    def refresh(self):
        history = self._window.data.get("history", {})

        today_count = models.get_today_count(history)
        week_count = models.get_week_count(history)
        total_count = models.get_total_count(history)

        self.today_label.setText(f"今日\n{today_count}")
        self.week_label.setText(f"本周\n{week_count}")
        self.total_label.setText(f"累计\n{total_count}")

        data = models.get_last_7_days(history)
        days = [d for d, _ in data]
        counts = [c for _, c in data]
        self.chart.set_data(days, counts)
