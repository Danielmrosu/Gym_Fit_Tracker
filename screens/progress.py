from datetime import date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.app import App


class BarChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bar_data = []
        self.bar_color = (0.435, 0.545, 0.639, 1)
        self.grid_lines = 4
        self.bind(size=self._draw, pos=self._draw)

    def set_data(self, data, color=None):
        self.bar_data = data
        if color:
            self.bar_color = color
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        if not self.bar_data or self.width <= 0 or self.height <= 0:
            return

        max_val = max(d["count"] for d in self.bar_data) if self.bar_data else 1
        if max_val == 0:
            max_val = 1

        n = len(self.bar_data)
        padding_x = dp(20)
        padding_y = dp(8)
        bar_spacing = dp(2)
        available_width = self.width - padding_x * 2
        bar_width = max(dp(6), (available_width - bar_spacing * (n - 1)) / n)
        bottom_label_height = dp(14)
        bar_radius = [dp(3), dp(3), 0, 0]
        chart_height = self.height - bottom_label_height - padding_y * 2

        with self.canvas:
            Color(0.2, 0.18, 0.16, 1)
            for i in range(self.grid_lines + 1):
                y = self.y + bottom_label_height + padding_y + (chart_height * i / self.grid_lines)
                Line(points=[self.x + padding_x, y, self.x + self.width - padding_x, y],
                     width=1, dash_length=4, dash_offset=4)

            y_label = self.y + chart_height + padding_y
            lbl = Label(text=f"{int(max_val)}", font_size=dp(8), size=(dp(20), dp(12)))
            lbl.texture_update()
            lbl.pos = (self.x, y_label)
            lbl.size = (dp(20), dp(12))

        for i, d in enumerate(self.bar_data):
            bar_height = (d["count"] / max_val) * chart_height
            x = self.x + padding_x + i * (bar_width + bar_spacing)
            y = self.y + bottom_label_height + padding_y

            with self.canvas:
                Color(*self.bar_color)
                RoundedRectangle(pos=(x, y), size=(bar_width, bar_height), radius=bar_radius)

                Color(0.48, 0.45, 0.41, 1)
                label_text = d.get("label", "")[:3]
                lbl = Label(text=label_text, font_size=dp(8), size=(bar_width, bottom_label_height))
                lbl.texture_update()
                lbl.pos = (x, self.y)
                lbl.size = (bar_width, bottom_label_height)


