import time

class PomodoroTimer:
    def __init__(self, work_time=25*60, break_time=5*60):
        self.work_time = work_time
        self.break_time = break_time
        self.start_time = time.time()
        self.is_break = False
        self.cycle_count = 0

    def update(self):
        # check if you need to switch settings
        elapsed = time.time() - self.start_time
        current_duration = self.break_time if self.is_break else self.work_time

        if elapsed >= current_duration:
            self.is_break = not self.is_break
            self.start_time = time.time()
            if not self.is_break:
                self.cycle_count += 1

    def is_break_time(self):
        self.update()
        return self.is_break

    def get_time_remaining(self):
        elapsed = time.time() - self.start_time
        current_duration = self.break_time if self.is_break else self.work_time
        return max(0, current_duration - elapsed)

    def get_status_string(self):
        remaining = self.get_time_remaining()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        period = "BREAK" if self.is_break else "WORK"
        return f"{period}: {minutes:02d}:{seconds:02d}"

    def set_times(self, work_minutes, break_minutes):
        self.work_time = work_minutes * 60
        self.break_time = break_minutes * 60