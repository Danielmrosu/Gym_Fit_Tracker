import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App


class ExerciseLibraryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_category = "All"
        self.current_equipment = "All"
        self.current_muscle = "All"
        self.active_tab = "category"

    def on_enter(self):
        self._load_exercises()
        self._update_tabs()

    def switch_tab(self, tab):
        self.active_tab = tab
        self._update_tabs()

    def _update_tabs(self):
        cat_visible = self.active_tab == "category"
        equip_visible = self.active_tab == "equipment"
        muscle_visible = self.active_tab == "muscle"

        self.ids.category_container.opacity = 1 if cat_visible else 0
        self.ids.category_container.height = dp(34) if cat_visible else 0
        self.ids.equipment_container.opacity = 1 if equip_visible else 0
        self.ids.equipment_container.height = dp(34) if equip_visible else 0
        self.ids.equipment_container2.opacity = 1 if equip_visible else 0
        self.ids.equipment_container2.height = dp(34) if equip_visible else 0
        self.ids.muscle_container.opacity = 1 if muscle_visible else 0
        self.ids.muscle_container.height = dp(34) if muscle_visible else 0
        self.ids.muscle_container2.opacity = 1 if muscle_visible else 0
        self.ids.muscle_container2.height = dp(34) if muscle_visible else 0

        self.ids.tab_category_btn.background_color = (0.435, 0.545, 0.639, 1) if cat_visible else (0.18, 0.168, 0.15, 1)
        self.ids.tab_equipment_btn.background_color = (0.435, 0.545, 0.639, 1) if equip_visible else (0.18, 0.168, 0.15, 1)
        self.ids.tab_muscle_btn.background_color = (0.435, 0.545, 0.639, 1) if muscle_visible else (0.18, 0.168, 0.15, 1)

        self.ids.tab_category_btn.text = f"Category ({self.current_category})"
        self.ids.tab_equipment_btn.text = f"Equipment ({self.current_equipment})"
        self.ids.tab_muscle_btn.text = f"Body Part ({self.current_muscle})"

    def _load_exercises(self, exercises=None):
        app = App.get_running_app()
        if exercises is None:
            exercises = app.db.get_all_exercises()

        container = self.ids.exercises_container
        container.clear_widgets()

        if not exercises:
            container.add_widget(Label(
                text="No exercises found.",
                size_hint_y=None,
                height=dp(60),
                color=(0.6, 0.6, 0.6, 1)
            ))
            return

        for ex in exercises:
            item = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(72),
                padding=[dp(12), dp(8)],
                spacing=dp(2)
            )

            item.add_widget(Label(
                text=ex["name"],
                font_size=dp(15),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(24)
            ))

            equip = ex.get("equipment", "None")
            item.add_widget(Label(
                text=f"{ex['muscle_group']} | {equip}",
                font_size=dp(12),
                color=(0.5, 0.5, 0.8, 1),
                halign="left",
                size_hint_y=None,
                height=dp(18)
            ))

            desc_parts = []
            if ex.get("muscle_group"):
                desc_parts.append(f"Targets: {ex['muscle_group']}")
            if ex.get("description"):
                desc_parts.append(ex["description"])
            if desc_parts:
                item.add_widget(Label(
                    text=" | ".join(desc_parts),
                    font_size=dp(11),
                    color=(0.5, 0.5, 0.5, 1),
                    halign="left",
                    size_hint_y=None,
                    height=dp(16),
                    shorten=True,
                    shorten_from="right"
                ))

            ex_id = ex["id"]
            item.bind(on_touch_down=lambda inst, touch, eid=ex_id: self._on_item_touch(inst, touch, eid))

            container.add_widget(item)

    def _on_item_touch(self, item, touch, exercise_id):
        if item.collide_point(*touch.pos):
            self.show_details(exercise_id)
            return True
        return False

    def _show_image_popup(self, img_path):
        content = BoxLayout(orientation="vertical", spacing=dp(8))
        img = Image(
            source=img_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.9
        )
        content.add_widget(img)

        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_color=(0.757, 0.267, 0.235, 1),
            color=(1, 1, 1, 1)
        )
        content.add_widget(close_btn)

        popup = Popup(
            title="Exercise Image",
            content=content,
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def filter_by_category(self, category):
        self.current_category = category
        self._apply_filters()
        self._update_tabs()

    def filter_by_equipment(self, equipment):
        self.current_equipment = equipment
        self._apply_filters()
        self._update_tabs()

    def _apply_filters(self):
        app = App.get_running_app()
        exercises = app.db.get_all_exercises()

        if self.current_category != "All":
            exercises = [e for e in exercises if e["category"] == self.current_category]

        if self.current_equipment != "All":
            exercises = [e for e in exercises if e["equipment"] == self.current_equipment]

        if self.current_muscle != "All":
            exercises = [e for e in exercises if e["muscle_group"] == self.current_muscle]

        self._load_exercises(exercises)

    def filter_by_muscle(self, muscle):
        self.current_muscle = muscle
        self._apply_filters()
        self._update_tabs()

    def search(self, query):
        app = App.get_running_app()
        if query:
            exercises = app.db.search_exercises(query)
        else:
            exercises = app.db.get_all_exercises()
        self._load_exercises(exercises)

    def show_details(self, exercise_id):
        app = App.get_running_app()
        exercises = app.db.get_all_exercises()
        ex = next((e for e in exercises if e["id"] == exercise_id), None)
        if not ex:
            return

        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(8))

        exercises_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "exercises"
        )
        img_name = f"{ex['name'].lower().replace(' ', '_')}.png"
        img_path = os.path.join(exercises_dir, img_name)

        if not os.path.exists(img_path):
            for f in os.listdir(exercises_dir) if os.path.exists(exercises_dir) else []:
                if f.lower().endswith('.png') and f.lower().replace('.png', '') == img_name.replace('.png', ''):
                    img_path = os.path.join(exercises_dir, f)
                    break

        has_image = os.path.exists(img_path)

        content.add_widget(Label(
            text=ex["name"],
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(32)
        ))

        equip = ex.get("equipment", "None")
        info_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(28),
            spacing=dp(8)
        )

        cat_label = Label(
            text=ex["category"],
            font_size=dp(12),
            color=(0.435, 0.545, 0.639, 1)
        )
        info_box.add_widget(cat_label)

        muscle_label = Label(
            text=ex["muscle_group"],
            font_size=dp(12),
            color=(0.478, 0.62, 0.435, 1)
        )
        info_box.add_widget(muscle_label)

        equip_label = Label(
            text=equip,
            font_size=dp(12),
            color=(0.788, 0.635, 0.294, 1)
        )
        info_box.add_widget(equip_label)

        content.add_widget(info_box)

        if ex.get("primary_muscles"):
            muscles_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(50),
                padding=[0, dp(4)]
            )
            muscles_box.add_widget(Label(
                text="Primary Muscles Worked",
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(20)
            ))
            muscles_box.add_widget(Label(
                text=ex["primary_muscles"],
                font_size=dp(12),
                color=(0.478, 0.62, 0.435, 1),
                halign="left",
                valign="top"
            ))
            content.add_widget(muscles_box)

        if ex.get("secondary_muscles") and ex["secondary_muscles"] != "None":
            sec_muscles_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(50),
                padding=[0, dp(4)]
            )
            sec_muscles_box.add_widget(Label(
                text="Secondary & Supporting Muscles",
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(20)
            ))
            sec_muscles_box.add_widget(Label(
                text=ex["secondary_muscles"],
                font_size=dp(12),
                color=(0.788, 0.635, 0.294, 1),
                halign="left",
                valign="top"
            ))
            content.add_widget(sec_muscles_box)

        if ex.get("description"):
            desc_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(50),
                padding=[0, dp(4)]
            )
            desc_box.add_widget(Label(
                text="Description",
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(20)
            ))
            desc_box.add_widget(Label(
                text=ex["description"],
                font_size=dp(12),
                color=(0.8, 0.8, 0.8, 1),
                halign="left",
                valign="top"
            ))
            content.add_widget(desc_box)

        if ex.get("instructions") or has_image:
            inst_header = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(24),
                spacing=dp(8)
            )
            inst_header.add_widget(Label(
                text="How to do it",
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_x=0.6
            ))
            if has_image:
                view_img_btn = Button(
                    text="View Image",
                    font_size=dp(11),
                    size_hint_x=0.4,
                    background_color=(0.435, 0.545, 0.639, 1),
                    color=(1, 1, 1, 1)
                )
                view_img_btn.bind(on_press=lambda inst, path=img_path: self._show_image_popup(path))
                inst_header.add_widget(view_img_btn)
            content.add_widget(inst_header)

            if ex.get("instructions"):
                inst_box = BoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(70),
                    padding=[0, dp(4)]
                )
                inst_box.add_widget(Label(
                    text=ex["instructions"],
                    font_size=dp(12),
                    color=(0.8, 0.8, 0.8, 1),
                    halign="left",
                    valign="top",
                    text_size=(dp(300), None)
                ))
                content.add_widget(inst_box)

        progress = app.db.get_exercise_progress(exercise_id, limit=10)
        pr = app.db.get_personal_record(exercise_id)

        if pr:
            pr_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(44),
                padding=[0, dp(4)]
            )
            pr_box.add_widget(Label(
                text="Personal Record",
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(20)
            ))
            pr_box.add_widget(Label(
                text=f"{pr['value']}kg x {pr['reps']} reps ({pr['date']})",
                font_size=dp(12),
                color=(0.478, 0.62, 0.435, 1),
                halign="left",
                size_hint_y=None,
                height=dp(20)
            ))
            content.add_widget(pr_box)

        if progress:
            hist_box = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=min(dp(180), dp(24) + len(progress) * dp(22)),
                padding=[0, dp(4)]
            )
            hist_box.add_widget(Label(
                text="Recent History",
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(22)
            ))

            header = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(4))
            for txt in ["Date", "Weight", "Reps", "1RM"]:
                header.add_widget(Label(text=txt, font_size=dp(11), bold=True, color=(0.7, 0.7, 0.7, 1)))
            hist_box.add_widget(header)

            for p in progress:
                row = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(4))
                e1rm = p["weight"] * (1 + p["reps"] / 30) if p["reps"] > 1 else p["weight"]
                for txt in [p["date"][-5:], f"{p['weight']}kg", str(p["reps"]), f"{e1rm:.0f}"]:
                    row.add_widget(Label(text=txt, font_size=dp(11), color=(0.8, 0.8, 0.8, 1)))
                hist_box.add_widget(row)

            content.add_widget(hist_box)

        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=dp(44),
            font_size=dp(14)
        )
        content.add_widget(close_btn)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.92, 0.8)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
