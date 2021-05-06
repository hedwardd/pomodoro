import rumps


class PomodoroApp(object):
    def __init__(self):
        self.config = {
            "app_name": "Pomodoro",
            "start": "Start Timer",
            "start_break": "Start Break",
            "pause": "Pause Timer",
            "pause_break": "Pause Break",
            "continue": "Continue Timer",
            "continue_break": "Continue Break",
            "stop": "Stop Timer",
            "stop_break": "Stop Break",
            "timer_end_message": "Time is up! Take a break :)",
            "break_end_message": "Break is up. Time to get back to it :)",
            "halfway_message": "Halfway there!",
            "interval": 1800,
            "break_interval": 600
        }
        self.app = rumps.App(self.config["app_name"])
        self.timer = rumps.Timer(self.on_tick, 1)
        self.interval = self.config["interval"]
        self.break_interval = self.config["break_interval"]
        self.set_up_menu()
        self.start_pause_button = rumps.MenuItem(
            title=self.config["start"], callback=self.start_timer)
        self.start_pause_break_button = rumps.MenuItem(
            title=self.config["start_break"], callback=self.start_timer)
        self.stop_button = rumps.MenuItem(
            title=self.config["stop"], callback=self.stop_timer)
        self.app.menu = [self.start_pause_button, self.start_pause_break_button, self.stop_button]

    def set_up_menu(self):
        self.timer.stop()
        self.timer.count = 0
        self.app.title = "🍅"

    def on_tick(self, sender):
        time_left = sender.end - sender.count
        mins = time_left // 60 if time_left >= 0 else time_left // 60 + 1
        secs = time_left % 60 if time_left >= 0 else (-1 * time_left) % 60
        # TODO: Send different notification if on break
        if mins == 0 and time_left < 0:
            rumps.notification(
                title=self.config["app_name"],
                subtitle=self.config["timer_end_message"],
                message='')
            self.stop_timer()
            self.stop_button.set_callback(None)
        else:
            # TODO: Fix this to not send halfway notification if on break, e.g., sender.end != sender.break_interval
            if sender.count > 0 and sender.end / sender.count == 2:
                rumps.notification(
                    title=self.config["app_name"],
                    subtitle=self.config["halfway_message"],
                    message='')
            self.stop_button.set_callback(self.stop_timer)
            self.app.title = '{:2d}:{:02d}'.format(mins, secs)
        sender.count += 1

    def start_timer(self, sender):
        if sender.title == self.config["start"] or sender.title == self.config["continue"]:
            if sender.title == self.config["start"]:
                self.timer.count = 0
                self.timer.end = self.interval
            sender.title = self.config["pause"]
            self.timer.start()
        elif sender.title == self.config["start_break"] or sender.title == self.config["continue_break"]:
            if sender.title == self.config["start_break"]:
                self.timer.count = 0
                self.timer.end = self.break_interval
            sender.title = self.config["pause_break"]
            self.timer.start()
        else:
            sender.title = self.config["continue"]
            self.timer.stop()

    def stop_timer(self, sender):
        # TODO: Update this to work differently if break
        self.set_up_menu()
        self.stop_button.set_callback(None)
        self.start_pause_button.title = self.config["start"]

    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = PomodoroApp()
    app.run()
