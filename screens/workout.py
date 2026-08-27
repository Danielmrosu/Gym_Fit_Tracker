from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime, date

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
TODAY = DAYS[date.today().weekday()]


class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self._load_today_plan()
        self._load_workouts()
        self._load_templates()

    def _load_today_plan(self):
        app = App.get_running_app()
        exercises = app.db.get_plan_exercises_for_day(TODAY)
        container = self.ids.plan_container
        container.clear_widgets()

        if not exercises:
            self.ids.plan_section.height = dp(0)
            self.ids.plan_section.opacity = 0
            self.ids.plan_section.size_hint_y = None
            return

        self.ids.plan_section.height = dp(44) + len(exercises) * dp(28)
        self.ids.plan_section.opacity = 1
        self.ids.plan_section.size_hint_y = None

        for ex in exercises:
            row = BoxLayout(size_hint_y=None, height=dp(26), spacing=dp(8))
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

    def _load_workouts(self):
        app = App.get_running_app()
        workouts = app.db.get_workouts(limit=50)

        container = self.ids.workouts_container
        container.clear_widgets()

        if not workouts:
            container.add_widget(Label(
                text="No workouts yet.\nTap + to create one!",
                size_hint_y=None,
                height=dp(100),
                font_size=dp(16),
                color=(0.6, 0.6, 0.6, 1)
            ))
            return

        for w in workouts:
            has_notes = bool(w.get("notes"))
            item_height = dp(90) if has_notes else dp(70)

            item = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=item_height,
                padding=[dp(12), dp(8)],
                spacing=dp(2)
            )

            row = BoxLayout(spacing=dp(10))

            info = BoxLayout(orientation="vertical", spacing=dp(2))
            info.add_widget(Label(
                text=w["name"],
                font_size=dp(16),
                bold=True,
                halign="left",
                size_hint_x=0.8
            ))

            status = "Completed" if w["completed"] else "In Progress"
            duration = f" | {w['duration']}min" if w["duration"] else ""
            distance = f" | {w['distance']:.1f}km" if w.get("distance") else ""
            info.add_widget(Label(
                text=f"{w['date']} {duration}{distance} - {status}",
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                halign="left",
                size_hint_x=0.8
            ))

            row.add_widget(info)

            btn = Button(
                text="Open",
                size_hint_x=0.25,
                size_hint_y=None,
                height=dp(40),
                font_size=dp(12)
            )
            wid = w["id"]
            btn.bind(on_press=lambda inst, wid=wid: self._open_workout(wid))
            row.add_widget(btn)

            item.add_widget(row)

            if has_notes:
                item.add_widget(Label(
                    text=w["notes"],
                    font_size=dp(11),
                    color=(0.5, 0.5, 0.8, 1),
                    halign="left",
                    size_hint_y=None,
                    height=dp(18),
                    shorten=True,
                    shorten_from="right",
                ))

            container.add_widget(item)

    def _load_templates(self):
        app = App.get_running_app()
        templates = app.db.get_templates()

        container = self.ids.templates_container
        container.clear_widgets()

        if not templates:
            container.add_widget(Label(
                text="No templates yet.\nSave a workout as template!",
                size_hint_y=None,
                height=dp(60),
                font_size=dp(13),
                color=(0.6, 0.6, 0.6, 1)
            ))
            return

        for t in templates:
            item = BoxLayout(
                size_hint_y=None,
                height=dp(50),
                padding=[dp(12), dp(4)],
                spacing=dp(8)
            )

            item.add_widget(Label(
                text=t["name"],
                font_size=dp(14),
                halign="left",
                size_hint_x=0.5
            ))

            start_btn = Button(
                text="Start",
                size_hint_x=0.25,
                size_hint_y=None,
                height=dp(36),
                font_size=dp(12),
                background_color=(0.478, 0.62, 0.435, 1),
            )
            tid = t["id"]
            start_btn.bind(on_press=lambda inst, tid=tid: self._start_from_template(tid))
            item.add_widget(start_btn)

            del_btn = Button(
                text="X",
                size_hint_x=0.15,
                size_hint_y=None,
                height=dp(36),
                font_size=dp(12),
                background_color=(0.757, 0.267, 0.235, 1),
            )
            del_btn.bind(on_press=lambda inst, tid=tid: self._delete_template(tid))
            item.add_widget(del_btn)

            container.add_widget(item)

    def _open_workout(self, workout_id):
        app = App.get_running_app()
        screen = self.manager.get_screen("active_workout")
        screen.load_workout(workout_id)
        self.manager.current = "active_workout"

    def _start_from_template(self, template_id):
        app = App.get_running_app()
        workout_id = app.db.start_workout_from_template(template_id)
        if workout_id:
            screen = self.manager.get_screen("active_workout")
            screen.load_workout(workout_id)
            self.manager.current = "active_workout"

    def _delete_template(self, template_id):
        app = App.get_running_app()
        app.db.delete_template(template_id)
        self._load_templates()

    def go_new(self):
        self.manager.current = "new_workout"

    def start_from_plan(self):
        app = App.get_running_app()
        workout_id = app.db.start_workout_from_plan(TODAY)
        if workout_id:
            screen = self.manager.get_screen("active_workout")
            screen.load_workout(workout_id)
            self.manager.current = "active_workout"


class NewWorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_workout(self):
        name = self.ids.workout_name.text.strip()
        if not name:
            name = f"Workout - {datetime.now().strftime('%Y-%m-%d')}"

        app = App.get_running_app()
        workout_id = app.db.create_workout(name)

        screen = self.manager.get_screen("active_workout")
        screen.load_workout(workout_id)
        self.manager.current = "active_workout"
        self.ids.workout_name.text = ""

    def cancel(self):
        self.manager.current = "workouts"


class ActiveWorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.workout_id = None
        self.start_time = None

    def load_workout(self, workout_id):
        self.workout_id = workout_id
        self.start_time = datetime.now()
        self._load_exercises()

    def _load_exercises(self):
        app = App.get_running_app()
        workout = app.db.get_workout(self.workout_id)
        if workout:
            self.ids.workout_title.text = workout["name"]

        exercises = app.db.get_workout_exercises(self.workout_id)
        container = self.ids.exercises_container
        container.clear_widgets()

        for we in exercises:
            sets = app.db.get_sets_for_exercise(we["id"])
            set_rows_height = len(sets) * dp(30) if sets else 0
            item_height = dp(130) + set_rows_height

            is_completed = we.get("completed", 0) == 1

            item = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=item_height,
                padding=[dp(12), dp(8)],
                spacing=dp(4)
            )

            with item.canvas.before:
                Color(0.08, 0.3, 0.12, 0.3) if is_completed else Color(0, 0, 0, 0)
                item._bg_rect = RoundedRectangle(pos=item.pos, size=item.size, radius=[dp(8)])
            item.bind(pos=self._update_item_bg, size=self._update_item_bg)
            item._is_completed = is_completed

            header = BoxLayout(size_hint_y=None, height=dp(30))
            header.add_widget(Label(
                text=we["exercise_name"],
                font_size=dp(16),
                bold=True,
                halign="left"
            ))

            we_id = we["id"]

            check_btn = Button(
                text="Done" if is_completed else "Check",
                size_hint_x=0.2,
                font_size=dp(11),
                background_color=(0.12, 0.5, 0.18, 1) if is_completed else (0.2, 0.18, 0.16, 1),
                color=(1, 1, 1, 1) if is_completed else (0.658, 0.631, 0.588, 1),
            )
            check_btn.bind(on_press=lambda inst, we_id=we_id, cur=is_completed: self._toggle_complete(we_id, cur))
            header.add_widget(check_btn)

            rm_btn = Button(
                text="X",
                size_hint_x=0.15,
                font_size=dp(12),
                background_color=(0.757, 0.267, 0.235, 1)
            )
            rm_btn.bind(on_press=lambda inst, we_id=we_id: self._remove_exercise(we_id))
            header.add_widget(rm_btn)
            item.add_widget(header)

            info = Label(
                text=f"{we['category']} | {we['muscle_group']}",
                font_size=dp(12),
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(20),
                halign="left"
            )
            item.add_widget(info)

            for s in sets:
                set_row = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(6))

                is_cardio = we.get("category") == "Cardio"
                if is_cardio:
                    calories = s.get("calories", 0) or 0
                    cal_text = f" | {calories:.0f}cal" if calories > 0 else ""
                    set_text = f"S{s['set_number']}: {s['weight']:.1f}km x{s['reps']}min{cal_text}".replace(".", ",")
                else:
                    set_text = f"S{s['set_number']}: {s['weight']:.1f}{s['weight_unit']} x{s['reps']} reps".replace(".", ",")

                set_row.add_widget(Label(
                    text=set_text,
                    font_size=dp(12),
                    size_hint_x=0.4,
                    halign="left",
                ))

                edit_btn = Button(text="Edit", font_size=dp(10), size_hint_x=0.2,
                                  background_color=(0.18, 0.168, 0.15, 1), color=(0.48, 0.45, 0.41, 1))
                dup_btn = Button(text="Dup", font_size=dp(10), size_hint_x=0.2,
                                 background_color=(0.435, 0.545, 0.639, 1), color=(1, 1, 1, 1))
                del_btn = Button(text="Del", font_size=dp(10), size_hint_x=0.2,
                                 background_color=(0.757, 0.267, 0.235, 1), color=(1, 1, 1, 1))

                sid = s["id"]
                edit_btn.bind(on_press=lambda inst, s=s, we_id=we_id: self._edit_set(s, we_id))
                dup_btn.bind(on_press=lambda inst, s=s, we_id=we_id: self._duplicate_set(s, we_id))
                del_btn.bind(on_press=lambda inst, sid=sid: self._delete_set(sid))

                set_row.add_widget(edit_btn)
                set_row.add_widget(dup_btn)
                set_row.add_widget(del_btn)
                item.add_widget(set_row)

            btn_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))

            add_set_btn = Button(
                text="+ Add Set",
                font_size=dp(12)
            )
            add_set_btn.bind(on_press=lambda inst, we_id=we_id: self._add_set(we_id))
            btn_row.add_widget(add_set_btn)

            item.add_widget(btn_row)
            container.add_widget(item)

    def _add_exercise(self):
        app = App.get_running_app()
        popup = AddExercisePopup(self.workout_id, self._load_exercises)
        popup.open()

    def _add_set(self, workout_exercise_id):
        popup = AddSetPopup(workout_exercise_id, self._load_exercises)
        popup.open()

    def _edit_set(self, set_data, workout_exercise_id):
        popup = AddSetPopup(workout_exercise_id, self._load_exercises, set_data=set_data)
        popup.open()

    def _duplicate_set(self, set_data, workout_exercise_id):
        app = App.get_running_app()
        sets = app.db.get_sets_for_exercise(workout_exercise_id)
        set_num = len(sets) + 1
        app.db.add_set(
            workout_exercise_id, set_num,
            reps=set_data["reps"],
            weight=set_data["weight"],
            weight_unit=set_data.get("weight_unit", "kg"),
            rest_time=set_data.get("rest_time", 60),
        )
        self._load_exercises()

    def _delete_set(self, set_id):
        app = App.get_running_app()
        app.db.delete_set(set_id)
        self._load_exercises()

    def _remove_exercise(self, workout_exercise_id):
        app = App.get_running_app()
        app.db.remove_exercise_from_workout(workout_exercise_id)
        self._load_exercises()

    def _toggle_complete(self, workout_exercise_id, currently_completed):
        app = App.get_running_app()
        app.db.update_workout_exercise(workout_exercise_id, completed=0 if currently_completed else 1)
        self._load_exercises()

    def _update_item_bg(self, instance, value):
        if hasattr(instance, '_bg_rect'):
            instance._bg_rect.pos = instance.pos
            instance._bg_rect.size = instance.size

    def save_as_template(self):
        if self.workout_id is None:
            return
        app = App.get_running_app()
        workout = app.db.get_workout(self.workout_id)
        if workout:
            popup = TemplateNamePopup(self.workout_id, None, default_name=workout["name"])
            popup.open()

    def finish_workout(self):
        if self.workout_id is None:
            return
        popup = WorkoutNotesPopup(self.workout_id, self.start_time, self.manager)
        popup.open()

    def cancel_workout(self):
        if self.workout_id:
            app = App.get_running_app()
            app.db.delete_workout(self.workout_id)
        self.workout_id = None
        self.manager.current = "workouts"


