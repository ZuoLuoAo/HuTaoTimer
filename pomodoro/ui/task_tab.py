# -*- coding: utf-8 -*-
"""任务管理页签"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt


class TaskTab(QWidget):
    """任务 CRUD 与列表显示"""

    def __init__(self, window):
        super().__init__()
        self._window = window
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # --- 输入行 ---
        input_layout = QHBoxLayout()

        input_layout.addWidget(QLabel("任务名称:"))

        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("输入任务名称")
        self.title_entry.returnPressed.connect(self._add_task)
        input_layout.addWidget(self.title_entry, stretch=1)

        input_layout.addWidget(QLabel("目标番茄数:"))

        self.target_entry = QLineEdit("1")
        self.target_entry.setFixedWidth(40)
        self.target_entry.returnPressed.connect(self._add_task)
        input_layout.addWidget(self.target_entry)

        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self._add_task)
        input_layout.addWidget(add_btn)

        layout.addLayout(input_layout)

        # --- 任务列表 ---
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["状态", "任务", "进度"])
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.setAlternatingRowColors(True)
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 50)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 80)
        layout.addWidget(self.tree, stretch=1)

        # --- 按钮行 ---
        btn_layout = QHBoxLayout()

        set_btn = QPushButton("设为当前")
        set_btn.clicked.connect(self._set_current)
        btn_layout.addWidget(set_btn)

        done_btn = QPushButton("标记完成/取消")
        done_btn.clicked.connect(self._mark_done)
        btn_layout.addWidget(done_btn)

        del_btn = QPushButton("删除")
        del_btn.clicked.connect(self._delete)
        btn_layout.addWidget(del_btn)

        clear_btn = QPushButton("清除已完成")
        clear_btn.clicked.connect(self._clear_done)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

    def refresh(self):
        self.tree.clear()
        for task in self._window.data["tasks"]:
            if task["done"]:
                status = "✓"
            elif task["id"] == self._window.current_task_id:
                status = "●"
            else:
                status = ""
            progress = f"{task.get('completed_pomodoros', 0)}/{task['target']}"
            item = QTreeWidgetItem([status, task["title"], progress])
            item.setData(0, Qt.ItemDataRole.UserRole, task["id"])
            self.tree.addTopLevelItem(item)

    def _selected_id(self):
        items = self.tree.selectedItems()
        if not items:
            return None
        return items[0].data(0, Qt.ItemDataRole.UserRole)

    def _add_task(self):
        title = self.title_entry.text().strip()
        if not title:
            return
        try:
            target = max(1, int(self.target_entry.text()))
        except ValueError:
            target = 1
        self._window.add_task(title, target)
        self.title_entry.clear()
        self.target_entry.setText("1")

    def _set_current(self):
        tid = self._selected_id()
        if tid is None:
            QMessageBox.information(self, "提示", "请先在列表中选择一个任务")
            return
        self._window.set_current_task(tid)

    def _mark_done(self):
        tid = self._selected_id()
        if tid is None:
            return
        self._window.mark_task_done(tid)

    def _delete(self):
        tid = self._selected_id()
        if tid is None:
            return
        if not self._confirm("删除", "确定要删除该任务吗？"):
            return
        self._window.delete_task(tid)

    def _clear_done(self):
        if not any(t["done"] for t in self._window.data["tasks"]):
            return
        if not self._confirm("清除", "确定要清除所有已完成的任务吗？"):
            return
        self._window.clear_done_tasks()

    @staticmethod
    def _confirm(title, msg):
        return (
            QMessageBox.question(None, title, msg)
            == QMessageBox.StandardButton.Yes
        )
