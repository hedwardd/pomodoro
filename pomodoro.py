import rumps
class PomodoroApp(object):
    def __init__(self):
        self.config = {
            "app_name": "Pomodoro Remix",
            "start": "Start Timer",
            "pause": "Pause Timer",
            "continue": "Continue Timer",
            "stop": "Stop Timer",
            "timer_end_message": "Time is up! Take a break :)",
            "break_menu": "Break",
            "start_break": "Start Break",
            "pause_break": "Pause Break",
            "continue_break": "Continue Break",
            "stop_break": "Stop Break",
            "break_end_message": "Break is up. Time to get back to it :)",
            "halfway_message": "Halfway there!",
            # "interval": 1800,
            "interval": 10,
            # "break_interval": 600
            "break_interval": 8
        }

        # Rumps Objects
        self.app = rumps.App(self.config["app_name"])
        self.timer = rumps.Timer(self.on_tick, 1)

        # Menu Setup
        self.start_pause_timer = rumps.MenuItem(
            title=self.config["start"], callback=self.start_timer)
        self.start_pause_break = rumps.MenuItem(
            title=self.config["start_break"], callback=self.start_timer)
        self.stop_button = rumps.MenuItem(
            title=self.config["stop"], callback=None)
        self.break_submenu = rumps.MenuItem(title=self.config["break_menu"])
        self.break_submenu.add(self.start_pause_break)

        self.app.menu = [self.start_pause_timer, self.stop_button, self.break_submenu]

        # Values/Attributes
        self.interval = self.config["interval"]
        self.break_interval = self.config["break_interval"]
        self.is_break = False

        # Initiate
        self.set_up_menu()

    def set_up_menu(self):
        self.timer.stop()
        self.timer.count = 0
        self.app.title = "🍅"

    def on_tick(self, sender):
        time_left = sender.end - sender.count
        mins = time_left // 60 if time_left >= 0 else time_left // 60 + 1
        secs = time_left % 60 if time_left >= 0 else (-1 * time_left) % 60
        if time_left == 0:
            # Send different notification if on break
            noti_message = self.config["timer_end_message"] if not self.is_break else self.config["break_end_message"]
            rumps.notification(
                title=self.config["app_name"],
                subtitle=noti_message,
                message='')
        else:
            # Don't send halfway notification if on break
            if sender.count > 0 and sender.end / sender.count == 2 and not self.is_break:
                rumps.notification(
                    title=self.config["app_name"],
                    subtitle=self.config["halfway_message"],
                    message='')
            formatted_time = '{:2d}:{:02d}'.format(mins, secs) if time_left >= 0 else '({:2d}:{:02d} )'.format(mins, secs) 
            self.app.title = formatted_time if not self.is_break else "🧘‍♂️" + formatted_time + "🧘‍♀️"
        sender.count += 1

    # TODO: Separate button text updates from timer update. I.e., separate actions
    def start_timer(self, sender):
        self.stop_button.set_callback(self.stop_timer)
        if sender.title == self.config["start"] or sender.title == self.config["continue"]:
            if sender.title == self.config["start"]:
                self.timer.count = 0
                self.timer.end = self.interval
                self.is_break = False
            sender.title = self.config["pause"]
            self.timer.start()
        elif sender.title == self.config["start_break"] or sender.title == self.config["continue_break"]:
            if sender.title == self.config["start_break"]:
                self.timer.count = 0
                self.timer.end = self.break_interval
                self.is_break = True
            sender.title = self.config["pause_break"]
            self.timer.start()
        else:
            sender.title = self.config["continue"]
            self.timer.stop()

    def stop_timer(self, sender):
        self.set_up_menu()
        self.stop_button.set_callback(None)
        self.start_pause_timer.title = self.config["start"]

    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = PomodoroApp()
    app.run()
