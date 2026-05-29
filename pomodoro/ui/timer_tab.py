# -*- coding: utf-8 -*-
"""计时页签"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

from pomodoro import models


class TimerTab(QWidget):
    """番茄计时显示与控制"""

    def __init__(self, window):
        super().__init__()
        self._window = window  # MainWindow 引用
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 模式标签
        self.mode_label = QLabel("工作中")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.mode_label)
        layout.addSpacing(20)

        # 时间显示
        self.time_label = QLabel("05:05")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace; "
            "font-size: 80px; font-weight: bold;"
        )
        layout.addWidget(self.time_label)
        layout.addSpacing(10)

        # 当前任务
        self.current_task_label = QLabel("当前任务: 无")
        self.current_task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_task_label.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(self.current_task_label)

        # 番茄计数
        self.pomodoro_count_label = QLabel("本次会话已完成: 0 个番茄")
        self.pomodoro_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pomodoro_count_label.setStyleSheet("font-size: 10px; color: #888;")
        layout.addWidget(self.pomodoro_count_label)
        layout.addSpacing(30)

        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton("开始")
        self.start_btn.setFixedWidth(100)
        self.start_btn.clicked.connect(self._window.toggle_timer)
        btn_layout.addWidget(self.start_btn)

        self.skip_btn = QPushButton("跳过")
        self.skip_btn.setFixedWidth(100)
        self.skip_btn.clicked.connect(self._window.skip_phase)
        btn_layout.addWidget(self.skip_btn)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.setFixedWidth(100)
        self.reset_btn.clicked.connect(self._window.reset_timer)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(btn_layout)

    def refresh(self, window):
        """根据 MainWindow 状态更新显示"""
        m = window.remaining // 60
        s = window.remaining % 60
        color = models.MODE_COLORS[window.mode]
        self.time_label.setText(f"{m:02d}:{s:02d}")
        self.time_label.setStyleSheet(
            "font-family: 'Consolas', 'Courier New', monospace; "
            f"font-size: 80px; font-weight: bold; color: {color};"
        )
        self.mode_label.setText(models.MODE_LABELS[window.mode])
        self.mode_label.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {color};"
        )
        self.pomodoro_count_label.setText(
            f"本次会话已完成: {window.session_completed} 个番茄"
        )

        if window.current_task_id is not None:
            task = next(
                (t for t in window.data["tasks"] if t["id"] == window.current_task_id),
                None,
            )
            if task:
                self.current_task_label.setText(f"当前任务: {task['title']}")
                return
        self.current_task_label.setText("当前任务: 无")

    def update_buttons(self, running):
        self.start_btn.setText("暂停" if running else "继续")
