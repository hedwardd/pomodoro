import rumps
class PomodoroApp(object):
    def __init__(self):
        self.config = {
            "app_name": "Pomodoro Remix",
            "start": "Start 30m Timer",
            "start2": "Start 15m Timer",
            "pause": "Pause Timer",
            "continue": "Continue Timer",
            "stop": "Stop Timer",
            "timer_end_message": "Time is up! Take a break :)",
            "break_menu": "Break",
            "start_break": "Start 10m Break",
            "start_break2": "Start 5m Break",
            "pause_break": "Pause Break",
            "continue_break": "Continue Break",
            "stop_break": "Stop Break",
            "break_end_message": "Break's up. Time to get back to it :)",
            "halfway_message": "Halfway there!",
            "overtime_message": "Wrap it up! You're {:2d} minutes over",
            "interval": 1800,
            "interval2": 900,
            "break_interval": 600,
            "break_interval2": 300,
            "overtime_interval": 300,
            # "interval": 10,
            # "break_interval": 8,
            # "overtime_interval": 60,
        }

        # Rumps Objects
        self.app = rumps.App(self.config["app_name"])
        self.timer = rumps.Timer(self.on_tick, 1)

        # Menu Setup
        self.start_pause_timer = rumps.MenuItem(
            title=self.config["start"], callback=self.start_timer)
        self.start_pause_timer2 = rumps.MenuItem(
            title=self.config["start2"], callback=self.start_timer)
        self.start_pause_break = rumps.MenuItem(
            title=self.config["start_break"], callback=self.start_timer)
        self.start_pause_break2 = rumps.MenuItem(
            title=self.config["start_break2"], callback=self.start_timer)
        self.stop_button = rumps.MenuItem(
            title=self.config["stop"], callback=None)

        self.break_submenu = rumps.MenuItem(title=self.config["break_menu"])
        self.break_submenu.add(self.start_pause_break)
        self.break_submenu.add(self.start_pause_break2)

        self.app.menu = [self.start_pause_timer, self.start_pause_timer2, self.stop_button, self.break_submenu]

        # Values/Attributes
        self.interval = self.config["interval"]
        self.interval2 = self.config["interval2"]
        self.break_interval = self.config["break_interval"]
        self.break_interval2 = self.config["break_interval2"]
        self.overtime_interval = self.config["overtime_interval"]
        self.is_break = False

        # Initiate
        self.set_up_menu()

    def set_up_menu(self):
        self.timer.stop()
        self.timer.count = 0
        self.app.title = "🍅"
        self.stop_button.set_callback(None)
        self.start_pause_timer.title = self.config["start"]
        self.start_pause_timer2.title = self.config["start2"]
        self.start_pause_break.title = self.config["start_break"]
        self.start_pause_break2.title = self.config["start_break2"]

    def on_tick(self, sender):
        time_left = sender.end - sender.count
        mins = time_left // 60 if time_left >= 0 else (-1 * time_left) // 60
        secs = time_left % 60 if time_left >= 0 else (-1 * time_left) % 60
        is_break = True if sender.end != sender.interval else False
        if time_left == 0:
            # Send different notification if on break
            noti_message = self.config["timer_end_message"] if not self.is_break else self.config["break_end_message"]
            rumps.notification(
                title=self.config["app_name"],
                subtitle=noti_message,
                message='')
        # Send halfway notification if not on break
        elif sender.count > 0 and sender.end / sender.count == 2 and not self.is_break:
            rumps.notification(
                title=self.config["app_name"],
                subtitle=self.config["halfway_message"],
                message='')
        # Send overtime notification if over by __ minutes
        elif time_left < 0 and time_left % self.overtime_interval == 0:
            subtitle = self.config["overtime_message"].format(mins)
            rumps.notification(
                title=self.config["app_name"],
                subtitle=subtitle,
                message='')
        formatted_time = '{:2d}:{:02d}'.format(mins, secs) if time_left >= 0 else '(+{:2d}:{:02d} )'.format(mins, secs) 
        self.app.title = formatted_time if not self.is_break else "🧘‍♂️" + formatted_time + "🧘‍♀️"
        sender.count += 1

    # TODO: Separate button text updates from timer update. I.e., separate actions
    def start_timer(self, sender):
        self.stop_button.set_callback(self.stop_timer)
        if sender.title == self.config["start"] or sender.title == self.config["start2"] or sender.title == self.config["continue"]:
            self.is_break = False
            if sender.title == self.config["start"]:
                self.timer.count = 0
                self.timer.end = self.interval
            elif sender.title == self.config["start2"]:
                self.timer.count = 0
                self.timer.end = self.interval2
            sender.title = self.config["pause"]
            self.timer.start()
        elif sender.title == self.config["start_break"] or sender.title == self.config["start_break2"] or sender.title == self.config["continue_break"]:
            self.is_break = True
            if sender.title == self.config["start_break"]:
                self.timer.count = 0
                self.timer.end = self.break_interval
            elif sender.title == self.config["start_break2"]:
                self.timer.count = 0
                self.timer.end = self.break_interval2
            sender.title = self.config["pause_break"]
            self.timer.start()
        elif sender.title == self.config["pause"]:
            sender.title = self.config["continue"]
            self.timer.stop()
        elif sender.title == self.config["pause_break"]:
            sender.title = self.config["continue_break"]
            self.timer.stop()

    def stop_timer(self, sender):
        self.set_up_menu()

    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = PomodoroApp()
    app.run()
