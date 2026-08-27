import os
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty


class StopwatchScreen(Screen):
    running = BooleanProperty(False)
    elapsed = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stopwatch_event = None

    def on_enter(self):
        self._update_display()

    def on_leave(self):
        self.stop()

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if not self.running:
            self.running = True
            self._stopwatch_event = Clock.schedule_interval(self._tick_stopwatch, 1)

    def stop(self):
        self.running = False
        if self._stopwatch_event:
            self._stopwatch_event.cancel()
            self._stopwatch_event = None

    def reset_stopwatch(self):
        self.stop()
        self.elapsed = 0
        self._update_display()

    def _tick_stopwatch(self, dt):
        self.elapsed += 1
        self._update_display()

    def _update_display(self):
        if "time_display" not in self.ids:
            return
        hours = int(self.elapsed) // 3600
        minutes = (int(self.elapsed) % 3600) // 60
        seconds = int(self.elapsed) % 60
        self.ids.time_display.text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class RestTimerScreen(Screen):
    rest_running = BooleanProperty(False)
    rest_time = NumericProperty(60)
    rest_remaining = NumericProperty(60)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rest_event = None

    def on_enter(self):
        self._update_rest_display()

    def on_leave(self):
        self.stop_rest()

    def set_rest(self, seconds):
        self.stop_rest()
        self.rest_time = seconds
        self.rest_remaining = seconds
        self._update_rest_display()

    def toggle_rest(self):
        if self.rest_running:
            self.stop_rest()
        else:
            self.start_rest()

    def start_rest(self):
        if self.rest_remaining <= 0:
            self.rest_remaining = self.rest_time

        if not self.rest_running:
            self.rest_running = True
            self._rest_event = Clock.schedule_interval(self._tick_rest, 1)

    def stop_rest(self):
        self.rest_running = False
        if self._rest_event:
            self._rest_event.cancel()
            self._rest_event = None

    def reset_rest(self):
        self.stop_rest()
        self.rest_remaining = self.rest_time
        self._update_rest_display()

    def _tick_rest(self, dt):
        if self.rest_remaining > 0:
            self.rest_remaining -= 1
            self._update_rest_display()
            if self.rest_remaining == 0:
                self.stop_rest()
                self._play_beep()

    def _update_rest_display(self):
        if "rest_display" not in self.ids or "rest_progress" not in self.ids:
            return
            
        rem = max(0, int(self.rest_remaining))
        minutes = rem // 60
        seconds = rem % 60
        self.ids.rest_display.text = f"{minutes:02d}:{seconds:02d}"

        progress = (self.rest_remaining / self.rest_time) * 100 if self.rest_time > 0 else 0
        self.ids.rest_progress.value = max(0.0, min(100.0, progress))

    def _play_beep(self):
        try:
            from kivy.core.audio import SoundLoader
            beep_path = os.path.join(os.path.dirname(__file__), "..", "data", "beep.wav")
            if os.path.exists(beep_path):
                sound = SoundLoader.load(beep_path)
                if sound:
                    sound.play()
        except Exception:
            pass

    def preset_60(self):
        self.set_rest(60)
        self.start_rest()

    def preset_90(self):
        self.set_rest(90)
        self.start_rest()

    def preset_120(self):
        self.set_rest(120)
        self.start_rest()

    def preset_180(self):
        self.set_rest(180)
        self.start_rest()


class PomodoroScreen(Screen):
    pomo_running = BooleanProperty(False)
    pomo_time = NumericProperty(1500)  # 25 mins
    pomo_remaining = NumericProperty(1500)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pomo_event = None

    def on_enter(self):
        self._update_pomo_display()

    def on_leave(self):
        self.stop_pomo()

    def toggle_pomo(self):
        if self.pomo_running:
            self.stop_pomo()
        else:
            self.start_pomo()

    def set_work_mode(self):
        self.stop_pomo()
        self.pomo_time = 1500
        self.pomo_remaining = 1500
        self._update_pomo_display()

    def set_break_mode(self):
        self.stop_pomo()
        self.pomo_time = 300
        self.pomo_remaining = 300
        self._update_pomo_display()

    def show_custom_time_popup(self):
        CustomTimePopup(self._apply_custom_time)

    def _apply_custom_time(self, minutes):
        self.stop_pomo()
        self.pomo_time = minutes * 60
        self.pomo_remaining = minutes * 60
        self._update_pomo_display()

    def start_pomo(self):
        if self.pomo_remaining <= 0:
            self.pomo_remaining = self.pomo_time

        if not self.pomo_running:
            self.pomo_running = True
            self._pomo_event = Clock.schedule_interval(self._tick_pomo, 1)

    def stop_pomo(self):
        self.pomo_running = False
        if self._pomo_event:
            self._pomo_event.cancel()
            self._pomo_event = None

    def reset_pomo(self):
        self.stop_pomo()
        self.pomo_remaining = self.pomo_time
        self._update_pomo_display()

    def _tick_pomo(self, dt):
        if self.pomo_remaining > 0:
            self.pomo_remaining -= 1
            self._update_pomo_display()
            if self.pomo_remaining == 0:
                self.stop_pomo()

    def _update_pomo_display(self):
        if "pomo_display" not in self.ids:
            return
        rem = max(0, int(self.pomo_remaining))
        minutes = rem // 60
        seconds = rem % 60
        self.ids.pomo_display.text = f"{minutes:02d}:{seconds:02d}"


class CustomTimePopup(Popup):
    def __init__(self, on_save_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Custom Timer"
        self.size_hint = (0.8, 0.4)
        self.on_save_callback = on_save_callback
        self._build_content()
        self.open()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        content.add_widget(Label(
            text="Enter time in minutes:",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30),
        ))

        self.minute_input = TextInput(
            text="25",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(44),
            input_filter="int",
            multiline=False,
            halign="center",
        )
        content.add_widget(self.minute_input)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))

        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Start", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _save(self, *args):
        try:
            minutes = int(self.minute_input.text)
            if minutes > 0:
                self.on_save_callback(minutes)
                self.dismiss()
        except ValueError:
            pass