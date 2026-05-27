# PyInstaller runtime hook — 在任何 Python 代码执行前设置 AppUserModelID
# 这比 pomodoro.py 中的模块级别设置更早，确保 bootloader 阶段就已正确标识
import ctypes
import sys

if sys.platform == "win32":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("hutaozhong.pomodoro.app")
    except Exception:
        pass
