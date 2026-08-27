import os
import shutil
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App
from kivy.config import Config


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self._load_settings()

    def _load_settings(self):
        if not Config.has_section("gym"):
            Config.add_section("gym")

        default_unit = Config.get("gym", "weight_unit", fallback="kg")
        default_rest = Config.get("gym", "rest_time", fallback="60")
        default_reps = Config.get("gym", "default_reps", fallback="10")

        self.ids.weight_unit_spinner.text = default_unit
        self.ids.rest_time_spinner.text = f"{default_rest}s"
        self.ids.default_reps_spinner.text = default_reps

    def save_settings(self):
        if not Config.has_section("gym"):
            Config.add_section("gym")

        unit = self.ids.weight_unit_spinner.text
        rest = self.ids.rest_time_spinner.text.replace("s", "")
        reps = self.ids.default_reps_spinner.text

        Config.set("gym", "weight_unit", unit)
        Config.set("gym", "rest_time", rest)
        Config.set("gym", "default_reps", reps)
        Config.write()

    def backup_database(self):
        app = App.get_running_app()
        db_path = app.db.db_path
        backup_dir = os.path.join(os.path.dirname(db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"gym_backup_{timestamp}.db")

        try:
            shutil.copy2(db_path, backup_path)
            popup = Popup(
                title="Backup Complete",
                content=Label(
                    text=f"Saved to:\n{backup_path}",
                    font_size=dp(12),
                    halign="center",
                ),
                size_hint=(0.85, 0.4),
            )
            popup.open()
        except Exception as e:
            popup = Popup(
                title="Backup Failed",
                content=Label(
                    text=str(e),
                    font_size=dp(12),
                    halign="center",
                ),
                size_hint=(0.85, 0.4),
            )
            popup.open()

    def reset_data(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text="This will delete ALL your workouts,\nbody metrics, and personal records.\n\nExercises will be reset to defaults.\n\nThis cannot be undone!",
            font_size=dp(13),
            halign="center",
        ))

        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))

        cancel_btn = Button(
            text="Cancel",
            font_size=dp(13),
            background_color=(0.18, 0.168, 0.15, 1),
            color=(0.658, 0.631, 0.588, 1),
        )

        confirm_btn = Button(
            text="Delete Everything",
            font_size=dp(13),
            background_color=(0.757, 0.267, 0.235, 1),
            color=(1, 1, 1, 1),
        )

        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(confirm_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title="Reset All Data",
            content=content,
            size_hint=(0.85, 0.45),
            auto_dismiss=False,
        )

        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda inst: self._do_reset(popup))
        popup.open()

    def _do_reset(self, popup):
        popup.dismiss()
        app = App.get_running_app()
        try:
            app.db.conn.close()
        except Exception:
            pass

        db_path = app.db.db_path
        if os.path.exists(db_path):
            os.remove(db_path)

        app.db = app.db.__class__(db_path)
        app.stop()

    def go_back(self):
        self.save_settings()
        self.manager.current = "home"
