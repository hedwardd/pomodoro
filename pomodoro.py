import rumps

CONFIG = {
    "app_name": "Pomodoro Remix",
    "start1": "40 min",
    "start2": "30 min",
    "start3": "15 min",
    "pause": "Pause Session",
    "continue": "Continue Session",
    "stop": "Stop Timer",
    "timer_end_message": "Time is up! Take a break :)",
    "break_menu": "Break",
    "start_break1": "10 min",
    "start_break2": " 5 min",
    "pause_break": "Pause Break",
    "continue_break": "Continue Break",
    "stop_break": "Stop Break",
    "break_end_message": "Break's up. Time to get back to it :)",
    "halfway_message": "Halfway there!",
    "overtime_message": "Wrap it up! You're {:2d} minutes over",
    "custom_input_button_label": "Custom",
    "interval1": 2400,
    "interval2": 1800,
    "interval3": 900,
    "break_interval1": 600,
    "break_interval2": 300,
    "overtime_interval": 300,
    # "interval1": 10,
    # "interval2": 5,
    # "break_interval1": 8,
    # "break_interval2": 4,
    # "overtime_interval": 5,
}


def minutes_for_timer(seconds):
    return seconds // 60 if seconds >= 0 else (-1 * seconds) // 60


def seconds_for_timer(seconds):
    return seconds % 60 if seconds >= 0 else (-1 * seconds) % 60


def formatted_time_from_seconds(seconds):
    mins = minutes_for_timer(seconds)
    secs = seconds_for_timer(seconds)
    return '{:2d}:{:02d}'.format(mins, secs) if seconds >= 0 else '(+{:2d}:{:02d} )'.format(mins, secs)


def get_formatted_time_for_mode(seconds_left, is_break):
    formatted_time = formatted_time_from_seconds(seconds_left)
    return formatted_time if not is_break else "🧘‍♂️" + formatted_time + "🧘‍♀️"


def should_send_timeup_message(time_left):
    return time_left == 0


def should_send_halfway_message(interval, elapsed, is_break):
    return elapsed > 0 and interval / elapsed == 2 and not is_break


def should_send_overtime_message(overtime_interval, time_left):
    return time_left < 0 and time_left % overtime_interval == 0


INITIAL_STATE = {
    "timer_state": "stopped",
    "elapsed": 0,
    "is_break": False,
    "interval": CONFIG["interval1"],
}


