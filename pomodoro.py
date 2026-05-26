# -*- coding: utf-8 -*-
"""胡桃钟 - Python + Tkinter 实现"""
import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None

if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).parent
else:
    DATA_DIR = Path(__file__).resolve().parent
DATA_FILE = DATA_DIR / "data.json"

DEFAULT_SETTINGS = {
    "work_minutes": 5,
    "work_seconds": 5,
    "break_minutes": 5,
}

MODE_WORK = "work"
MODE_BREAK = "break"

MODE_LABELS = {
    MODE_WORK: "工作中",
    MODE_BREAK: "休息",
}

MODE_COLORS = {
    MODE_WORK: "#e74c3c",
    MODE_BREAK: "#27ae60",
}


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_SETTINGS.items():
                    data.setdefault("settings", {}).setdefault(k, v)
                data.setdefault("tasks", [])
                data.setdefault("history", {})
                data.setdefault("next_task_id", 1)
                return data
        except Exception:
            pass
    return {
        "settings": DEFAULT_SETTINGS.copy(),
        "tasks": [],
        "history": {},
        "next_task_id": 1,
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _work_duration(settings):
    return settings["work_minutes"] * 60 + settings.get("work_seconds", 0)


def _break_duration(settings):
    return settings["break_minutes"] * 60


class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("胡桃钟")
        self.root.geometry("540x640")
        self.root.minsize(500, 600)

        icon_path = DATA_DIR / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        self.data = load_data()
        self.settings = self.data["settings"]

        self.mode = MODE_WORK
        self.remaining = _work_duration(self.settings)
        self.running = False
        self.session_completed = 0
        self.current_task_id = None
        self._timer_job = None

        self._alert_window = None
        self._alert_job = None
        self._alert_active = False
        self._auto_start_after_ack = False

        self._build_ui()
        self._update_display()
        self._refresh_tasks()
        self._refresh_stats()

    def _build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.timer_frame = ttk.Frame(notebook)
        self.task_frame = ttk.Frame(notebook)
        self.stats_frame = ttk.Frame(notebook)
        self.settings_frame = ttk.Frame(notebook)

        notebook.add(self.timer_frame, text="计时")
        notebook.add(self.task_frame, text="任务")
        notebook.add(self.stats_frame, text="统计")
        notebook.add(self.settings_frame, text="设置")

        self._build_timer_tab()
        self._build_task_tab()
        self._build_stats_tab()
        self._build_settings_tab()

    def _build_timer_tab(self):
        self.mode_label = tk.Label(
            self.timer_frame,
            text=MODE_LABELS[self.mode],
            font=("Microsoft YaHei", 18, "bold"),
            fg=MODE_COLORS[self.mode],
        )
        self.mode_label.pack(pady=(40, 10))

        self.time_label = tk.Label(
            self.timer_frame,
            text="05:05",
            font=("Consolas", 80, "bold"),
        )
        self.time_label.pack(pady=10)

        self.current_task_label = ttk.Label(
            self.timer_frame,
            text="当前任务: 无",
            font=("Microsoft YaHei", 11),
            foreground="#666",
        )
        self.current_task_label.pack(pady=5)

        self.pomodoro_count_label = ttk.Label(
            self.timer_frame,
            text="本次会话已完成: 0 个番茄",
            font=("Microsoft YaHei", 10),
            foreground="#888",
        )
        self.pomodoro_count_label.pack(pady=5)

        button_frame = ttk.Frame(self.timer_frame)
        button_frame.pack(pady=30)

        self.start_button = ttk.Button(
            button_frame, text="开始", width=12, command=self.toggle_timer
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.skip_button = ttk.Button(
            button_frame, text="跳过", width=12, command=self.skip_phase
        )
        self.skip_button.grid(row=0, column=1, padx=5)

        self.reset_button = ttk.Button(
            button_frame, text="重置", width=12, command=self.reset_timer
        )
        self.reset_button.grid(row=0, column=2, padx=5)

    def _build_task_tab(self):
        top = ttk.Frame(self.task_frame)
        top.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(top, text="任务名称:").grid(row=0, column=0, sticky="w")
        self.task_entry = ttk.Entry(top)
        self.task_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        ttk.Label(top, text="目标番茄数:").grid(row=0, column=2, sticky="w")
        self.task_target_entry = ttk.Entry(top, width=5)
        self.task_target_entry.grid(row=0, column=3, padx=5)
        self.task_target_entry.insert(0, "1")

        ttk.Button(top, text="添加", command=self.add_task).grid(row=0, column=4, padx=5)
        top.columnconfigure(1, weight=1)

        list_frame = ttk.Frame(self.task_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("status", "title", "progress")
        self.task_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        self.task_tree.heading("status", text="状态")
        self.task_tree.heading("title", text="任务")
        self.task_tree.heading("progress", text="进度")
        self.task_tree.column("status", width=60, anchor="center")
        self.task_tree.column("title", width=300)
        self.task_tree.column("progress", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(self.task_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="设为当前", command=self.set_current_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="标记完成/取消", command=self.mark_task_done).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除", command=self.delete_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="清除已完成", command=self.clear_done_tasks).pack(side=tk.LEFT, padx=2)

    def _build_stats_tab(self):
        info = ttk.Frame(self.stats_frame)
        info.pack(pady=20)

        self.today_label = tk.Label(info, text="今日\n0", font=("Microsoft YaHei", 14), fg="#e74c3c")
        self.today_label.grid(row=0, column=0, padx=25)

        self.week_label = tk.Label(info, text="本周\n0", font=("Microsoft YaHei", 14), fg="#2980b9")
        self.week_label.grid(row=0, column=1, padx=25)

        self.total_label = tk.Label(info, text="累计\n0", font=("Microsoft YaHei", 14), fg="#27ae60")
        self.total_label.grid(row=0, column=2, padx=25)

        ttk.Label(self.stats_frame, text="近 7 天番茄数", font=("Microsoft YaHei", 12)).pack(pady=(20, 5))
        self.chart_canvas = tk.Canvas(
            self.stats_frame, width=480, height=240, bg="white",
            highlightthickness=1, highlightbackground="#ddd"
        )
        self.chart_canvas.pack(pady=10)

        ttk.Button(self.stats_frame, text="刷新", command=self._refresh_stats).pack(pady=5)

    def _build_settings_tab(self):
        f = ttk.Frame(self.settings_frame)
        f.pack(padx=30, pady=30, fill=tk.X)

        ttk.Label(f, text="工作时长 (分钟):").grid(row=0, column=0, sticky="w", pady=8)
        self.work_min_var = tk.IntVar(value=self.settings["work_minutes"])
        ttk.Spinbox(f, from_=0, to=120, textvariable=self.work_min_var, width=8).grid(row=0, column=1, sticky="w", pady=8, padx=10)

        ttk.Label(f, text="工作时长 (秒):").grid(row=1, column=0, sticky="w", pady=8)
        self.work_sec_var = tk.IntVar(value=self.settings.get("work_seconds", 0))
        ttk.Spinbox(f, from_=0, to=59, textvariable=self.work_sec_var, width=8).grid(row=1, column=1, sticky="w", pady=8, padx=10)

        ttk.Label(f, text="休息时长 (分钟):").grid(row=2, column=0, sticky="w", pady=8)
        self.break_var = tk.IntVar(value=self.settings["break_minutes"])
        ttk.Spinbox(f, from_=1, to=120, textvariable=self.break_var, width=8).grid(row=2, column=1, sticky="w", pady=8, padx=10)

        ttk.Button(f, text="保存设置", command=self.save_settings).grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Label(
            f,
            text=f"数据存储位置:\n{DATA_FILE}",
            font=("Microsoft YaHei", 9),
            foreground="#888",
            justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=10)

    def toggle_timer(self):
        if self._alert_active:
            self._acknowledge_alert()
            return
        if self.running:
            self._pause()
        else:
            self._start()

    def _start(self):
        self.running = True
        self.start_button.config(text="暂停")
        self._tick()

    def _pause(self):
        self.running = False
        self.start_button.config(text="继续")
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None

    def _tick(self):
        if not self.running:
            return
        if self.remaining <= 0:
            self._on_phase_complete()
            return
        self.remaining -= 1
        self._update_display()
        self._timer_job = self.root.after(1000, self._tick)

    def _update_display(self):
        m = self.remaining // 60
        s = self.remaining % 60
        self.time_label.config(text=f"{m:02d}:{s:02d}", fg=MODE_COLORS[self.mode])
        self.mode_label.config(text=MODE_LABELS[self.mode], fg=MODE_COLORS[self.mode])
        self.pomodoro_count_label.config(text=f"本次会话已完成: {self.session_completed} 个番茄")

        if self.current_task_id is not None:
            task = next((t for t in self.data["tasks"] if t["id"] == self.current_task_id), None)
            if task:
                self.current_task_label.config(text=f"当前任务: {task['title']}")
                return
        self.current_task_label.config(text="当前任务: 无")

    def _play_alert_sound(self):
        if not self._alert_active:
            return
        if winsound is not None:
            try:
                winsound.PlaySound(
                    "SystemExclamation",
                    winsound.SND_ALIAS | winsound.SND_ASYNC,
                )
            except Exception:
                self.root.bell()
        else:
            self.root.bell()
        self._alert_job = self.root.after(1200, self._play_alert_sound)

    def _stop_alert_sound(self):
        if self._alert_job is not None:
            self.root.after_cancel(self._alert_job)
            self._alert_job = None
        if winsound is not None:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def _show_alert_window(self, msg):
        win = tk.Toplevel(self.root)
        win.title("胡桃钟")
        win.geometry("320x140")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.protocol("WM_DELETE_WINDOW", self._acknowledge_alert)

        tk.Label(
            win, text=msg, font=("Microsoft YaHei", 11),
            wraplength=280, justify="center",
        ).pack(expand=True, padx=15, pady=15)
        ttk.Button(win, text="继续", width=12, command=self._acknowledge_alert).pack(pady=(0, 15))

        self._alert_window = win

    def _acknowledge_alert(self):
        if not self._alert_active:
            return
        self._alert_active = False
        self._stop_alert_sound()
        if self._alert_window is not None:
            try:
                self._alert_window.destroy()
            except Exception:
                pass
            self._alert_window = None
        if self._auto_start_after_ack:
            self._auto_start_after_ack = False
            self._start()

    def _on_phase_complete(self):
        self.running = False
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None

        finished_work = self.mode == MODE_WORK
        if finished_work:
            self._record_pomodoro()
            self.session_completed += 1
            self._switch_mode(MODE_BREAK)
            msg = "工作完成！点击继续开始休息倒计时。"
        else:
            self._switch_mode(MODE_WORK)
            msg = "休息结束，点击继续开始新的工作。"

        self.start_button.config(text="开始")
        self._refresh_tasks()
        self._refresh_stats()
        self._update_display()

        self._auto_start_after_ack = finished_work
        self._alert_active = True
        self._show_alert_window(msg)
        self._play_alert_sound()

    def _switch_mode(self, mode):
        self.mode = mode
        if mode == MODE_WORK:
            self.remaining = _work_duration(self.settings)
        else:
            self.remaining = _break_duration(self.settings)

    def skip_phase(self):
        if self._alert_active:
            self._acknowledge_alert()
            return
        if not messagebox.askyesno("跳过", "确定要跳过当前阶段吗？"):
            return
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None
        self.running = False
        self.remaining = 0
        self._on_phase_complete()

    def reset_timer(self):
        if self._alert_active:
            self._acknowledge_alert()
            return
        if not messagebox.askyesno("重置", "确定要重置当前计时器吗？"):
            return
        if self._timer_job:
            self.root.after_cancel(self._timer_job)
            self._timer_job = None
        self.running = False
        self._switch_mode(MODE_WORK)
        self.start_button.config(text="开始")
        self._update_display()

    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            return
        try:
            target = max(1, int(self.task_target_entry.get()))
        except ValueError:
            target = 1

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
        save_data(self.data)

        self.task_entry.delete(0, tk.END)
        self.task_target_entry.delete(0, tk.END)
        self.task_target_entry.insert(0, "1")
        self._refresh_tasks()

    def _refresh_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        for task in self.data["tasks"]:
            if task["done"]:
                status = "✓"
            elif task["id"] == self.current_task_id:
                status = "●"
            else:
                status = ""
            progress = f"{task.get('completed_pomodoros', 0)}/{task['target']}"
            self.task_tree.insert(
                "", tk.END, iid=str(task["id"]),
                values=(status, task["title"], progress),
            )

    def _selected_task_id(self):
        sel = self.task_tree.selection()
        if not sel:
            return None
        return int(sel[0])

    def set_current_task(self):
        tid = self._selected_task_id()
        if tid is None:
            messagebox.showinfo("提示", "请先在列表中选择一个任务")
            return
        self.current_task_id = tid
        self._refresh_tasks()
        self._update_display()

    def mark_task_done(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        for t in self.data["tasks"]:
            if t["id"] == tid:
                t["done"] = not t["done"]
                break
        save_data(self.data)
        self._refresh_tasks()

    def delete_task(self):
        tid = self._selected_task_id()
        if tid is None:
            return
        if not messagebox.askyesno("删除", "确定要删除该任务吗？"):
            return
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != tid]
        if self.current_task_id == tid:
            self.current_task_id = None
        save_data(self.data)
        self._refresh_tasks()
        self._update_display()

    def clear_done_tasks(self):
        if not any(t["done"] for t in self.data["tasks"]):
            return
        if not messagebox.askyesno("清除", "确定要清除所有已完成的任务吗？"):
            return
        self.data["tasks"] = [t for t in self.data["tasks"] if not t["done"]]
        save_data(self.data)
        self._refresh_tasks()

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
        save_data(self.data)

    def _refresh_stats(self):
        today = date.today()
        history = self.data.get("history", {})

        today_count = len(history.get(today.isoformat(), []))
        week_start = today - timedelta(days=today.weekday())
        week_count = sum(
            len(history.get((week_start + timedelta(days=i)).isoformat(), []))
            for i in range(7)
        )
        total = sum(len(v) for v in history.values())

        self.today_label.config(text=f"今日\n{today_count}")
        self.week_label.config(text=f"本周\n{week_count}")
        self.total_label.config(text=f"累计\n{total}")

        self._draw_chart(history, today)

    def _draw_chart(self, history, today):
        canvas = self.chart_canvas
        canvas.delete("all")

        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        counts = [len(history.get(d.isoformat(), [])) for d in days]
        max_count = max(counts) if max(counts) > 0 else 1

        width = 480
        height = 240
        padding_left = 35
        padding_bottom = 35
        padding_top = 20
        chart_w = width - padding_left - 15
        chart_h = height - padding_top - padding_bottom
        gap = chart_w / 7
        bar_w = gap * 0.55

        baseline_y = padding_top + chart_h
        canvas.create_line(padding_left, baseline_y, padding_left + chart_w, baseline_y, fill="#999")

        for i, (d, c) in enumerate(zip(days, counts)):
            x = padding_left + gap * i + (gap - bar_w) / 2
            bar_h = (c / max_count) * chart_h if max_count else 0
            y = baseline_y - bar_h
            color = "#e74c3c" if d == today else "#3498db"
            canvas.create_rectangle(x, y, x + bar_w, baseline_y, fill=color, outline="")
            if c > 0:
                canvas.create_text(x + bar_w / 2, y - 10, text=str(c), font=("Arial", 10, "bold"))
            label = f"{d.month}/{d.day}"
            canvas.create_text(x + bar_w / 2, baseline_y + 14, text=label, font=("Arial", 9), fill="#666")

    def save_settings(self):
        work_min = max(0, self.work_min_var.get())
        work_sec = max(0, min(59, self.work_sec_var.get()))
        if work_min == 0 and work_sec == 0:
            work_sec = 1
        self.settings["work_minutes"] = work_min
        self.settings["work_seconds"] = work_sec
        self.settings["break_minutes"] = max(1, self.break_var.get())
        self.data["settings"] = self.settings
        save_data(self.data)
        if not self.running:
            self._switch_mode(self.mode)
            self._update_display()
        messagebox.showinfo("提示", "设置已保存")


def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("hutaozhong.app")
    root = tk.Tk()
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass
    app = PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
