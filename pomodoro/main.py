# -*- coding: utf-8 -*-
"""胡桃钟 PyQt6 入口 — 请使用 run.bat 启动以避免 Anaconda DLL 冲突"""
import ctypes
import os
import sys

# 设置任务栏图标 ID（必须在 QApplication 创建前）
if sys.platform == "win32":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("hutaozhong.pomodoro.app")
    except Exception:
        pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from pomodoro.models import RESOURCE_DIR
from pomodoro.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("胡桃钟")
    app.setOrganizationName("HuTaoZhong")

    # 应用图标
    icon_path = RESOURCE_DIR / "assets" / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 胡桃主题样式表
    qss_path = RESOURCE_DIR / "pomodoro" / "resources" / "style.qss"
    if qss_path.exists():
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
