from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App
from datetime import date, timedelta
import calendar


class CalendarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_year = date.today().year
        self.current_month = date.today().month
        self.workout_dates = set()

    def on_enter(self):
        self._load_workouts()
        self._build_calendar()

    def _load_workouts(self):
        app = App.get_running_app()
        self.workout_dates = set()
        workouts = app.db.get_workout_dates_for_month(self.current_year, self.current_month)
        for w in workouts:
            self.workout_dates.add(w["date"])

    def _build_calendar(self):
        self.ids.calendar_grid.clear_widgets()
        self.ids.month_label.text = calendar.month_name[self.current_month] + " " + str(self.current_year)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day_name in days:
            lbl = Label(
                text=day_name,
                font_size=dp(11),
                bold=True,
                color=(0.658, 0.631, 0.588, 1)
            )
            self.ids.calendar_grid.add_widget(lbl)

        cal = calendar.monthcalendar(self.current_year, self.current_month)
        today = date.today()

        for week in cal:
            for day in week:
                if day == 0:
                    self.ids.calendar_grid.add_widget(Label(text=""))
                else:
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    is_today = (day == today.day and self.current_month == today.month and self.current_year == today.year)
                    has_workout = date_str in self.workout_dates

                    if has_workout and is_today:
                        bg = (0.29, 0.55, 0.35, 1)
                    elif has_workout:
                        bg = (0.478, 0.62, 0.435, 1)
                    elif is_today:
                        bg = (0.435, 0.545, 0.639, 1)
                    else:
                        bg = (0.33, 0.31, 0.27, 1)

                    btn = Button(
                        text=str(day),
                        font_size=dp(12),
                        background_color=bg,
                        color=(1, 1, 1, 1),
                        bold=is_today
                    )
                    d = day
                    btn.bind(on_press=lambda inst, dd=d: self._on_day_press(dd))
                    self.ids.calendar_grid.add_widget(btn)

        self._load_day_summary(today.day)

    def _on_day_press(self, day):
        date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        self._load_day_summary(day)

    def _load_day_summary(self, day):
        date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
        self.ids.selected_date.text = f"{calendar.month_name[self.current_month]} {day}, {self.current_year}"

        app = App.get_running_app()
        workouts = app.db.get_workouts_for_date(date_str)

        container = self.ids.workout_list_container
        container.clear_widgets()

        if not workouts:
            container.add_widget(Label(
                text="No workouts on this day",
                font_size=dp(12),
                color=(0.48, 0.45, 0.41, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for w in workouts:
            row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

            info = BoxLayout(orientation="vertical", size_hint_x=0.6)
            name_text = w.get("name", "Workout")
            duration = w.get("duration", 0) or 0
            mins = duration // 60
            info.add_widget(Label(
                text=name_text,
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(24)
            ))
            info.add_widget(Label(
                text=f"{mins} min",
                font_size=dp(11),
                halign="left",
                size_hint_y=None,
                height=dp(18),
                color=(0.658, 0.631, 0.588, 1)
            ))
            row.add_widget(info)

            completed = w.get("completed", 0)
            if completed:
                status_label = Label(
                    text="(Completed)",
                    font_size=dp(11),
                    bold=True,
                    color=(0.478, 0.62, 0.435, 1),
                    size_hint_x=0.3
                )
            else:
                status_label = Label(
                    text="(In Progress)",
                    font_size=dp(11),
                    bold=True,
                    color=(0.788, 0.635, 0.294, 1),
                    size_hint_x=0.3
                )
            row.add_widget(status_label)

            container.add_widget(row)

    def prev_month(self):
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self._load_workouts()
        self._build_calendar()

    def next_month(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self._load_workouts()
        self._build_calendar()
