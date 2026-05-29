# -*- coding: utf-8 -*-
"""数据模型与 JSON 持久化"""
import json
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

# ---------- 路径 ----------
if getattr(sys, "frozen", False):
    DATA_DIR = Path(sys.executable).parent
    RESOURCE_DIR = Path(sys._MEIPASS)
else:
    DATA_DIR = Path(__file__).resolve().parent.parent
    RESOURCE_DIR = DATA_DIR
DATA_FILE = DATA_DIR / "data.json"

# ---------- 默认设置 ----------
DEFAULT_SETTINGS = {
    "work_minutes": 5,
    "work_seconds": 5,
    "break_minutes": 5,
}

# ---------- 模式常量 ----------
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


def work_duration(settings):
    return settings["work_minutes"] * 60 + settings.get("work_seconds", 0)


def break_duration(settings):
    return settings["break_minutes"] * 60


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


def get_today_count(history):
    today = date.today().isoformat()
    return len(history.get(today, []))


def get_week_count(history):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    return sum(
        len(history.get((week_start + timedelta(days=i)).isoformat(), []))
        for i in range(7)
    )


def get_total_count(history):
    return sum(len(v) for v in history.values())


def get_last_7_days(history):
    today = date.today()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    return [(d, len(history.get(d.isoformat(), []))) for d in days]