class PomodoroApp(object):
    def __init__(self):
        self.config = CONFIG
        self.state = INITIAL_STATE.copy()
        # {
        #     "timer_state": "stopped",
        #     "elapsed": 0,
        #     "is_break": False,
        #     "interval": None,
        # }

        self.app = rumps.App(
            self.config["app_name"],
            quit_button=None,
        )
        self.timer = rumps.Timer(self.on_tick, 1)

        self.session_submenu = rumps.MenuItem(title="Start Session")
        self.session_submenu.add(rumps.MenuItem(
            title=self.config["start1"],
            callback=self.handle_start_button(self.config["interval1"])
        ))
        self.session_submenu.add(rumps.MenuItem(
            title=self.config["start2"],
            callback=self.handle_start_button(self.config["interval2"])
        ))
        self.session_submenu.add(rumps.MenuItem(
            title=self.config["start3"],
            callback=self.handle_start_button(self.config["interval3"])
        ))
        self.session_submenu.add(rumps.MenuItem(
            title=self.config["custom_input_button_label"],
            callback=self.handle_custom_length_button(False),
        ))
        self.break_submenu = rumps.MenuItem(title="Start Break")
        self.break_submenu.add(rumps.MenuItem(
            title=self.config["start_break1"],
            callback=self.handle_start_button(
                self.config["break_interval1"], True)
        ))
        self.break_submenu.add(rumps.MenuItem(
            title=self.config["start_break2"],
            callback=self.handle_start_button(
                self.config["break_interval2"], True)
        ))
        self.break_submenu.add(rumps.MenuItem(
            title=self.config["custom_input_button_label"],
            callback=self.handle_custom_length_button(True),
        ))

        self.input_window = rumps.Window(
            title='Custom Session',
            message='Enter the duration in minutes',
            default_text='',
            ok='Start session',
            cancel='Cancel',
            dimensions=(150, 100),
        )

        self.update_title()
        self.update_menu()

    def open_custom_input_window(self, is_break: bool = False):
        if is_break == True:
            self.input_window.title = 'Custom Break'
            self.input_window.ok = 'Start break'
        else:
            self.input_window.title = 'Custom Session'
            self.input_window.ok = 'Start session'

        response = self.input_window.run()  # blocking
        # if clicked start button and input is valid
        if response.clicked == 1 and response.text.isdigit():
            self.start_timer(int(response.text) * 60, is_break)
        else:
            self.input_window.close()

    def start_timer(self, interval: int, is_break: bool = False):
        self.state["timer_state"] = "running"
        self.state["interval"] = interval
        self.state["is_break"] = is_break
        self.update_menu()
        self.timer.start()

    def pause_timer(self):
        self.state["timer_state"] = "paused"
        self.update_menu()
        self.timer.stop()

    def resume_timer(self):
        self.state["timer_state"] = "running"
        self.update_menu()
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()
        self.state = INITIAL_STATE.copy()
        self.update_title()
        self.update_menu()

    def get_title(self):
        timer_state = self.state["timer_state"]
        if timer_state == "stopped":
            return "🍅"
        time_left = self.state["interval"] - self.state["elapsed"]
        is_break = self.state["is_break"]
        return get_formatted_time_for_mode(time_left, is_break)

    def update_title(self):
        self.app.title = self.get_title()

    def handle_start_button(self, interval: int, is_break: bool = False):
        return (lambda _: self.start_timer(interval, is_break))

    def handle_custom_length_button(self, is_break: bool = False):
        return (lambda _: self.open_custom_input_window(is_break))

    def handle_pause_button(self, _):
        self.pause_timer()

    def handle_resume_button(self, _):
        self.resume_timer()

    def handle_stop_button(self, _):
        self.stop_timer()

    def update_menu(self):
        self.app.menu.clear()
        timer_state = self.state["timer_state"]
        is_break = self.state["is_break"]
        mode = "Session" if not is_break == True else "Break"
        if timer_state == "stopped":
            self.app.menu = [self.session_submenu, self.break_submenu]
        elif timer_state == "running":
            pause_button = rumps.MenuItem(
                title="Pause " + mode,
                callback=self.handle_pause_button
            )
            stop_button = rumps.MenuItem(
                title="Stop " + mode,
                callback=self.handle_stop_button
            )
            self.app.menu = [pause_button, stop_button]
        elif timer_state == "paused":
            resume_button = rumps.MenuItem(
                title="Resume " + mode,
                callback=self.handle_resume_button
            )
            stop_button = rumps.MenuItem(
                title="Stop " + mode,
                callback=self.handle_stop_button
            )
            self.app.menu = [resume_button, stop_button]
        self.app.menu.add(rumps.MenuItem(
            title="Quit",
            callback=rumps.rumps.quit_application
        ))

    def handle_notifications(self):
        elapsed = self.state["elapsed"]
        interval = self.state["interval"]
        is_break = self.state["is_break"]
        overtime_interval = self.config["overtime_interval"]
        difference_in_seconds = interval - elapsed
        minutes_overtime = minutes_for_timer(difference_in_seconds)
        noti_message = ""
        play_sound = False
        # Send notification if time is up
        if should_send_timeup_message(difference_in_seconds):
            noti_message = self.config["timer_end_message"] if not is_break else self.config["break_end_message"]
            play_sound = True
        # Send halfway notification if not on break
        elif should_send_halfway_message(interval, elapsed, is_break):
            noti_message = self.config["halfway_message"]
        # Send overtime notification if over by __ minutes
        elif should_send_overtime_message(overtime_interval, difference_in_seconds):
            noti_message = self.config["overtime_message"].format(
                minutes_overtime)
            play_sound = True

        if noti_message != "":
            rumps.notification(
                title=CONFIG["app_name"],
                subtitle=noti_message,
                message='',
                sound=play_sound,
            )

    def on_tick(self, sender):
        # Update title
        self.update_title()

        # Send any notifications
        self.handle_notifications()

        self.state["elapsed"] += 1

    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = PomodoroApp()
    app.run()