class LineChart(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.line_data = []
        self.line_color = (0.757, 0.267, 0.235, 1)
        self.grid_lines = 4
        self.bind(size=self._draw, pos=self._draw)

    def set_data(self, data, color=None):
        self.line_data = data
        if color:
            self.line_color = color
        self._draw()

    def _draw(self, *args):
        self.canvas.clear()
        if not self.line_data or self.width <= 0 or self.height <= 0:
            return

        values = [d["count"] for d in self.line_data]
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            max_val = min_val + 1

        n = len(self.line_data)
        padding_x = dp(20)
        padding_y = dp(8)
        bottom_label_height = dp(14)
        chart_height = self.height - bottom_label_height - padding_y * 2
        chart_width = self.width - padding_x * 2

        with self.canvas:
            Color(0.2, 0.18, 0.16, 1)
            for i in range(self.grid_lines + 1):
                y = self.y + bottom_label_height + padding_y + (chart_height * i / self.grid_lines)
                Line(points=[self.x + padding_x, y, self.x + self.width - padding_x, y],
                     width=1, dash_length=4, dash_offset=4)

        points = []
        for i, d in enumerate(self.line_data):
            x = self.x + padding_x + (chart_width * i / (n - 1)) if n > 1 else self.x + padding_x + chart_width / 2
            y = self.y + bottom_label_height + padding_y + ((d["count"] - min_val) / (max_val - min_val)) * chart_height
            points.extend([x, y])

        if len(points) >= 4:
            with self.canvas:
                Color(*self.line_color)
                Line(points=points, width=dp(2), cap="round", joint="round")

        label_step = max(1, n // 5)
        for i, d in enumerate(self.line_data):
            if i % label_step == 0 or i == n - 1:
                x = self.x + padding_x + (chart_width * i / (n - 1)) if n > 1 else self.x + padding_x + chart_width / 2
                with self.canvas:
                    Color(0.48, 0.45, 0.41, 1)
                    lbl = Label(text=d.get("label", "")[:5], font_size=dp(8), size=(dp(30), dp(12)))
                    lbl.texture_update()
                    lbl.pos = (x - dp(15), self.y)
                    lbl.size = (dp(30), dp(12))


class ProgressScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_tab = "week"

    def on_enter(self):
        self.ids.today_date.text = date.today().strftime("%A, %B %d, %Y")
        self._load_stats()
        self._load_workout_chart()
        self._load_muscle_chart()
        self._load_weight_chart()
        self._load_duration_chart()
        self._load_volume_chart()
        self._load_measurements_chart()
        self._load_prs()
        self._load_personal_records()
        self._load_streak()
        self._load_achievements()
        self._highlight_tab()

    def _load_stats(self):
        app = App.get_running_app()
        total = app.db.get_workout_stats()
        self.ids.total_workouts.text = f"All Time: {total['total_workouts']}"

        period = app.db.get_workout_stats_for_period(self.active_tab)
        self.ids.period_workouts.text = f"Workouts: {period['workouts_count']}"
        self.ids.period_minutes.text = f"Minutes: {period['total_minutes']}"
        self.ids.period_active.text = f"Active Days: {period['active_days']}"

        run_stats = app.db.get_run_stats_for_period(self.active_tab)
        calories = app.db.get_calories_for_period(self.active_tab)
        if run_stats["run_count"] > 0:
            self.ids.period_distance.text = f"Distance: {run_stats['total_distance']}km"
            self.ids.period_pace.text = f"Avg Pace: {run_stats['avg_pace']:.1f} min/km"
        else:
            self.ids.period_distance.text = ""
            self.ids.period_pace.text = ""

        if calories > 0:
            self.ids.period_calories.text = f"Calories: {calories:.0f}cal"
        else:
            self.ids.period_calories.text = ""

    def _load_workout_chart(self):
        app = App.get_running_app()
        freq = app.db.get_workout_frequency(self.active_tab)
        chart_data = []
        for item in freq:
            if self.active_tab == "year":
                label = item["month"][-2:]
            else:
                label = item["date"][-2:]
            chart_data.append({"label": label, "count": item["count"]})
        self.ids.workout_chart.set_data(chart_data)
        self.ids.workout_chart_title.text = "Workouts" if chart_data else "No workouts this period"

    def _load_muscle_chart(self):
        app = App.get_running_app()
        freq = app.db.get_muscle_group_frequency(self.active_tab)
        chart_data = []
        for item in freq:
            chart_data.append({"label": item["muscle_group"][:4], "count": item["count"]})
        self.ids.muscle_chart.set_data(chart_data, color=(0.435, 0.545, 0.639, 1))
        self.ids.muscle_chart_title.text = "Muscles Trained" if chart_data else "No data"

    def _load_weight_chart(self):
        app = App.get_running_app()
        history = app.db.get_weight_history(limit=10)
        history = list(reversed(history))
        chart_data = []
        for item in history:
            chart_data.append({"label": item["date"][-5:], "count": item["weight"]})
        self.ids.weight_chart.set_data(chart_data, color=(0.757, 0.267, 0.235, 1))
        self.ids.weight_chart_title.text = "Body Weight (kg)" if chart_data else "No weight data"

    def _load_duration_chart(self):
        app = App.get_running_app()
        trend = app.db.get_workout_duration_trend(limit=10)
        trend = list(reversed(trend))
        chart_data = []
        for item in trend:
            chart_data.append({"label": item["date"][-5:], "count": item["duration"]})
        self.ids.duration_chart.set_data(chart_data, color=(0.435, 0.545, 0.639, 1))
        self.ids.duration_chart_title.text = "Duration (min)" if chart_data else "No duration data"

    def _load_volume_chart(self):
        app = App.get_running_app()
        trend = app.db.get_volume_trend(limit=10)
        trend = list(reversed(trend))
        chart_data = []
        for item in trend:
            chart_data.append({"label": item["date"][-5:], "count": item["volume"]})
        self.ids.volume_chart.set_data(chart_data, color=(0.478, 0.62, 0.435, 1))
        self.ids.volume_chart_title.text = "Volume (kg)" if chart_data else "No volume data"

    def _load_measurements_chart(self):
        app = App.get_running_app()
        data = app.db.get_body_measurements_trend(limit=8)
        data = list(reversed(data))
        container = self.ids.measurements_container
        container.clear_widgets()
        if not data:
            container.add_widget(Label(
                text="No measurements logged",
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(24),
            ))
            return

        header = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(4))
        for txt in ["Date", "Chest", "Waist", "Hips", "Bicep", "Thigh"]:
            header.add_widget(Label(text=txt, font_size=dp(10), bold=True, color=(0.7, 0.7, 0.7, 1)))
        container.add_widget(header)

        for m in data:
            row = BoxLayout(size_hint_y=None, height=dp(22), spacing=dp(4))
            for key, default in [("date", ""), ("chest", "--"), ("waist", "--"), ("hips", "--"), ("biceps_left", "--"), ("thighs_left", "--")]:
                val = m.get(key, default)
                if key == "date":
                    val = str(val)[-5:]
                elif val and val != "--":
                    val = f"{val:.0f}"
                row.add_widget(Label(text=str(val), font_size=dp(10), color=(0.8, 0.8, 0.8, 1)))
            container.add_widget(row)

    def _load_prs(self):
        app = App.get_running_app()
        leaders = app.db.get_estimated_1rm_leaders(5)
        container = self.ids.pr_container
        container.clear_widgets()
        if not leaders:
            container.add_widget(Label(
                text="No records yet",
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(28),
            ))
            return
        for i, pr in enumerate(leaders):
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))

            rank_box = BoxLayout(size_hint_x=None, width=dp(28), size_hint_y=None, height=dp(28))
            with rank_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle, Ellipse
                if i == 0:
                    Color(0.788, 0.635, 0.294, 1)
                else:
                    Color(0.133, 0.122, 0.106, 1)
                    Color(0.2, 0.18, 0.16, 1)
                Ellipse(pos=rank_box.pos, size=rank_box.size)
            rank_box.bind(pos=self._update_rank_bg, size=self._update_rank_bg)

            rank_label = Label(
                text="★" if i == 0 else str(i + 1),
                font_size=dp(11),
                bold=True,
                color=(0.133, 0.122, 0.106, 1) if i == 0 else (0.48, 0.45, 0.41, 1),
            )
            rank_box.add_widget(rank_label)
            row.add_widget(rank_box)

            info_box = BoxLayout(orientation="vertical", size_hint_x=0.55)
            info_box.add_widget(Label(
                text=pr["name"],
                font_size=dp(12),
                halign="left",
                size_hint_y=None,
                height=dp(18),
                color=(0.949, 0.929, 0.886, 1),
            ))
            info_box.add_widget(Label(
                text=f"from {pr['weight']}kg × {pr['reps']} on {pr['date'][-5:]}",
                font_size=dp(10),
                halign="left",
                size_hint_y=None,
                height=dp(16),
                color=(0.658, 0.631, 0.588, 1),
            ))
            row.add_widget(info_box)

            rm_label = Label(
                text=f"{pr['est_1rm']:.0f}",
                font_size=dp(16),
                bold=True,
                size_hint_x=0.2,
                color=(0.757, 0.267, 0.235, 1),
            )
            row.add_widget(rm_label)

            unit_label = Label(
                text="kg",
                font_size=dp(10),
                size_hint_x=0.1,
                color=(0.658, 0.631, 0.588, 1),
            )
            row.add_widget(unit_label)

            container.add_widget(row)

    def _load_personal_records(self):
        app = App.get_running_app()
        prs = app.db.get_all_prs()
        container = self.ids.get("personal_records_container")
        if not container:
            return
        container.clear_widgets()

        if not prs:
            container.add_widget(Label(
                text="No personal records yet",
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(28),
            ))
            return

        seen = {}
        for pr in prs:
            ex_id = pr["exercise_id"]
            if ex_id not in seen:
                seen[ex_id] = pr

        for ex_id, pr in list(seen.items())[:10]:
            row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))

            row.add_widget(Label(
                text=pr["exercise_name"],
                font_size=dp(12),
                halign="left",
                size_hint_x=0.45,
                color=(0.949, 0.929, 0.886, 1),
            ))

            row.add_widget(Label(
                text=f"{pr['value']:.1f}kg x {pr['reps']}",
                font_size=dp(12),
                bold=True,
                size_hint_x=0.3,
                color=(0.788, 0.635, 0.294, 1),
            ))

            row.add_widget(Label(
                text=pr["date"][-5:],
                font_size=dp(10),
                size_hint_x=0.2,
                color=(0.658, 0.631, 0.588, 1),
            ))

            container.add_widget(row)

    def _update_rank_bg(self, instance, value):
        pass

    def _load_streak(self):
        app = App.get_running_app()
        dates = app.db.get_workout_dates()
        if not dates:
            self.ids.streak_text.text = "Current: 0 days | Best: 0 days"
            return

        current = 0
        check = date.today()
        date_set = set(dates)
        while check.isoformat() in date_set:
            current += 1
            check -= timedelta(days=1)

        best = app.db.get_longest_streak()
        self.ids.streak_text.text = f"Current: {current} days | Best: {best} days"

    def _load_achievements(self):
        app = App.get_running_app()
        total = app.db.get_total_workouts()
        total_sets = app.db.get_total_sets()
        best_streak = app.db.get_longest_streak()
        dates = app.db.get_workout_dates()
        prs = app.db.get_all_personal_records()

        achievements = []

        milestones = [
            (1, "First Workout", "Completed your first workout!"),
            (5, "Getting Started", "Completed 5 workouts"),
            (10, "Dedicated", "Completed 10 workouts"),
            (25, "Committed", "Completed 25 workouts"),
            (50, "Beast Mode", "Completed 50 workouts"),
            (100, "Centurion", "Completed 100 workouts"),
        ]
        for threshold, name, desc in milestones:
            if total >= threshold:
                achievements.append((name, desc))

        streak_milestones = [
            (3, "On a Roll", "3 day streak"),
            (7, "Week Warrior", "7 day streak"),
            (14, "Two Week Champion", "14 day streak"),
            (30, "Monthly Machine", "30 day streak"),
        ]
        for threshold, name, desc in streak_milestones:
            if best_streak >= threshold:
                achievements.append((name, desc))

        if total_sets >= 100:
            achievements.append(("Century of Sets", f"{total_sets} total sets completed"))
        if total_sets >= 500:
            achievements.append(("Set Monster", f"{total_sets} total sets completed"))
        if len(prs) >= 5:
            achievements.append(("PR Collector", f"{len(prs)} personal records"))

        if dates:
            first = min(dates)
            days_since = (date.today() - date.fromisoformat(first)).days
            if days_since >= 30:
                achievements.append(("Monthly Member", f"{days_since} days since first workout"))
            if days_since >= 90:
                achievements.append(("Quarterly Legend", f"{days_since} days since first workout"))

        container = self.ids.achievements_container
        container.clear_widgets()
        if not achievements:
            container.add_widget(Label(
                text="Complete workouts to earn badges!",
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(28),
            ))
            return

        for name, desc in achievements:
            container.add_widget(Label(
                text=f"★ {name} — {desc}",
                font_size=dp(12),
                color=(0.788, 0.635, 0.294, 1),
                size_hint_y=None,
                height=dp(24),
                halign="left",
            ))

    def switch_tab(self, tab):
        self.active_tab = tab
        self._highlight_tab()
        self._load_stats()
        self._load_workout_chart()
        self._load_muscle_chart()

    def _highlight_tab(self):
        tabs = {"week": 0, "month": 1, "year": 2}
        for name, idx in tabs.items():
            btn = self.ids.get(f"tab_{name}")
            if not btn:
                continue
            if name == self.active_tab:
                btn.background_color = (0.757, 0.267, 0.235, 1)
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_color = (0.18, 0.168, 0.15, 1)
                btn.color = (0.48, 0.45, 0.41, 1)


