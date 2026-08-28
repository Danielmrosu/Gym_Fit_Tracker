# Gym Tracker

A free, offline-first gym tracking app with nutrition, recipes, and workout planning.

## Features

- **Workout Tracking** — Log sets, reps, weight with rest timer and Pomodoro support
- **Exercise Library** — 80+ exercises with muscle groups, equipment, and descriptions
- **Nutrition Tracking** — Daily calories, protein, carbs, fat with meal categories
- **Recipe System** — Create recipes with ingredients that auto-calculate macros
- **Water Intake** — Track daily water with custom goals
- **Weekly Plan** — Schedule exercises for each day of the week
- **Body Metrics** — Track weight, body fat, BMI, chest, waist, and more
- **Personal Records** — Auto-detect PRs when you complete a set
- **Calendar View** — See your workout history on a monthly calendar
- **1RM Calculator** — Estimate your one-rep max
- **Workout Templates** — Save and reuse workout routines
- **Timers** — Stopwatch, rest timer, and Pomodoro for focused training

## Download

Download the latest APK from [Releases](../../releases).

### Installing the APK

1. Download the `.apk` file from the latest release
2. On your phone, open the downloaded file
3. If prompted, enable "Install from unknown sources"
4. Install and open

**Requires Android 5.0+ (API 21)**

## Building from Source

### Requirements

- Linux (tested on Ubuntu)
- Python 3.10+
- Java JDK 17

### Setup

```bash
# Clone the repo
git clone https://github.com/Danielmrosu/Gym_Fit_Tracker.git
cd Gym_Fit_Tracker

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install kivy buildozer

# Build the APK
export VIRTUAL_ENV=$(pwd)/.venv
buildozer android debug
```

The APK will be in `bin/`.

## Tech Stack

- Python 3 + Kivy
- SQLite (local database)
- Buildozer (Android packaging)

## Data Privacy

**No data leaves your phone.** Everything is stored locally in SQLite. No accounts, no cloud, no tracking.

## License

MIT License — free to use, modify, and distribute.
