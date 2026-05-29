# -*- coding: utf-8 -*-
"""完成提醒弹窗"""
import sys

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer, Qt

if sys.platform == "win32":
    try:
        import winsound
    except ImportError:
        winsound = None
else:
    winsound = None


class AlertDialog(QDialog):
    """非模态提醒弹窗 — 循环播放提示音直到用户确认"""

    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("胡桃钟")
        self.setFixedSize(320, 140)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )

        # 提示音定时器
        self._sound_timer = QTimer(self)
        self._sound_timer.setInterval(1200)
        self._sound_timer.timeout.connect(self._play_sound)

        layout = QVBoxLayout(self)

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 11px;")
        layout.addWidget(label, stretch=1)

        btn = QPushButton("继续")
        btn.setFixedWidth(100)
        btn.clicked.connect(self._on_acknowledge)
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        layout.addSpacing(10)

        # 开始播放
        self._sound_timer.start()

    def _play_sound(self):
        if winsound is not None:
            try:
                winsound.PlaySound(
                    "SystemExclamation",
                    winsound.SND_ALIAS | winsound.SND_ASYNC,
                )
            except Exception:
                pass

    def stop_sound(self):
        self._sound_timer.stop()
        if winsound is not None:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def _on_acknowledge(self):
        parent = self.parentWidget()
        if parent and hasattr(parent, "_acknowledge_alert"):
            parent._acknowledge_alert()
