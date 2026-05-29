# -*- coding: utf-8 -*-
"""主窗口 — QMainWindow + 全局状态管理"""
from datetime import datetime, date

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QMessageBox,
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon

from pomodoro import models
from pomodoro.ui.timer_tab import TimerTab
from pomodoro.ui.task_tab import TaskTab
from pomodoro.ui.stats_tab import StatsTab
from pomodoro.ui.settings_tab import SettingsTab
from pomodoro.ui.alert_dialog import AlertDialog


class MainWindow(QMainWindow):
    """胡桃钟主窗口，管理全局状态并协调四个页签"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("胡桃钟")
        self.resize(540, 640)
        self.setMinimumSize(500, 600)

        # 窗口图标
        icon_path = models.RESOURCE_DIR / "assets" / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # ---------- 数据 ----------
        self.data = models.load_data()
        self.settings = self.data["settings"]

        # ---------- 计时状态 ----------
        self.mode = models.MODE_WORK
        self.remaining = models.work_duration(self.settings)
        self.running = False
        self.session_completed = 0
        self.current_task_id = None

        # ---------- 提醒状态 ----------
        self._alert_active = False
        self._auto_start_after_ack = False

        # ---------- 定时器 ----------
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        # ---------- 构建 UI ----------
        self._build_ui()
        self._refresh_all()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.timer_tab = TimerTab(self)
        self.task_tab = TaskTab(self)
        self.stats_tab = StatsTab(self)
        self.settings_tab = SettingsTab(self)

        self.tabs.addTab(self.timer_tab, "计时")
        self.tabs.addTab(self.task_tab, "任务")
        self.tabs.addTab(self.stats_tab, "统计")
        self.tabs.addTab(self.settings_tab, "设置")

        # 页签切换时刷新统计和设置
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, index):
        if index == 2:
            self.stats_tab.refresh()
        elif index == 3:
            self.settings_tab.refresh()

    # ==================== 计时逻辑 ====================

    def toggle_timer(self):
        """开始 / 暂停 / 确认提醒"""
        if self._alert_active:
            self._acknowledge_alert()
            return
        if self.running:
            self._pause()
        else:
            self._start()

    def _start(self):
        self.running = True
        self._timer.start()
        self.timer_tab.update_buttons(running=True)

    def _pause(self):
        self.running = False
        self._timer.stop()
        self.timer_tab.update_buttons(running=False)

    def _tick(self):
        if self.remaining <= 0:
            self._on_phase_complete()
            return
        self.remaining -= 1
        self.timer_tab.refresh(self)

    def skip_phase(self):
        if self._alert_active:
            self._acknowledge_alert()
            return
        if not self._confirm("跳过", "确定要跳过当前阶段吗？"):
            return
        self._timer.stop()
        self.running = False
        self.remaining = 0
        self._on_phase_complete()

    def reset_timer(self):
        if self._alert_active:
            self._acknowledge_alert()
            return
        if not self._confirm("重置", "确定要重置当前计时器吗？"):
            return
        self._timer.stop()
        self.running = False
        self._switch_mode(models.MODE_WORK)
        self.timer_tab.update_buttons(running=False)
        self.timer_tab.refresh(self)

    def _switch_mode(self, mode):
        self.mode = mode
        if mode == models.MODE_WORK:
            self.remaining = models.work_duration(self.settings)
        else:
            self.remaining = models.break_duration(self.settings)

    def _on_phase_complete(self):
        self.running = False
        self._timer.stop()

        finished_work = self.mode == models.MODE_WORK
        if finished_work:
            self._record_pomodoro()
            self.session_completed += 1
            self._switch_mode(models.MODE_BREAK)
            msg = "工作完成！点击继续开始休息倒计时。"
        else:
            self._switch_mode(models.MODE_WORK)
            msg = "休息结束，点击继续开始新的工作。"

        self.timer_tab.update_buttons(running=False)
        self.task_tab.refresh()
        self.stats_tab.refresh()
        self.timer_tab.refresh(self)

        self._auto_start_after_ack = finished_work
        self._alert_active = True
        self._alert = AlertDialog(msg, self)
        self._alert.show()

    def _record_pomodoro(self):
        today = date.today().isoformat()
        record = {
            "task_id": self.current_task_id,
            "completed_at": datetime.now().isoformat(),
        }
        self.data["history"].setdefault(today, []).append(record)
        if self.current_task_id is not None:
            for t in self.data["tasks"]:
                if t["id"] == self.current_task_id:
                    t["completed_pomodoros"] = t.get("completed_pomodoros", 0) + 1
                    break
        models.save_data(self.data)

    # ==================== 提醒弹窗 ====================

    def _acknowledge_alert(self):
        if not self._alert_active:
            return
        self._alert_active = False
        self._alert.stop_sound()
        self._alert.close()
        if self._auto_start_after_ack:
            self._auto_start_after_ack = False
            self._start()

    # ==================== 任务操作 ====================

    def add_task(self, title, target):
        task = {
            "id": self.data["next_task_id"],
            "title": title,
            "target": target,
            "completed_pomodoros": 0,
            "done": False,
            "created": datetime.now().isoformat(),
        }
        self.data["next_task_id"] += 1
        self.data["tasks"].append(task)
        models.save_data(self.data)
        self.task_tab.refresh()

    def set_current_task(self, task_id):
        self.current_task_id = task_id
        self.task_tab.refresh()
        self.timer_tab.refresh(self)

    def mark_task_done(self, task_id):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                break
        models.save_data(self.data)
        self.task_tab.refresh()

    def delete_task(self, task_id):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        if self.current_task_id == task_id:
            self.current_task_id = None
        models.save_data(self.data)
        self.task_tab.refresh()
        self.timer_tab.refresh(self)

    def clear_done_tasks(self):
        self.data["tasks"] = [t for t in self.data["tasks"] if not t["done"]]
        models.save_data(self.data)
        self.task_tab.refresh()

    # ==================== 设置操作 ====================

    def save_settings(self, work_min, work_sec, break_min):
        self.settings["work_minutes"] = work_min
        self.settings["work_seconds"] = work_sec
        self.settings["break_minutes"] = break_min
        self.data["settings"] = self.settings
        models.save_data(self.data)
        if not self.running:
            self._switch_mode(self.mode)
            self.timer_tab.refresh(self)

    # ==================== 内部辅助 ====================

    def _refresh_all(self):
        self.timer_tab.refresh(self)
        self.task_tab.refresh()
        self.stats_tab.refresh()
        self.settings_tab.refresh()

    @staticmethod
    def _confirm(title, msg):
        return (
            QMessageBox.question(None, title, msg)
            == QMessageBox.StandardButton.Yes
        )