class TemplateNamePopup(Popup):
    def __init__(self, workout_id, on_save_callback, default_name="", **kwargs):
        super().__init__(**kwargs)
        self.title = "Save as Template"
        self.size_hint = (0.85, 0.45)
        self.workout_id = workout_id
        self.on_save_callback = on_save_callback
        self._build_content(default_name)
        self.open()

    def _build_content(self, default_name):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        content.add_widget(Label(
            text="Template Name",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(24),
        ))

        self.name_input = TextInput(
            text=default_name,
            font_size=dp(16),
            size_hint_y=None,
            height=dp(44),
            multiline=False,
            hint_text="e.g. Push Day, Leg Day...",
        )
        content.add_widget(self.name_input)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _save(self, *args):
        app = App.get_running_app()
        name = self.name_input.text.strip()
        if not name:
            return
        app.db.save_workout_as_template(self.workout_id, name)
        if self.on_save_callback:
            self.on_save_callback()
        self.dismiss()


class AddExercisePopup(Popup):
    def __init__(self, workout_id, on_add_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Add Exercise"
        self.size_hint = (0.92, 0.85)
        self.workout_id = workout_id
        self.on_add_callback = on_add_callback
        self.active_tab = "category"
        self.current_category = "All"
        self.current_equipment = "All"
        self.current_muscle = "All"
        self._build_content()

    def _build_content(self):
        app = App.get_running_app()
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

        scroll = ScrollView(size_hint_y=1)
        self.exercises_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4),
        )
        self.exercises_list.bind(minimum_height=self.exercises_list.setter("height"))
        scroll.add_widget(self.exercises_list)
        content.add_widget(scroll)

        self.content = content
        self._load_filter_buttons()
        self._update_tabs()
        self._load_exercises(app.db.get_all_exercises())

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
            btn.bind(on_press=lambda inst, ex_id=ex_id: self._add_exercise(ex_id))
            self.exercises_list.add_widget(btn)

    def _add_exercise(self, exercise_id):
        app = App.get_running_app()
        app.db.add_exercise_to_workout(self.workout_id, exercise_id)
        if self.on_add_callback:
            self.on_add_callback()
        self.dismiss()


