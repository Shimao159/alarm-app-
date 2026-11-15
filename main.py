# -*- coding: utf-8 -*-
"""
定时闹钟 —— 常驻版
- 启动时间 + 间隔循环提醒，过滤区间内不响
- 推算"铺满当天并跨天衔接"，保证第二天 6:55 照样叫
- 点"停止"只消音本次，服务不停；"停止并退出"才关闭
"""
import os, datetime, json, traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
from kivy.utils import platform

CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alarm.conf")


def mins(t):
    return t[0] * 60 + t[1]


class AlarmApp(App):
    def build(self):
        self.title = "定时闹钟"
        c = self.load_conf()
        self.start_time = c.get("start", (6, 55))
        self.interval = c.get("interval", 30)
        self.quiet_start = c.get("qs", (23, 30))
        self.quiet_end = c.get("qe", (1, 0))

        root = BoxLayout(orientation="vertical", padding=16, spacing=10)
        root.add_widget(Label(text="⏰ 定时闹钟", font_size=28,
                              size_hint_y=None, height=48))

        self.status = Label(text="未启动", font_size=20, color=(1, 0.4, 0.4, 1),
                            size_hint_y=None, height=40)
        root.add_widget(self.status)

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=260)
        self._add(grid, "启动时间 (HH:MM)", "start_input", self._fmt(self.start_time))
        self._add(grid, "间隔 (分钟)", "interval_input", str(self.interval))
        self._add(grid, "过滤开始 (HH:MM)", "qs_input", self._fmt(self.quiet_start))
        self._add(grid, "过滤结束 (HH:MM)", "qe_input", self._fmt(self.quiet_end))
        root.add_widget(grid)

        btns = BoxLayout(size_hint_y=None, height=55, spacing=12)
        self.start_btn = Button(text="▶ 开始", font_size=20,
                                background_color=(0.2, 0.7, 0.3, 1))
        self.start_btn.bind(on_press=self.start_alarm)
        btns.add_widget(self.start_btn)
        self.stop_btn = Button(text="⏹ 停止", font_size=20,
                               background_color=(0.8, 0.2, 0.2, 1), disabled=True)
        self.stop_btn.bind(on_press=self.stop_alarm)
        btns.add_widget(self.stop_btn)
        self.quit_btn = Button(text="✖ 退出", font_size=20,
                               background_color=(0.4, 0.4, 0.4, 1))
        self.quit_btn.bind(on_press=lambda *a: self._quit())
        btns.add_widget(self.quit_btn)
        root.add_widget(btns)

        root.add_widget(Label(text="— 运行日志 —", size_hint_y=None, height=28))
        self.log = Label(text="", halign="left", valign="top")
        self.log.bind(size=self.log.setter("text_size"))
        root.add_widget(self.log)

        self.running = False
        self._event = None
        self.next_time = None
        return root

    def _add(self, grid, label, attr, val):
        grid.add_widget(Label(text=label))
        ti = TextInput(text=val, multiline=False, halign="center")
        setattr(self, attr, ti)
        grid.add_widget(ti)

    @staticmethod
    def _fmt(t):
        return f"{t[0]:02d}:{t[1]:02d}"

    def log_msg(self, msg):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.log.text = f"[{now}] {msg}\n" + self.log.text
        print(f"[{now}] {msg}")

    def load_conf(self):
        try:
            with open(CONF) as f:
                return json.load(f)
        except Exception:
            return {}

    def save_conf(self):
        try:
            with open(CONF, "w") as f:
                json.dump({"start": list(self.start_time), "interval": self.interval,
                           "qs": list(self.quiet_start), "qe": list(self.quiet_end)}, f)
        except Exception as e:
            self.log_msg(f"保存配置失败: {e}")

    def parse_time(self, text):
        h, m = text.strip().split(":")
        return (int(h), int(m))

    def in_quiet(self, dt):
        s, e = mins(self.quiet_start), mins(self.quiet_end)
        if s == e:
            return False
        m = dt.hour * 60 + dt.minute
        return m >= s or m < e if s > e else s <= m < e

    def next_wake(self, after):
        """核心：算出 after 之后下一个该响的时刻（跳过过滤区，跨天衔接）"""
        cand = after.replace(second=0, microsecond=0) + datetime.timedelta(minutes=self.interval)
        # 若落在过滤区，直接跳到过滤结束时刻对齐起点，再按间隔铺
        if self.in_quiet(cand):
            qs, qe = self.quiet_start, self.quiet_end
            end = cand.replace(hour=qe[0], minute=qe[1], second=0, microsecond=0)
            if mins(qs) > mins(qe) and cand < end + datetime.timedelta(days=1):
                end = end + datetime.timedelta(days=1)
            cand = end
            # 对齐到间隔起点
            base = datetime.datetime.combine(cand.date(), datetime.time(
                self.start_time[0], self.start_time[1]))
            while cand < base + datetime.timedelta(minutes=self.interval):
                cand += datetime.timedelta(minutes=self.interval)
        return cand

    def start_alarm(self, *a):
        try:
            self.start_time = self.parse_time(self.start_input.text)
            self.interval = int(self.interval_input.text)
            self.quiet_start = self.parse_time(self.qs_input.text)
            self.quiet_end = self.parse_time(self.qe_input.text)
        except Exception as e:
            self.log_msg(f"输入格式错误: {e}")
            return
        self.save_conf()

        now = datetime.datetime.now()
        # 以今天启动时刻为起点铺满，再找下一个该响的
        base = now.replace(hour=self.start_time[0], minute=self.start_time[1],
                           second=0, microsecond=0)
        if base <= now:
            base += datetime.timedelta(days=1)
        self.next_time = base
        # 把今天已过的时刻快速推进到"下一个未来时刻"
        while self.next_time <= now or self.in_quiet(self.next_time):
            nxt = self.next_wake(self.next_time - datetime.timedelta(minutes=self.interval))
            if nxt <= self.next_time:
                self.next_time += datetime.timedelta(minutes=self.interval)
            else:
                self.next_time = nxt
            if (self.next_time - now).days > 2:  # 安全兜底
                break

        self.running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        self.schedule_next()
        self.log_msg(f"已启动，下次提醒: {self._fmt_hm(self.next_time)}")
        if platform == "android":
            self.start_android_service()

    def _fmt_hm(self, dt):
        return f"{dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"

    def schedule_next(self):
        if not self.running:
            return
        delay = (self.next_time - datetime.datetime.now()).total_seconds()
        if delay < 0:
            delay = 0
        self._event = Clock.schedule_once(self.fire, delay)
        self.status.text = f"运行中 · 下次: {self._fmt_hm(self.next_time)}"
        self.status.color = (0.4, 0.9, 0.4, 1)

    def fire(self, *a):
        if not self.running:
            return
        now = datetime.datetime.now()
        self.log_msg(f"🔔 闹钟触发! ({now.hour:02d}:{now.minute:02d})")
        if platform == "android":
            self.android_notify()
        else:
            print("\a")
        self.next_time = self.next_wake(now)
        self.schedule_next()

    def stop_alarm(self, *a):
        # 只消音本次，服务不停，继续排下一次
        if self._event:
            self._event.cancel()
        self.status.text = "已停止本次 · 等待下一轮"
        self.status.color = (0.9, 0.9, 0.3, 1)
        self.log_msg("已停止本次，继续常驻等待下一轮")
        self.running = True
        self.schedule_next()

    def start_android_service(self):
        try:
            from jnius import autoclass
            service = autoclass("org.kivy.android.PythonService").mService
            Intent = autoclass("android.content.Intent")
            ctx = autoclass("org.kivy.android.PythonActivity").mActivity
            intent = Intent(ctx, autoclass("com.alarmapp.ServiceAlarms"))
            ctx.startService(intent)
        except Exception as e:
            self.log_msg(f"前台服务启动提示: {e}")

    def _quit(self):
        self.running = False
        if self._event:
            self._event.cancel()
        self.status.text = "已退出"
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        self.log_msg("已退出")
        Clock.schedule_once(lambda *a: App.get_running_app().stop(), 0.5)


if __name__ == "__main__":
    AlarmApp().run()
