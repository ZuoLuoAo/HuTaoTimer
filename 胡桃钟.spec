# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pomodoro/main.py'],
    pathex=[],
    binaries=[
        ('D:/APPS/Anaconde/Library/bin/ffi.dll', '.'),
        ('D:/APPS/Anaconde/Library/bin/libcrypto-3-x64.dll', '.'),
        ('D:/APPS/Anaconde/Library/bin/liblzma.dll', '.'),
        ('D:/APPS/Anaconde/Library/bin/libbz2.dll', '.'),
    ],
    datas=[
        ('assets/icon.ico', 'assets'),
        ('assets/图标_胡桃.png', 'assets'),
        ('pomodoro/resources/style.qss', 'pomodoro/resources'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='胡桃钟',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 关闭 UPX 压缩，避免资源嵌入异常
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.ico'],
)