from kivy.uix.popup import Popup


class PRPopup(Popup):
    def __init__(self, pr_data, **kwargs):
        super().__init__(**kwargs)
        self.title = "New Personal Record!"
        self.size_hint = (0.75, 0.5)
        self.pr_data = pr_data
        self._build_content()

    def _build_content(self):
        from kivy.app import App
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        app = App.get_running_app()
        cursor = app.db.conn.cursor()
        cursor.execute("SELECT name FROM exercises WHERE id = ?", (self.pr_data["exercise_id"],))
        row = cursor.fetchone()
        exercise_name = row["name"] if row else "Exercise"

        content.add_widget(Label(
            text="NEW PR!",
            font_size=dp(24),
            bold=True,
            color=(0.788, 0.635, 0.294, 1),
            size_hint_y=None,
            height=dp(40)
        ))

        content.add_widget(Label(
            text=exercise_name,
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))

        old_val = self.pr_data.get("old_value", 0)
        new_val = self.pr_data["value"]
        reps = self.pr_data["reps"]

        if old_val > 0:
            content.add_widget(Label(
                text=f"{old_val:.1f}kg x {self.pr_data.get('old_reps', '?')} reps",
                font_size=dp(13),
                color=(0.658, 0.631, 0.588, 1),
                size_hint_y=None,
                height=dp(24)
            ))

            arrow_label = Label(
                text="▼",
                font_size=dp(16),
                color=(0.478, 0.62, 0.435, 1),
                size_hint_y=None,
                height=dp(24)
            )
            content.add_widget(arrow_label)

        content.add_widget(Label(
            text=f"{new_val:.1f}kg x {reps} reps",
            font_size=dp(18),
            bold=True,
            color=(0.478, 0.62, 0.435, 1),
            size_hint_y=None,
            height=dp(32)
        ))

        close_btn = Button(
            text="Awesome!",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(44),
            background_color=(0.788, 0.635, 0.294, 1),
            color=(1, 1, 1, 1)
        )
        close_btn.bind(on_press=lambda x: self.dismiss())
        content.add_widget(close_btn)

        self.content = content