class AddSetPopup(Popup):
    def __init__(self, workout_exercise_id, on_save_callback, set_data=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Edit Set" if set_data else "Add Set"
        self.size_hint = (0.8, 0.55)
        self.workout_exercise_id = workout_exercise_id
        self.on_save_callback = on_save_callback
        self.set_data = set_data
        self.is_cardio = False
        self._check_exercise_type()
        self._build_content()
        self.open()

    def _check_exercise_type(self):
        app = App.get_running_app()
        cursor = app.db.conn.cursor()
        cursor.execute("""
            SELECT e.category FROM exercises e
            JOIN workout_exercises we ON e.id = we.exercise_id
            WHERE we.id = ?
        """, (self.workout_exercise_id,))
        row = cursor.fetchone()
        if row and row["category"] == "Cardio":
            self.is_cardio = True

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        if self.is_cardio:
            content.add_widget(Label(
                text="Distance (km)",
                font_size=dp(14),
                size_hint_y=None,
                height=dp(24),
                halign="left",
            ))

            default_distance = str(self.set_data["weight"]) if self.set_data and self.set_data["weight"] > 0 else "0"

            self.weight_input = TextInput(
                text=default_distance,
                font_size=dp(18),
                size_hint_y=None,
                height=dp(44),
                input_filter="float",
                multiline=False,
                halign="center",
            )
            content.add_widget(self.weight_input)

            content.add_widget(Label(
                text="Duration (min)",
                font_size=dp(14),
                size_hint_y=None,
                height=dp(24),
                halign="left",
            ))

            default_duration = str(self.set_data["reps"]) if self.set_data else "0"

            self.reps_input = TextInput(
                text=default_duration,
                font_size=dp(18),
                size_hint_y=None,
                height=dp(44),
                input_filter="int",
                multiline=False,
                halign="center",
            )
            content.add_widget(self.reps_input)
        else:
            content.add_widget(Label(
                text="Weight",
                font_size=dp(14),
                size_hint_y=None,
                height=dp(24),
                halign="left",
            ))

            default_weight = str(int(self.set_data["weight"])) if self.set_data and self.set_data["weight"] == int(self.set_data["weight"]) else str(self.set_data["weight"]) if self.set_data else "0"

            self.weight_input = TextInput(
                text=default_weight,
                font_size=dp(18),
                size_hint_y=None,
                height=dp(44),
                input_filter="float",
                multiline=False,
                halign="center",
            )
            content.add_widget(self.weight_input)

            content.add_widget(Label(
                text="Reps",
                font_size=dp(14),
                size_hint_y=None,
                height=dp(24),
                halign="left",
            ))

            default_reps = str(self.set_data["reps"]) if self.set_data else "10"

            self.reps_input = TextInput(
                text=default_reps,
                font_size=dp(18),
                size_hint_y=None,
                height=dp(44),
                input_filter="int",
                multiline=False,
                halign="center",
            )
            content.add_widget(self.reps_input)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _save(self, *args):
        app = App.get_running_app()
        try:
            weight = float(self.weight_input.text)
        except ValueError:
            weight = 0
        try:
            reps = int(self.reps_input.text)
        except ValueError:
            reps = 0

        calories = 0.0
        if self.is_cardio:
            cursor = app.db.conn.cursor()
            cursor.execute("""
                SELECT e.name FROM exercises e
                JOIN workout_exercises we ON e.id = we.exercise_id
                WHERE we.id = ?
            """, (self.workout_exercise_id,))
            row = cursor.fetchone()
            if row:
                calories = app.db.calculate_cardio_calories(row["name"], reps, weight)

        if self.set_data:
            app.db.update_set(self.set_data["id"], weight=weight, reps=reps, calories=calories)
        else:
            sets = app.db.get_sets_for_exercise(self.workout_exercise_id)
            set_num = len(sets) + 1
            app.db.add_set(self.workout_exercise_id, set_num, reps=reps, weight=weight, rest_time=60, calories=calories)

            if not self.is_cardio:
                try:
                    timer_screen = self.manager.get_screen("rest_timer")
                    timer_screen.set_rest(60)
                    timer_screen.start_rest()
                except Exception:
                    pass

        if not self.is_cardio and weight > 0 and reps > 0:
            cursor = app.db.conn.cursor()
            cursor.execute("""
                SELECT we.exercise_id, we.workout_id FROM workout_exercises we
                WHERE we.id = ?
            """, (self.workout_exercise_id,))
            row = cursor.fetchone()
            if row:
                pr_result = app.db.check_and_save_pr(
                    row["exercise_id"], weight, reps,
                    workout_id=row["workout_id"], record_type="weight"
                )
                if pr_result:
                    from screens.progress import PRPopup
                    pr_popup = PRPopup(pr_result)
                    pr_popup.open()

        if self.on_save_callback:
            self.on_save_callback()
        self.dismiss()


class WorkoutNotesPopup(Popup):
    def __init__(self, workout_id, start_time, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.title = "Finish Workout"
        self.size_hint = (0.85, 0.6)
        self.workout_id = workout_id
        self.start_time = start_time
        self.screen_manager = screen_manager
        self._build_content()
        self.open()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        content.add_widget(Label(
            text="How was your workout?",
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(30),
        ))

        self.notes_input = TextInput(
            hint_text="Notes (optional)...",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(80),
            multiline=True,
            padding=[dp(8), dp(8)],
        )
        content.add_widget(self.notes_input)

        dist_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        dist_row.add_widget(Label(
            text="Distance (km):",
            font_size=dp(13),
            size_hint_x=0.4,
            halign="left",
        ))
        self.distance_input = TextInput(
            hint_text="0.0",
            font_size=dp(14),
            size_hint_x=0.6,
            input_filter="float",
            multiline=False,
        )
        dist_row.add_widget(self.distance_input)
        content.add_widget(dist_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Finish", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _save(self, *args):
        app = App.get_running_app()
        try:
            duration = 0
            if self.start_time:
                duration = int((datetime.now() - self.start_time).total_seconds() / 60)
            notes = self.notes_input.text.strip() if self.notes_input else ""
            distance = 0.0
            if self.distance_input.text.strip():
                try:
                    distance = float(self.distance_input.text.strip())
                except ValueError:
                    pass
            app.db.update_workout(self.workout_id, duration=duration, completed=1, notes=notes, distance=distance)
            active = self.screen_manager.get_screen("active_workout")
            active.workout_id = None
            active.start_time = None
            self.screen_manager.current = "workouts"
            self.dismiss()
        except Exception as e:
            print(f"Error saving workout: {e}")
            self.dismiss()
