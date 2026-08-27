from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App


DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
TODAY = DAYS[date.today().weekday()]


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self._update_stats()
        self._load_today_plan()

    def _update_stats(self):
        app = App.get_running_app()
        stats = app.db.get_workout_stats()
        latest = app.db.get_latest_body_metric()

        self.ids.total_workouts.text = str(stats["total_workouts"])
        self.ids.weekly_workouts.text = str(stats["workouts_this_week"])
        self.ids.monthly_minutes.text = str(stats["monthly_minutes"])
        self.ids.active_days.text = str(stats["active_days_this_month"])
        self.ids.monthly_distance.text = f"{stats['monthly_distance']}km"

        if latest and latest.get("weight"):
            self.ids.latest_weight.text = f"{latest['weight']}{latest.get('weight_unit', 'kg')}"
        else:
            self.ids.latest_weight.text = "--"

    def _load_today_plan(self):
        app = App.get_running_app()
        exercises = app.db.get_plan_exercises_for_day(TODAY)
        container = self.ids.today_plan_container
        container.clear_widgets()

        if not exercises:
            container.add_widget(Label(
                text="No plan for today",
                font_size=dp(12),
                color=(0.48, 0.45, 0.41, 1),
                size_hint_y=None,
                height=dp(30),
            ))
            return

        for ex in exercises:
            row = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
            row.add_widget(Label(
                text=ex["exercise_name"],
                font_size=dp(12),
                halign="left",
                size_hint_x=0.6,
                color=(0.949, 0.929, 0.886, 1),
            ))
            row.add_widget(Label(
                text=f"{ex['sets']}×{ex['reps']}",
                font_size=dp(11),
                size_hint_x=0.3,
                color=(0.658, 0.631, 0.588, 1),
            ))
            container.add_widget(row)

    def show_1rm_calculator(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        content.add_widget(Label(
            text="1RM Calculator",
            font_size=dp(18),
            bold=True,
            size_hint_y=None,
            height=dp(32),
        ))

        content.add_widget(Label(
            text="Weight (kg)",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(24),
            halign="left",
        ))
        weight_input = TextInput(
            text="0",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            input_filter="float",
            multiline=False,
            halign="center",
        )
        content.add_widget(weight_input)

        content.add_widget(Label(
            text="Reps",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(24),
            halign="left",
        ))
        reps_input = TextInput(
            text="10",
            font_size=dp(16),
            size_hint_y=None,
            height=dp(40),
            input_filter="int",
            multiline=False,
            halign="center",
        )
        content.add_widget(reps_input)

        result_label = Label(
            text="Estimated 1RM: --",
            font_size=dp(16),
            bold=True,
            color=(0.478, 0.62, 0.435, 1),
            size_hint_y=None,
            height=dp(32),
        )
        content.add_widget(result_label)

        def calculate(*args):
            try:
                w = float(weight_input.text)
                r = int(reps_input.text)
                if r <= 0:
                    return
                if r == 1:
                    e1rm = w
                else:
                    e1rm = w * (1 + r / 30)
                result_label.text = f"Estimated 1RM: {e1rm:.1f}kg"
            except ValueError:
                result_label.text = "Enter valid numbers"

        calc_btn = Button(
            text="Calculate",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(44),
            background_color=(0.435, 0.545, 0.639, 1),
        )
        calc_btn.bind(on_press=calculate)
        content.add_widget(calc_btn)

        close_btn = Button(
            text="Close",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(44),
        )
        content.add_widget(close_btn)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.8, 0.7),
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
