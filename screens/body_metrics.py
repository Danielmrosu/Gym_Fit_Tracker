from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App


class BodyMetricsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self._load_metrics()

    def _load_metrics(self):
        app = App.get_running_app()
        metrics = app.db.get_body_metrics(limit=20)
        latest = app.db.get_latest_body_metric()

        if latest:
            weight = latest.get('weight', 0) or 0
            height = latest.get('height', 0) or 0
            body_fat = latest.get('body_fat', 0) or 0
            waist = latest.get('waist', 0) or 0

            self.ids.current_weight.text = f"{weight}{latest.get('weight_unit', 'kg')}"
            self.ids.current_fat.text = f"Body Fat: {body_fat}%"
            self.ids.current_chest.text = f"Chest: {latest.get('chest', '--')}cm"
            self.ids.current_waist.text = f"Waist: {latest.get('waist', '--')}cm"

            if height > 0:
                bmi = weight / ((height / 100) ** 2)
                if bmi < 18.5:
                    bmi_cat = "Underweight"
                    bmi_color = (0.435, 0.545, 0.639, 1)
                elif bmi < 25:
                    bmi_cat = "Normal"
                    bmi_color = (0.478, 0.62, 0.435, 1)
                elif bmi < 30:
                    bmi_cat = "Overweight"
                    bmi_color = (0.788, 0.635, 0.294, 1)
                else:
                    bmi_cat = "Obese"
                    bmi_color = (0.757, 0.267, 0.235, 1)
                self.ids.bmi_value.text = f"BMI: {bmi:.1f}"
                self.ids.bmi_category.text = bmi_cat
                self.ids.bmi_category.color = bmi_color
            else:
                self.ids.bmi_value.text = "BMI: --"
                self.ids.bmi_category.text = "Add height"
                self.ids.bmi_category.color = (0.48, 0.45, 0.41, 1)

            if body_fat > 0:
                if body_fat < 6:
                    zone = "Essential"
                    zone_color = (0.435, 0.545, 0.639, 1)
                elif body_fat < 14:
                    zone = "Athletic"
                    zone_color = (0.478, 0.62, 0.435, 1)
                elif body_fat < 18:
                    zone = "Fitness"
                    zone_color = (0.478, 0.62, 0.435, 1)
                elif body_fat < 25:
                    zone = "Average"
                    zone_color = (0.788, 0.635, 0.294, 1)
                else:
                    zone = "Obese"
                    zone_color = (0.757, 0.267, 0.235, 1)
                self.ids.fat_zone.text = f"{body_fat}% - {zone}"
                self.ids.fat_zone.color = zone_color
            else:
                self.ids.fat_zone.text = "--"
                self.ids.fat_zone.color = (0.48, 0.45, 0.41, 1)

            if len(metrics) >= 2:
                prev = metrics[1]
                w_diff = weight - (prev.get('weight', 0) or 0)
                f_diff = body_fat - (prev.get('body_fat', 0) or 0)
                w_sign = "+" if w_diff >= 0 else ""
                f_sign = "+" if f_diff >= 0 else ""
                self.ids.change_value.text = f"Weight: {w_sign}{w_diff:.1f}kg | Fat: {f_sign}{f_diff:.1f}%"
                if w_diff > 0:
                    self.ids.change_value.color = (0.757, 0.267, 0.235, 1)
                elif w_diff < 0:
                    self.ids.change_value.color = (0.478, 0.62, 0.435, 1)
                else:
                    self.ids.change_value.color = (0.48, 0.45, 0.41, 1)
            else:
                self.ids.change_value.text = "Log 2+ entries to see changes"
                self.ids.change_value.color = (0.48, 0.45, 0.41, 1)
        else:
            self.ids.current_weight.text = "--"
            self.ids.current_fat.text = "Body Fat: --"
            self.ids.current_chest.text = "Chest: --"
            self.ids.current_waist.text = "Waist: --"
            self.ids.bmi_value.text = "BMI: --"
            self.ids.bmi_category.text = "No data"
            self.ids.bmi_category.color = (0.6, 0.6, 0.6, 1)
            self.ids.fat_zone.text = "--"
            self.ids.fat_zone.color = (0.6, 0.6, 0.6, 1)
            self.ids.change_value.text = "Log 2+ entries to see changes"
            self.ids.change_value.color = (0.6, 0.6, 0.6, 1)

        container = self.ids.metrics_container
        container.clear_widgets()

        for m in metrics:
            item = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(110),
                padding=[dp(12), dp(6)],
                spacing=dp(2)
            )

            weight_str = f"{m['weight']}{m['weight_unit']}" if m.get("weight") else "--"
            item.add_widget(Label(
                text=f"{m['date']}  |  Weight: {weight_str}",
                font_size=dp(14),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(24)
            ))

            details = []
            if m.get("body_fat"):
                details.append(f"BF: {m['body_fat']}%")
            if m.get("chest"):
                details.append(f"Chest: {m['chest']}")
            if m.get("waist"):
                details.append(f"Waist: {m['waist']}")
            if m.get("hips"):
                details.append(f"Hips: {m['hips']}")
            if m.get("biceps_left"):
                details.append(f"Bicep: {m['biceps_left']}")
            if m.get("thighs_left"):
                details.append(f"Thigh: {m['thighs_left']}")

            item.add_widget(Label(
                text=" | ".join(details) if details else "No measurements",
                font_size=dp(12),
                color=(0.6, 0.6, 0.6, 1),
                halign="left",
                size_hint_y=None,
                height=dp(20)
            ))

            if m.get("notes"):
                item.add_widget(Label(
                    text=m["notes"],
                    font_size=dp(11),
                    color=(0.5, 0.5, 0.8, 1),
                    halign="left",
                    size_hint_y=None,
                    height=dp(18)
                ))

            btn_row = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(6))

            edit_btn = Button(
                text="Edit",
                font_size=dp(11),
                size_hint_x=0.3,
                background_color=(0.18, 0.168, 0.15, 1),
                color=(0.48, 0.45, 0.41, 1),
            )
            edit_btn.bind(on_press=lambda btn, metric=m: self.show_edit_metric(metric))
            btn_row.add_widget(edit_btn)

            delete_btn = Button(
                text="Delete",
                font_size=dp(11),
                size_hint_x=0.3,
                background_color=(0.757, 0.267, 0.235, 1),
                color=(1, 1, 1, 1),
            )
            delete_btn.bind(on_press=lambda btn, mid=m["id"]: self.delete_metric(mid))
            btn_row.add_widget(delete_btn)

            item.add_widget(btn_row)
            container.add_widget(item)

    def show_add_metric(self):
        popup = MetricPopup(self._load_metrics)
        popup.open()

    def show_edit_metric(self, metric):
        popup = MetricPopup(self._load_metrics, metric=metric)
        popup.open()

    def delete_metric(self, metric_id):
        popup = DeleteMetricPopup(metric_id, self._load_metrics)
        popup.open()


