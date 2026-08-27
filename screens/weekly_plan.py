from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App


DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
TODAY = DAYS[date.today().weekday()]


class WeeklyPlanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self._load_plan()

    def _load_plan(self):
        app = App.get_running_app()
        plan = app.db.get_weekly_plan()
        container = self.ids.plan_container
        container.clear_widgets()

        for day in DAYS:
            day_data = plan.get(day, {"id": None, "exercises": []})
            exercises = day_data["exercises"]
            is_today = day == TODAY

            day_card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(44) + len(exercises) * dp(30),
                padding=[dp(12), dp(8)],
                spacing=dp(4),
            )

            day_card.canvas.before.clear()
            with day_card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.133, 0.122, 0.106, 1)
                RoundedRectangle(pos=day_card.pos, size=day_card.size, radius=[dp(8)])
            day_card.bind(pos=self._update_card, size=self._update_card)

            header = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(8))

            day_label = Label(
                text=f"{day} · Today" if is_today else day,
                font_size=dp(14),
                bold=True,
                halign="left",
                size_hint_x=0.6,
                color=(0.949, 0.929, 0.886, 1) if is_today else (0.658, 0.631, 0.588, 1),
            )
            header.add_widget(day_label)

            add_btn = Button(
                text="+ Add",
                font_size=dp(11),
                size_hint_x=0.25,
                background_color=(0.18, 0.168, 0.15, 1),
                color=(0.48, 0.45, 0.41, 1),
            )
            plan_id = day_data["id"]
            add_btn.bind(on_press=lambda inst, d=day, pid=plan_id: self._add_exercise(d))
            header.add_widget(add_btn)

            day_card.add_widget(header)

            for ex in exercises:
                ex_row = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))

                ex_label = Label(
                    text=ex["exercise_name"],
                    font_size=dp(12),
                    halign="left",
                    size_hint_x=0.55,
                    color=(0.949, 0.929, 0.886, 1),
                )
                ex_row.add_widget(ex_label)

                sets_label = Label(
                    text=f"{ex['sets']}×{ex['reps']}",
                    font_size=dp(11),
                    size_hint_x=0.25,
                    color=(0.658, 0.631, 0.588, 1),
                )
                ex_row.add_widget(sets_label)

                remove_btn = Button(
                    text="X",
                    font_size=dp(10),
                    size_hint_x=0.12,
                    background_color=(0.757, 0.267, 0.235, 1),
                    color=(1, 1, 1, 1),
                )
                pe_id = ex["id"]
                remove_btn.bind(on_press=lambda inst, pid=pe_id: self._remove_exercise(pid))
                ex_row.add_widget(remove_btn)

                day_card.add_widget(ex_row)

            container.add_widget(day_card)

    def _update_card(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.133, 0.122, 0.106, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[dp(8)])

    def _add_exercise(self, day):
        popup = AddExerciseToPlanPopup(day, self._load_plan)
        popup.open()

    def _remove_exercise(self, plan_exercise_id):
        app = App.get_running_app()
        app.db.remove_exercise_from_plan(plan_exercise_id)
        self._load_plan()

    def start_today_workout(self):
        app = App.get_running_app()
        workout_id = app.db.start_workout_from_plan(TODAY)
        if workout_id:
            screen = self.manager.get_screen("active_workout")
            screen.load_workout(workout_id)
            self.manager.current = "active_workout"


