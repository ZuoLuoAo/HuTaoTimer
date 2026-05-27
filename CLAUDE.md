# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

胡桃钟 (Hu Tao Clock) — a Pomodoro timer desktop app built with Python + Tkinter, themed around Genshin Impact character 胡桃. Single-file application (`pomodoro.py`) with JSON persistence.

## Commands

```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Git Bash
# 或: .venv\Scripts\activate   # CMD / PowerShell

# Run the app
python pomodoro.py

# Build standalone exe with PyInstaller
pyinstaller 胡桃钟.spec
```

No test suite or linter is configured.

## 虚拟环境

项目使用 Python 虚拟环境 `.venv/`，通过 PyInstaller 构建独立 exe（`dist/胡桃钟.exe`），无需额外启动脚本。

## Architecture

**Single-class Tkinter app** (`PomodoroApp` in `pomodoro.py:76`). The root window contains a `ttk.Notebook` with four tabs: 计时 (timer), 任务 (tasks), 统计 (stats), 设置 (settings).

**Timer flow:**
- `_tick()` decrements `remaining` every second via `root.after(1000, ...)`
- When `remaining` hits 0 → `_on_phase_complete()` records the pomodoro (if work phase), switches mode (work↔break), and shows a non-modal alert popup with repeating sound
- The alert popup must be manually acknowledged before the next phase starts (auto-start only for work→break)

**Data persistence** (`data.json`):
- `load_data()` reads on startup, fills in missing defaults, returns the data dict
- `save_data()` writes the full dict back to disk
- `DATA_DIR` is `sys.executable` parent when frozen (PyInstaller), otherwise `__file__` parent
- History keys are ISO-format dates (`YYYY-MM-DD`), values are lists of `{task_id, completed_at}` records

**Settings structure (with defaults):**
```python
{
    "work_minutes": 25,
    "work_seconds": 0,
    "break_minutes": 5,
}
```

**Task structure:**
```python
{
    "id": int,           # unique, from next_task_id counter
    "title": str,
    "target": int,       # target pomodoro count
    "completed_pomodoros": int,
    "done": bool,
    "created": str,      # ISO datetime
}
```

**Key details:**
- `winsound` is used for alert playback on Windows (with `None` import guard)
- `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID` sets the taskbar icon ID
- PyInstaller 构建的 `胡桃钟.exe` 默认无控制台窗口（`console=False`）
- Chart in stats tab is hand-drawn on a Tkinter Canvas (no matplotlib dependency)
