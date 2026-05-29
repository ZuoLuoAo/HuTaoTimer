# 更新日志

## v2.0.0 (2026-05-29)

### 重大变更
- **框架迁移**：Tkinter → PyQt6，充分利用 Qt 现代 UI 能力
- **模块化重构**：632 行单文件拆分为 8 个独立模块

### 新增
- `pomodoro/main.py` — PyQt6 应用入口
- `pomodoro/main_window.py` — QMainWindow 主窗口与全局状态管理
- `pomodoro/models.py` — 数据持久化层（从旧版提取）
- `pomodoro/ui/timer_tab.py` — 计时页签，使用 QTimer 驱动
- `pomodoro/ui/task_tab.py` — 任务管理页签，使用 QTreeWidget
- `pomodoro/ui/stats_tab.py` — 统计页签，QPainter 手绘柱状图
- `pomodoro/ui/settings_tab.py` — 设置页签，使用 QSpinBox
- `pomodoro/ui/alert_dialog.py` — 完成提醒弹窗（非模态 QDialog）
- `pomodoro/resources/style.qss` — 胡桃主题 QSS 样式表（红棕金配色）
- `run.bat` — 启动脚本，解决 Anaconda Python 下 Qt6 DLL 冲突

### 修改
- `胡桃钟.spec` — 适配新入口文件与资源路径
- `runtime_hook.py` — 移除 ctypes 依赖，避免打包 DLL 缺失

### 移除
- `pomodoro.py` — 旧版 Tkinter 单文件（功能已全部迁移）

### 兼容性
- `data.json` 格式不变，可无缝从 v1.x 升级

---

## v1.1.0 (2026-05-28)

- 优化任务栏图标显示与打包配置

## v1.0.0

- 首个版本：Tkinter 番茄钟，含计时 / 任务 / 统计 / 设置四个页签
