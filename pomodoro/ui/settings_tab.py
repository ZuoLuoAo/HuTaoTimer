# -*- coding: utf-8 -*-
"""设置页签"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QMessageBox,
)
from PyQt6.QtCore import Qt

from pomodoro import models


class SettingsTab(QWidget):
    """工作时长与休息时长设置"""

    def __init__(self, window):
        super().__init__()
        self._window = window
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(30, 30, 30, 30)

        # 工作时长 (分钟)
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("工作时长 (分钟):"))
        self.work_min_spin = QSpinBox()
        self.work_min_spin.setRange(0, 120)
        self.work_min_spin.setValue(self._window.settings["work_minutes"])
        self.work_min_spin.setFixedWidth(80)
        row1.addWidget(self.work_min_spin)
        row1.addStretch()
        layout.addLayout(row1)
        layout.addSpacing(10)

        # 工作时长 (秒)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("工作时长 (秒):"))
        self.work_sec_spin = QSpinBox()
        self.work_sec_spin.setRange(0, 59)
        self.work_sec_spin.setValue(self._window.settings.get("work_seconds", 0))
        self.work_sec_spin.setFixedWidth(80)
        row2.addWidget(self.work_sec_spin)
        row2.addStretch()
        layout.addLayout(row2)
        layout.addSpacing(10)

        # 休息时长 (分钟)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("休息时长 (分钟):"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 120)
        self.break_spin.setValue(self._window.settings["break_minutes"])
        self.break_spin.setFixedWidth(80)
        row3.addWidget(self.break_spin)
        row3.addStretch()
        layout.addLayout(row3)
        layout.addSpacing(20)

        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(self._save)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addSpacing(20)

        # 数据路径
        path_label = QLabel(f"数据存储位置:\n{models.DATA_FILE}")
        path_label.setStyleSheet("font-size: 9px; color: #888;")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)

        layout.addStretch()

    def refresh(self):
        self.work_min_spin.setValue(self._window.settings["work_minutes"])
        self.work_sec_spin.setValue(self._window.settings.get("work_seconds", 0))
        self.break_spin.setValue(self._window.settings["break_minutes"])

    def _save(self):
        work_min = self.work_min_spin.value()
        work_sec = self.work_sec_spin.value()
        break_min = self.break_spin.value()

        if work_min == 0 and work_sec == 0:
            work_sec = 1
            self.work_sec_spin.setValue(1)

        self._window.save_settings(work_min, work_sec, break_min)
        QMessageBox.information(self, "提示", "设置已保存")
