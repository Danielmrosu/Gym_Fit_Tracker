import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition

from database import Database
from screens.home import HomeScreen
from screens.workout import WorkoutScreen, NewWorkoutScreen, ActiveWorkoutScreen
from screens.exercise_library import ExerciseLibraryScreen
from screens.timer import StopwatchScreen, RestTimerScreen, PomodoroScreen
from screens.progress import ProgressScreen
from screens.body_metrics import BodyMetricsScreen
from screens.settings import SettingsScreen
from screens.weekly_plan import WeeklyPlanScreen
from screens.nutrition import NutritionScreen
from screens.calendar_view import CalendarScreen

# Remove Builder.load_file() if your KV file is named gym.kv 
# and your App class is named GymApp (Kivy loads it automatically).


class GymApp(App):
    def build(self):
        self.title = "Gym Tracker"
        self.db = Database(os.path.join(self.user_data_dir, "gym.db"))

        sm = ScreenManager(transition=FadeTransition(duration=0.2))

        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(WorkoutScreen(name="workouts"))
        sm.add_widget(NewWorkoutScreen(name="new_workout"))
        sm.add_widget(ActiveWorkoutScreen(name="active_workout"))
        sm.add_widget(ExerciseLibraryScreen(name="library"))

        # Explicitly set the name attributes matching gym.kv targets
        sm.add_widget(StopwatchScreen(name="stopwatch"))
        sm.add_widget(RestTimerScreen(name="rest_timer"))
        sm.add_widget(PomodoroScreen(name="pomodoro"))

        sm.add_widget(ProgressScreen(name="progress"))
        sm.add_widget(BodyMetricsScreen(name="body_metrics"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(WeeklyPlanScreen(name="weekly_plan"))
        sm.add_widget(NutritionScreen(name="nutrition"))
        sm.add_widget(CalendarScreen(name="calendar"))

        sm.current = "home"
        return sm


if __name__ == "__main__":
    GymApp().run()