class MetricPopup(Popup):
    def __init__(self, on_save_callback, metric=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Edit Metrics" if metric else "Log Body Metrics"
        self.size_hint = (0.92, 0.85)
        self.on_save_callback = on_save_callback
        self.metric = metric
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        scroll = ScrollView()
        form = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        form.bind(minimum_height=form.setter("height"))

        defaults = self.metric if self.metric else {}

        self.inputs = {}
        fields = [
            ("weight", "Body Weight (kg)", "0"),
            ("height", "Height (cm)", "0"),
            ("body_fat", "Body Fat %", "0"),
            ("chest", "Chest (cm)", "0"),
            ("waist", "Waist (cm)", "0"),
            ("hips", "Hips (cm)", "0"),
            ("biceps_left", "Left Bicep (cm)", "0"),
            ("biceps_right", "Right Bicep (cm)", "0"),
            ("thighs_left", "Left Thigh (cm)", "0"),
            ("thighs_right", "Right Thigh (cm)", "0"),
            ("notes", "Notes", ""),
        ]

        for key, hint, default in fields:
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
            row.add_widget(Label(
                text=hint,
                font_size=dp(13),
                size_hint_x=0.45
            ))
            val = defaults.get(key, default)
            if isinstance(val, float) and val == int(val) and key != "notes":
                val = str(int(val))
            elif isinstance(val, float):
                val = str(val)
            inp = TextInput(
                text=str(val) if val else default,
                font_size=dp(13),
                size_hint_x=0.55,
                input_filter="float" if key != "notes" else None,
                readonly=key == "body_fat",
            )
            if key == "body_fat":
                inp.background_color = (0.15, 0.15, 0.18, 1)
            self.inputs[key] = inp
            row.add_widget(inp)
            form.add_widget(row)

        self.inputs["weight"].bind(text=self._auto_calc_body_fat)
        self.inputs["height"].bind(text=self._auto_calc_body_fat)
        self.inputs["waist"].bind(text=self._auto_calc_body_fat)

        scroll.add_widget(form)
        content.add_widget(scroll)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))

        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _auto_calc_body_fat(self, *args):
        try:
            weight = float(self.inputs["weight"].text)
            height = float(self.inputs["height"].text)
            waist = float(self.inputs["waist"].text)
        except ValueError:
            return
        if weight <= 0 or height <= 0 or waist <= 0:
            return
        bmi = weight / ((height / 100) ** 2)
        body_fat = (1.20 * bmi) + (0.23 * 25) - 10.8
        body_fat = max(5, min(60, round(body_fat, 1)))
        self.inputs["body_fat"].text = str(body_fat)

    def _save(self, *args):
        app = App.get_running_app()
        data = {}
        for key, inp in self.inputs.items():
            val = inp.text.strip()
            if key == "notes":
                data[key] = val
            elif val and val != "0":
                try:
                    data[key] = float(val)
                except ValueError:
                    pass

        if self.metric:
            app.db.update_body_metric(self.metric["id"], **data)
        else:
            if data:
                app.db.add_body_metric(**data)

        if self.on_save_callback:
            self.on_save_callback()
        self.dismiss()


class DeleteMetricPopup(Popup):
    def __init__(self, metric_id, on_delete_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Delete Metric"
        self.size_hint = (0.8, 0.35)
        self.metric_id = metric_id
        self.on_delete_callback = on_delete_callback
        self._build_content()
        self.open()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        content.add_widget(Label(
            text="Are you sure you want to\ndelete this metric entry?",
            font_size=dp(14),
            halign="center",
        ))

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        delete = Button(text="Delete", font_size=dp(14), background_color=(0.757, 0.267, 0.235, 1))
        delete.bind(on_press=self._confirm_delete)
        btn_row.add_widget(delete)

        content.add_widget(btn_row)
        self.content = content

    def _confirm_delete(self, *args):
        app = App.get_running_app()
        app.db.delete_body_metric(self.metric_id)
        if self.on_delete_callback:
            self.on_delete_callback()
        self.dismiss()
