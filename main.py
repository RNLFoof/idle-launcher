import re
import time
from copy import deepcopy
from datetime import timedelta
from os import system

import pyautogui
from win32gui import GetWindowText, GetForegroundWindow
from win32timezone import utcnow

class IdleWatcher:
    def __init__(self):
        self.mouse_position = None
        self.previous_state = None
        self.is_idle = False
        self._locked_idle_duration = None
        self.idle_since = utcnow()
        self.last_check = utcnow()
        self.update_previous_state()

    def update_previous_state(self):
        self.previous_state = deepcopy(self)
        self.previous_state.lock_idle_duration()
        self.previous_state.previous_state = None

    def lock_idle_duration(self):
        self._locked_idle_duration = self.idle_duration()

    def update_mouse_position(self):
        self.mouse_position = pyautogui.position()

    def update_state(self):
        update_start = utcnow()  # Called once so that the various time sets below are all the same
        self.update_mouse_position()
        window_text = GetWindowText(GetForegroundWindow())

        if re.search(r"PyCharm|VLC|YouTube|Hollow Knight|Sonic Robo", window_text):
            self.is_idle = False
        elif self.mouse_position == self.previous_state.mouse_position:
            self.is_idle = True
        else:
            self.is_idle = False

        self.last_check = update_start
        if self.is_idle and self.idle_since is None:
            self.idle_since = update_start
        if not self.is_idle:
            self.idle_since = None

        self.update_previous_state()

    def idle_duration(self):
        if self._locked_idle_duration is not None:
            return self._locked_idle_duration
        if not self.is_idle:
            return timedelta()
        return utcnow() - self.idle_since

    def just_passed_idle_duration(self, duration):
        print(self.previous_state.idle_duration())
        return self.idle_duration() >= duration > self.previous_state.idle_duration()

    def loop(self):
        return

    def __str__(self):
        return f"Idle for {self.idle_duration()}, last check {self.last_check.time()}"


def main_loop():
    idle_watcher = IdleWatcher()
    print(idle_watcher)
    while True:
        time.sleep(1)
        print("---")
        idle_watcher.update_state()
        print(idle_watcher)
        if not idle_watcher.is_idle:
            continue

        for x in range(10):
            td = timedelta(seconds=x)
            print(td, idle_watcher.just_passed_idle_duration(td))
        continue

        if idle_watcher.just_passed_idle_duration(timedelta(minutes=5)):
            # Killed because Discord doesn't send notifs to your phone if your computer is active.
            # /F, for force, because some of Discord's subprocesses don't close without it, it seems.
            system(r"taskkill /F /IM Discord.exe")

        if idle_watcher.just_passed_idle_duration(timedelta(minutes=10)):
            system(r"S:\Code\GML\Projects\Space-Screensaver\screensaver.exe")



main_loop()