class AddExerciseToPlanPopup(Popup):
    def __init__(self, day, on_add_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Add to {day}"
        self.size_hint = (0.92, 0.85)
        self.day = day
        self.on_add_callback = on_add_callback
        self.selected_exercise = None
        self.active_tab = "category"
        self.current_category = "All"
        self.current_equipment = "All"
        self.current_muscle = "All"
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(6))

        self.search_input = TextInput(
            hint_text="Search exercises...",
            size_hint_y=None,
            height=dp(38),
            font_size=dp(14),
        )
        self.search_input.bind(text=self._on_search)
        content.add_widget(self.search_input)

        tab_row = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(4))
        self.tab_category_btn = Button(text="Category", font_size=dp(11))
        self.tab_equipment_btn = Button(text="Equipment", font_size=dp(11))
        self.tab_muscle_btn = Button(text="Body Part", font_size=dp(11))
        self.tab_category_btn.bind(on_press=lambda inst: self._switch_tab("category"))
        self.tab_equipment_btn.bind(on_press=lambda inst: self._switch_tab("equipment"))
        self.tab_muscle_btn.bind(on_press=lambda inst: self._switch_tab("muscle"))
        tab_row.add_widget(self.tab_category_btn)
        tab_row.add_widget(self.tab_equipment_btn)
        tab_row.add_widget(self.tab_muscle_btn)
        content.add_widget(tab_row)

        cat_scroll = ScrollView(size_hint_y=None, height=dp(34), do_scroll_x=True, do_scroll_y=False)
        self.category_row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(4), size_hint_x=None)
        self.category_row.bind(minimum_width=self.category_row.setter('width'))
        cat_scroll.add_widget(self.category_row)
        self.cat_scroll = cat_scroll
        content.add_widget(cat_scroll)

        equip_scroll = ScrollView(size_hint_y=None, height=dp(34), do_scroll_x=True, do_scroll_y=False)
        self.equipment_row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(4), size_hint_x=None)
        self.equipment_row.bind(minimum_width=self.equipment_row.setter('width'))
        equip_scroll.add_widget(self.equipment_row)
        self.equip_scroll = equip_scroll
        content.add_widget(equip_scroll)

        muscle_scroll = ScrollView(size_hint_y=None, height=dp(34), do_scroll_x=True, do_scroll_y=False)
        self.muscle_row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(4), size_hint_x=None)
        self.muscle_row.bind(minimum_width=self.muscle_row.setter('width'))
        muscle_scroll.add_widget(self.muscle_row)
        self.muscle_scroll = muscle_scroll
        content.add_widget(muscle_scroll)

        self.scroll = ScrollView(size_hint_y=1)
        self.exercises_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
        )
        self.exercises_list.bind(minimum_height=self.exercises_list.setter("height"))
        self.scroll.add_widget(self.exercises_list)
        content.add_widget(self.scroll)

        self.config_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8), opacity=0)
        content.add_widget(self.config_row)

        self.btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        content.add_widget(self.btn_row)

        self.content = content
        self._load_filter_buttons()
        self._update_tabs()
        self._load_exercises(App.get_running_app().db.get_all_exercises())

    def _load_filter_buttons(self):
        categories = ["All", "Strength", "Bodyweight", "Cardio"]
        self.category_row.clear_widgets()
        for c in categories:
            btn = Button(text=c, font_size=dp(11), size_hint_x=None, width=dp(70))
            cat = c
            btn.bind(on_press=lambda inst, cat=cat: self._filter_by_category(cat))
            self.category_row.add_widget(btn)

        equipment = ["All", "Barbell", "Dumbbells", "Machine", "Cable", "None"]
        self.equipment_row.clear_widgets()
        for e in equipment:
            btn = Button(text=e, font_size=dp(11), size_hint_x=None, width=dp(70))
            equip = e
            btn.bind(on_press=lambda inst, equip=equip: self._filter_by_equipment(equip))
            self.equipment_row.add_widget(btn)

        muscles = ["All", "Chest", "Back", "Legs", "Shoulders", "Arms", "Core"]
        self.muscle_row.clear_widgets()
        for m in muscles:
            btn = Button(text=m, font_size=dp(11), size_hint_x=None, width=dp(70))
            muscle = m
            btn.bind(on_press=lambda inst, muscle=muscle: self._filter_by_muscle(muscle))
            self.muscle_row.add_widget(btn)

    def _switch_tab(self, tab):
        self.active_tab = tab
        self._update_tabs()

    def _update_tabs(self):
        cat_vis = self.active_tab == "category"
        equip_vis = self.active_tab == "equipment"
        muscle_vis = self.active_tab == "muscle"

        self.cat_scroll.opacity = 1 if cat_vis else 0
        self.cat_scroll.height = dp(34) if cat_vis else 0
        self.cat_scroll.size_hint_y = None
        self.equip_scroll.opacity = 1 if equip_vis else 0
        self.equip_scroll.height = dp(34) if equip_vis else 0
        self.equip_scroll.size_hint_y = None
        self.muscle_scroll.opacity = 1 if muscle_vis else 0
        self.muscle_scroll.height = dp(34) if muscle_vis else 0
        self.muscle_scroll.size_hint_y = None

        self.tab_category_btn.text = f"Category ({self.current_category})"
        self.tab_equipment_btn.text = f"Equipment ({self.current_equipment})"
        self.tab_muscle_btn.text = f"Body Part ({self.current_muscle})"

        self.tab_category_btn.background_color = (0.435, 0.545, 0.639, 1) if cat_vis else (0.18, 0.168, 0.15, 1)
        self.tab_category_btn.color = (1, 1, 1, 1) if cat_vis else (0.658, 0.631, 0.588, 1)
        self.tab_equipment_btn.background_color = (0.435, 0.545, 0.639, 1) if equip_vis else (0.18, 0.168, 0.15, 1)
        self.tab_equipment_btn.color = (1, 1, 1, 1) if equip_vis else (0.658, 0.631, 0.588, 1)
        self.tab_muscle_btn.background_color = (0.435, 0.545, 0.639, 1) if muscle_vis else (0.18, 0.168, 0.15, 1)
        self.tab_muscle_btn.color = (1, 1, 1, 1) if muscle_vis else (0.658, 0.631, 0.588, 1)

    def _filter_by_category(self, category):
        self.current_category = category
        for btn in self.category_row.children:
            if btn.text == category:
                btn.background_color = (0.757, 0.267, 0.235, 1)
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_color = (0.18, 0.168, 0.15, 1)
                btn.color = (0.658, 0.631, 0.588, 1)
        self._update_tabs()
        self._refresh_exercises()

    def _filter_by_equipment(self, equipment):
        self.current_equipment = equipment
        for btn in self.equipment_row.children:
            if btn.text == equipment:
                btn.background_color = (0.757, 0.267, 0.235, 1)
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_color = (0.18, 0.168, 0.15, 1)
                btn.color = (0.658, 0.631, 0.588, 1)
        self._update_tabs()
        self._refresh_exercises()

    def _filter_by_muscle(self, muscle):
        self.current_muscle = muscle
        for btn in self.muscle_row.children:
            if btn.text == muscle:
                btn.background_color = (0.757, 0.267, 0.235, 1)
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_color = (0.18, 0.168, 0.15, 1)
                btn.color = (0.658, 0.631, 0.588, 1)
        self._update_tabs()
        self._refresh_exercises()

    def _on_search(self, instance, text):
        self._refresh_exercises()

    def _refresh_exercises(self):
        app = App.get_running_app()
        search_text = self.search_input.text.strip() if self.search_input.text else ""
        if search_text:
            exercises = app.db.search_exercises(search_text)
        else:
            exercises = app.db.get_all_exercises()

        if self.current_category != "All":
            exercises = [e for e in exercises if e["category"] == self.current_category]
        if self.current_equipment != "All":
            equip_map = {"None": "None"}
            target = equip_map.get(self.current_equipment, self.current_equipment)
            exercises = [e for e in exercises if e["equipment"] == target]
        if self.current_muscle != "All":
            exercises = [e for e in exercises if e["muscle_group"] == self.current_muscle]

        self._load_exercises(exercises)

    def _load_exercises(self, exercises):
        self.exercises_list.clear_widgets()
        self.selected_exercise = None
        self.config_row.opacity = 0
        self.btn_row.clear_widgets()

        for ex in exercises:
            btn = Button(
                text=f"{ex['name']} ({ex['muscle_group']})",
                size_hint_y=None,
                height=dp(44),
                font_size=dp(13),
                halign="left",
                valign="middle",
                text_size=(dp(300), None),
            )
            ex_id = ex["id"]
            ex_name = ex["name"]
            btn.bind(on_press=lambda inst, eid=ex_id, ename=ex_name: self._select_exercise(eid, ename))
            self.exercises_list.add_widget(btn)

    def _select_exercise(self, exercise_id, exercise_name):
        self.selected_exercise = {"id": exercise_id, "name": exercise_name}
        self.scroll.opacity = 0
        self.search_input.opacity = 0
        self.muscle_row.opacity = 0

        self.config_row.clear_widgets()
        self.config_row.opacity = 1

        self.config_row.add_widget(Label(
            text=exercise_name,
            font_size=dp(14),
            bold=True,
            size_hint_x=0.4,
        ))

        self.sets_input = TextInput(
            text="3",
            font_size=dp(14),
            input_filter="int",
            multiline=False,
            halign="center",
            size_hint_x=0.2,
        )
        self.config_row.add_widget(self.sets_input)

        self.config_row.add_widget(Label(
            text="sets ×",
            font_size=dp(12),
            size_hint_x=0.15,
        ))

        self.reps_input = TextInput(
            text="10",
            font_size=dp(14),
            multiline=False,
            halign="center",
            size_hint_x=0.2,
        )
        self.config_row.add_widget(self.reps_input)

        self.config_row.add_widget(Label(
            text="reps",
            font_size=dp(12),
            size_hint_x=0.1,
        ))

        self.btn_row.clear_widgets()

        back_btn = Button(
            text="Back",
            font_size=dp(14),
            size_hint_x=0.35,
            background_color=(0.18, 0.168, 0.15, 1),
            color=(0.658, 0.631, 0.588, 1),
        )
        back_btn.bind(on_press=lambda inst: self._deselect_exercise())
        self.btn_row.add_widget(back_btn)

        add_btn = Button(
            text=f"Add to {self.day}",
            font_size=dp(14),
            size_hint_x=0.65,
            background_color=(0.757, 0.267, 0.235, 1),
            color=(1, 1, 1, 1),
            bold=True,
        )
        add_btn.bind(on_press=lambda inst: self._save())
        self.btn_row.add_widget(add_btn)

    def _deselect_exercise(self):
        self.selected_exercise = None
        self.scroll.opacity = 1
        self.search_input.opacity = 1
        self.muscle_row.opacity = 1
        self.config_row.opacity = 0
        self.btn_row.clear_widgets()

    def _save(self):
        if not self.selected_exercise:
            return
        try:
            sets = int(self.sets_input.text)
        except ValueError:
            sets = 3
        reps = self.reps_input.text.strip() or "10"

        app = App.get_running_app()
        app.db.add_exercise_to_plan(self.day, self.selected_exercise["id"], sets, reps)

        if self.on_add_callback:
            self.on_add_callback()
        self.dismiss()
