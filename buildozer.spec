[app]

# (str) Title of your application
title = 定时闹钟

# (str) Package name
package.name = alarmapp
package.domain = org.kivy

# (str) Source files to include (space separated)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Application requirements
# 钉死 Python 3.11.9 与 Kivy 2.3.0，避免拉到 3.14
requirements = python3==3.11.9,kivy==2.3.0

# (str) App versioning
version = 2.0

# (list) Permissions
android.permissions = FOREGROUND_SERVICE,FOREGROUND_SERVICE_ALARM,WAKE_LOCK,VIBRATE,POST_NOTIFICATIONS,SCHEDULE_EXACT_ALARM,RECEIVE_BOOT_COMPLETED,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS

# (int) Target SDK, minimum SDK
android.api = 33
android.minapi = 21

# (str) NDK version
android.ndk = 25b

# 强制 APK 内嵌 Python 3.11.9
android.python_version = 3.11.9

# (list) Android architectures
android.archs = arm64-v8a,armeabi-v7a

# 前台服务类型（Android 14+ 必需）
android.foreground_service_type = alarm

# 服务名称
android.service_name = ServiceAlarms

# 启动类
android.entrypoint = org.kivy.android.PythonService

# 横竖屏
orientation = portrait

# 全屏
fullscreen = 0

# 状态栏
android.statusbar = 1

# 启动图标与预设图标
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# 是否允许备份
android.allow_backup = True

# p4a 分支
p4a.branch = master

# 日志级别
log_level = 2


[buildozer]

log_level = 2
build_dir = .buildozer

# android.ndk_path =
# android.sdk_path =
# android.ant_path =


[android]

android.debug = True
# android.numeric_version =

android.accept_sdk_license = True
