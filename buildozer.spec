[app]

title = Gym Tracker

package.name = gymtracker

package.domain = org.gymtracker

source.dir = .

source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,sqlite3

orientation = portrait

fullscreen = 0

android.permissions = INTERNET

android.api = 31

android.minapi = 21

android.ndk = 25b

android.accept_sdk_license = True

android.arch = arm64-v8a

android.arch_targets = arm64-v8a

android.logcat_filters = *:S python:I

android.adb_device_timeout = 5

presplash.filename = %(source.dir)s/data/presplash.png

icon.filename = %(source.dir)s/data/icon.png

launcher.icon.filename = %(source.dir)s/data/icon.png

#build_mode = debug
