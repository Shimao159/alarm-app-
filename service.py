# -*- coding: utf-8 -*-
"""前台常驻服务：保证锁屏/休眠时不被系统回收。"""
import datetime, os
from kivy.app import App
from kivy.uix.label import Label
from kivy.utils import platform


class ServiceApp(App):
    def build(self):
        self.title = "闹钟常驻服务"
        if platform == "android":
            self.make_foreground()
        return Label(text="Alarm service running")

    def make_foreground(self):
        try:
            from jnius import autoclass
            Context = autoclass("android.content.Context")
            Intent = autoclass("android.content.Intent")
            PendingIntent = autoclass("android.app.PendingIntent")
            NotificationBuilder = autoclass("android.app.Notification$Builder")
            NotificationChannel = autoclass("android.app.NotificationChannel")
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            service = autoclass("org.kivy.android.PythonService").mService

            nm = service.getSystemService(Context.NOTIFICATION_SERVICE)
            chan_id = "alarm_foreground"
            if hasattr(NotificationChannel, "IMPORTANCE_LOW"):
                chan = NotificationChannel(chan_id, "闹钟服务",
                                          NotificationChannel.IMPORTANCE_LOW)
                nm.createNotificationChannel(chan)
            builder = NotificationBuilder(service, chan_id)
            builder.setContentTitle("定时闹钟正在运行")
            builder.setContentText("点击可回到应用")
            builder.setSmallIcon(service.getApplicationInfo().icon)
            intent = Intent(service, activity.getClass())
            pi = PendingIntent.getActivity(service, 0, intent,
                                          PendingIntent.FLAG_UPDATE_CURRENT)
            builder.setContentIntent(pi)
            service.startForeground(1, builder.build())
        except Exception as e:
            print("foreground error:", e)


if __name__ == "__main__":
    ServiceApp().run()
