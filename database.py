import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple


class Database:
    def __init__(self, db_path: str = "gym.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                equipment TEXT NOT NULL DEFAULT 'None',
                muscle_group TEXT NOT NULL,
                description TEXT DEFAULT '',
                instructions TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date DATE NOT NULL,
                duration INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workout_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                order_num INTEGER DEFAULT 0,
                FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS workout_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_exercise_id INTEGER NOT NULL,
                set_number INTEGER NOT NULL,
                reps INTEGER DEFAULT 0,
                weight REAL DEFAULT 0.0,
                weight_unit TEXT DEFAULT 'kg',
                rest_time INTEGER DEFAULT 60,
                completed INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS body_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                weight REAL DEFAULT 0.0,
                weight_unit TEXT DEFAULT 'kg',
                height REAL DEFAULT 0.0,
                body_fat REAL DEFAULT 0.0,
                chest REAL DEFAULT 0.0,
                waist REAL DEFAULT 0.0,
                hips REAL DEFAULT 0.0,
                biceps_left REAL DEFAULT 0.0,
                biceps_right REAL DEFAULT 0.0,
                thighs_left REAL DEFAULT 0.0,
                thighs_right REAL DEFAULT 0.0,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workout_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS template_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                order_num INTEGER DEFAULT 0,
                FOREIGN KEY (template_id) REFERENCES workout_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS template_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_exercise_id INTEGER NOT NULL,
                set_number INTEGER NOT NULL,
                reps INTEGER DEFAULT 10,
                weight REAL DEFAULT 0.0,
                weight_unit TEXT DEFAULT 'kg',
                rest_time INTEGER DEFAULT 60,
                FOREIGN KEY (template_exercise_id) REFERENCES template_exercises(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS weekly_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_of_week TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS plan_exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                sets INTEGER DEFAULT 3,
                reps TEXT DEFAULT '10',
                order_num INTEGER DEFAULT 0,
                FOREIGN KEY (plan_id) REFERENCES weekly_plan(id) ON DELETE CASCADE,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
            );
        """)

        self.conn.commit()

        cursor = self.conn.cursor()
        try:
            cursor.execute("ALTER TABLE body_metrics ADD COLUMN height REAL DEFAULT 0.0")
            self.conn.commit()
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE workout_exercises ADD COLUMN completed INTEGER DEFAULT 0")
            self.conn.commit()
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE workouts ADD COLUMN distance REAL DEFAULT 0.0")
            self.conn.commit()
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE workout_sets ADD COLUMN calories REAL DEFAULT 0.0")
            self.conn.commit()
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE exercises ADD COLUMN primary_muscles TEXT DEFAULT ''")
            self.conn.commit()
        except Exception:
            pass

        try:
            cursor.execute("ALTER TABLE exercises ADD COLUMN secondary_muscles TEXT DEFAULT ''")
            self.conn.commit()
        except Exception:
            pass

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS nutrition_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                meal_type TEXT NOT NULL,
                name TEXT NOT NULL,
                calories REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS water_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                amount_ml INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                calories INTEGER DEFAULT 0,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS personal_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_id INTEGER NOT NULL,
                record_type TEXT NOT NULL,
                value REAL NOT NULL,
                reps INTEGER DEFAULT 1,
                workout_id INTEGER,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (exercise_id) REFERENCES exercises(id),
                FOREIGN KEY (workout_id) REFERENCES workouts(id)
            );
        """)

        self._migrate_personal_records()

        self._seed_exercises()
        self.add_missing_exercises()

    def _migrate_personal_records(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(personal_records)")
        columns = {row[1] for row in cursor.fetchall()}
        if "value" not in columns:
            cursor.execute("DROP TABLE IF EXISTS personal_records")
            cursor.execute("""
                CREATE TABLE personal_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_id INTEGER NOT NULL,
                    record_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    reps INTEGER DEFAULT 1,
                    workout_id INTEGER,
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (exercise_id) REFERENCES exercises(id),
                    FOREIGN KEY (workout_id) REFERENCES workouts(id)
                )
            """)
            self.conn.commit()

    def _seed_exercises(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exercises")
        if cursor.fetchone()[0] > 0:
            return

        exercises = [
            ("Barbell Bench Press", "Strength", "Barbell", "Chest", "Flat barbell bench press", "Lie on bench, grip bar wider than shoulder width, lower to chest, press up", "Pectoralis Major, Triceps, Anterior Deltoids", "Pectoralis Minor, Serratus Anterior, Forearms"),
            ("Incline Dumbbell Press", "Strength", "Dumbbells", "Chest", "Incline dumbbell chest press", "Set bench to 30-45 degrees, press dumbbells up from chest", "Upper Pectoralis Major, Anterior Deltoids, Triceps", "Serratus Anterior, Forearms"),
            ("Dumbbell Flyes", "Strength", "Dumbbells", "Chest", "Dumbbell chest flyes", "Lie on bench, arms extended, lower dumbbells out to sides, squeeze back up", "Pectoralis Major", "Anterior Deltoids, Biceps"),
            ("Chest Press Machine", "Strength", "Machine", "Chest", "Machine chest press", "Sit upright, push handles forward, squeeze chest, return with control", "Pectoralis Major, Triceps, Anterior Deltoids", "Serratus Anterior"),
            ("Cable Crossover", "Strength", "Cable", "Chest", "Cable chest flyes", "Stand between cables, bring hands together in front, control the return", "Pectoralis Major", "Anterior Deltoids"),
            ("Push-ups", "Bodyweight", "None", "Chest", "Standard push-ups", "Hands shoulder width apart, lower body to ground, push back up", "Pectoralis Major, Triceps, Anterior Deltoids", "Core, Serratus Anterior"),
            ("Barbell Back Squat", "Strength", "Barbell", "Legs", "Barbell back squat", "Bar on upper back, squat down until thighs parallel, stand back up", "Quadriceps, Glutes, Hamstrings", "Calves, Core, Lower Back"),
            ("Leg Press", "Strength", "Machine", "Legs", "Machine leg press", "Push platform away with feet, lower back down with control", "Quadriceps, Glutes", "Hamstrings, Calves"),
            ("Romanian Deadlift", "Strength", "Barbell", "Legs", "Romanian deadlift for hamstrings", "Slight knee bend, hinge at hips, lower bar along legs, squeeze glutes up", "Hamstrings, Glutes", "Lower Back, Core"),
            ("Leg Curl", "Strength", "Machine", "Legs", "Lying leg curl", "Lie face down, curl weight up toward glutes, lower with control", "Hamstrings", "Calves"),
            ("Leg Extension", "Strength", "Machine", "Legs", "Leg extension machine", "Extend legs to lift weight, lower with control", "Quadriceps", "None"),
            ("Hack Squat", "Strength", "Machine", "Legs", "Machine hack squat", "Place shoulders under pads, squat down, push back up", "Quadriceps, Glutes", "Hamstrings, Calves"),
            ("Calf Raise Machine", "Strength", "Machine", "Legs", "Seated calf raise", "Place shoulders under pads, raise heels, lower with control", "Gastrocnemius, Soleus", "None"),
            ("Barbell Overhead Press", "Strength", "Barbell", "Shoulders", "Standing barbell overhead press", "Bar at collarbone, press overhead, lower with control", "Anterior Deltoids, Medial Deltoids, Triceps", "Upper Chest, Core"),
            ("Dumbbell Lateral Raise", "Strength", "Dumbbells", "Shoulders", "Lateral raise for side delts", "Arms at sides, raise dumbbells to shoulder height, lower slowly", "Medial Deltoids", "Anterior Deltoids, Trapezius"),
            ("Face Pulls", "Strength", "Cable", "Shoulders", "Cable face pulls", "Pull rope to face, squeeze rear delts, return slowly", "Posterior Deltoids, Rotator Cuff", "Biceps, Rhomboids"),
            ("Reverse Fly Machine", "Strength", "Machine", "Shoulders", "Rear delt fly machine", "Sit facing pad, open arms outward, squeeze rear delts", "Posterior Deltoids", "Rhomboids, Middle Trapezius"),
            ("Barbell Row", "Strength", "Barbell", "Back", "Barbell bent-over row", "Hinge at hips, row bar to lower chest, squeeze shoulder blades", "Latissimus Dorsi, Rhomboids, Biceps", "Posterior Deltoids, Lower Back"),
            ("Pull-ups", "Bodyweight", "None", "Back", "Pull-up bar exercise", "Hang from bar, pull up until chin over bar, lower with control", "Latissimus Dorsi, Biceps", "Rhomboids, Forearms"),
            ("Lat Pulldown", "Strength", "Cable", "Back", "Cable lat pulldown", "Pull bar to upper chest, squeeze lats, return slowly", "Latissimus Dorsi, Biceps", "Rhomboids, Posterior Deltoids"),
            ("Seated Cable Row", "Strength", "Cable", "Back", "Seated cable row", "Pull handle to abdomen, squeeze shoulder blades, return slowly", "Latissimus Dorsi, Rhomboids, Biceps", "Posterior Deltoids, Lower Back"),
            ("Deadlift", "Strength", "Barbell", "Back", "Conventional deadlift", "Feet hip width, grip bar, drive through heels, lock out hips at top", "Erector Spinae, Glutes, Hamstrings", "Quadriceps, Core, Forearms"),
            ("Barbell Bicep Curl", "Strength", "Barbell", "Arms", "Standing barbell curl", "Curl bar up, squeeze biceps, lower with control", "Biceps Brachii", "Brachialis, Forearms"),
            ("Hammer Curl", "Strength", "Dumbbells", "Arms", "Dumbbell hammer curl", "Curl with neutral grip, targets brachialis and forearms", "Brachialis, Brachioradialis", "Biceps Brachii, Forearms"),
            ("Tricep Pushdown", "Strength", "Cable", "Arms", "Cable tricep pushdown", "Push bar down, squeeze triceps, return with control", "Triceps Brachii", "None"),
            ("Skull Crushers", "Strength", "Barbell", "Arms", "Lying tricep extension", "Lower bar to forehead, extend arms, squeeze triceps", "Triceps Brachii", "None"),
            ("Tricep Dip Machine", "Strength", "Machine", "Arms", "Tricep dip machine", "Sit upright, push handles down, extend arms, return with control", "Triceps Brachii, Pectoralis Major", "Anterior Deltoids"),
            ("Plank", "Bodyweight", "None", "Core", "Core stabilization exercise", "Hold body in straight line from head to heels", "Transverse Abdominis, Rectus Abdominis", "Obliques, Lower Back"),
            ("Cable Crunch", "Strength", "Cable", "Core", "Cable abdominal crunch", "Kneel facing cable, crunch down, squeeze abs", "Rectus Abdominis", "Obliques"),
            ("Hanging Leg Raise", "Bodyweight", "None", "Core", "Hanging leg raise", "Hang from bar, raise legs to 90 degrees, lower with control", "Rectus Abdominis, Hip Flexors", "Obliques, Forearms"),
            ("Russian Twist", "Bodyweight", "None", "Core", "Seated Russian twist", "Lean back slightly, rotate torso side to side", "Obliques, Rectus Abdominis", "Hip Flexors"),
            ("Ab Rollout", "Bodyweight", "None", "Core", "Ab wheel rollout", "Kneel, roll wheel forward extending body, roll back to start", "Rectus Abdominis, Transverse Abdominis", "Obliques, Lower Back"),
            ("Calf Raise", "Strength", "Dumbbells", "Legs", "Standing calf raise", "Rise up on toes, squeeze calves, lower with control", "Gastrocnemius, Soleus", "None"),
            ("Treadmill Running", "Cardio", "Cardio Machine", "Full Body", "Running on treadmill", "Adjust speed and incline as needed", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Rowing Machine", "Cardio", "Cardio Machine", "Full Body", "Cardio rowing", "Drive with legs, pull handle to chest, return with control", "Latissimus Dorsi, Quadriceps, Glutes", "Biceps, Core, Hamstrings"),
            ("Stationary Bike", "Cardio", "Cardio Machine", "Full Body", "Indoor cycling", "Maintain steady cadence, adjust resistance as needed", "Quadriceps, Hamstrings, Glutes", "Calves, Core"),
            ("Elliptical", "Cardio", "Cardio Machine", "Full Body", "Elliptical trainer", "Push and pull handles, maintain smooth stride", "Quadriceps, Glutes, Latissimus Dorsi", "Hamstrings, Core, Biceps"),
            ("Jump Rope", "Cardio", "None", "Full Body", "Jump rope cardio", "Maintain steady pace, stay on balls of feet", "Calves, Quadriceps, Core", "Shoulders, Forearms"),
            ("Battle Ropes", "Cardio", "None", "Full Body", "Battle rope exercises", "Alternate waves, slams, or other patterns", "Shoulders, Core, Arms", "Back, Legs"),
            ("Outdoor Running", "Cardio", "None", "Legs", "Running outdoors", "Run at steady pace or intervals, track distance and time", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Trail Running", "Cardio", "None", "Legs", "Running on trails", "Run on uneven terrain, adjust pace for elevation changes", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors, Ankles"),
            ("Sprint Intervals", "Cardio", "None", "Legs", "High intensity sprints", "Sprint 100-400m, walk/jog recovery, repeat", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Hill Repeats", "Cardio", "None", "Legs", "Running uphill repeatedly", "Find a hill, run up hard, jog down recovery, repeat", "Quadriceps, Glutes, Calves", "Hamstrings, Core"),
            ("Fartlek Run", "Cardio", "None", "Legs", "Speed play running", "Mix fast and slow segments randomly during run", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Tempo Run", "Cardio", "None", "Legs", "Sustained pace running", "Run at comfortably hard pace for 20-40 minutes", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Outdoor Cycling", "Cardio", "None", "Legs", "Road cycling outdoors", "Cycle at steady pace or intervals, track distance and time", "Quadriceps, Hamstrings, Glutes", "Calves, Core"),
            ("Mountain Biking", "Cardio", "None", "Legs", "Off-road cycling", "Cycle on trails with varying terrain, adjust effort for climbs", "Quadriceps, Glutes, Hamstrings", "Calves, Core, Arms"),
            ("Cycling Intervals", "Cardio", "None", "Legs", "High intensity cycling intervals", "Alternate between fast sprints and easy recovery pedaling", "Quadriceps, Hamstrings, Glutes", "Calves, Core"),
            ("Hill Cycling", "Cardio", "None", "Legs", "Cycling uphill repeatedly", "Find a hill, cycle up hard, easy recovery descent, repeat", "Quadriceps, Glutes, Calves", "Hamstrings, Core"),
        ]

        cursor.executemany(
            "INSERT INTO exercises (name, category, equipment, muscle_group, description, instructions, primary_muscles, secondary_muscles) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            exercises
        )
        self.conn.commit()

    def add_missing_exercises(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM exercises")
        existing = {row["name"] for row in cursor.fetchall()}

        new_exercises = [
            ("Outdoor Running", "Cardio", "None", "Legs", "Running outdoors", "Run at steady pace or intervals, track distance and time", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Trail Running", "Cardio", "None", "Legs", "Running on trails", "Run on uneven terrain, adjust pace for elevation changes", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors, Ankles"),
            ("Sprint Intervals", "Cardio", "None", "Legs", "High intensity sprints", "Sprint 100-400m, walk/jog recovery, repeat", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Hill Repeats", "Cardio", "None", "Legs", "Running uphill repeatedly", "Find a hill, run up hard, jog down recovery, repeat", "Quadriceps, Glutes, Calves", "Hamstrings, Core"),
            ("Fartlek Run", "Cardio", "None", "Legs", "Speed play running", "Mix fast and slow segments randomly during run", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Tempo Run", "Cardio", "None", "Legs", "Sustained pace running", "Run at comfortably hard pace for 20-40 minutes", "Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            ("Outdoor Cycling", "Cardio", "None", "Legs", "Road cycling outdoors", "Cycle at steady pace or intervals, track distance and time", "Quadriceps, Hamstrings, Glutes", "Calves, Core"),
            ("Mountain Biking", "Cardio", "None", "Legs", "Off-road cycling", "Cycle on trails with varying terrain, adjust effort for climbs", "Quadriceps, Glutes, Hamstrings", "Calves, Core, Arms"),
            ("Cycling Intervals", "Cardio", "None", "Legs", "High intensity cycling intervals", "Alternate between fast sprints and easy recovery pedaling", "Quadriceps, Hamstrings, Glutes", "Calves, Core"),
            ("Hill Cycling", "Cardio", "None", "Legs", "Cycling uphill repeatedly", "Find a hill, cycle up hard, easy recovery descent, repeat", "Quadriceps, Glutes, Calves", "Hamstrings, Core"),
        ]

        to_add = [ex for ex in new_exercises if ex[0] not in existing]
        if to_add:
            cursor.executemany(
                "INSERT INTO exercises (name, category, equipment, muscle_group, description, instructions, primary_muscles, secondary_muscles) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                to_add
            )
            self.conn.commit()

        cursor.execute("SELECT name, primary_muscles FROM exercises WHERE primary_muscles = '' OR primary_muscles IS NULL")
        missing = cursor.fetchall()
        muscle_data = {
            "Barbell Bench Press": ("Pectoralis Major, Triceps, Anterior Deltoids", "Pectoralis Minor, Serratus Anterior, Forearms"),
            "Incline Dumbbell Press": ("Upper Pectoralis Major, Anterior Deltoids, Triceps", "Serratus Anterior, Forearms"),
            "Dumbbell Flyes": ("Pectoralis Major", "Anterior Deltoids, Biceps"),
            "Chest Press Machine": ("Pectoralis Major, Triceps, Anterior Deltoids", "Serratus Anterior"),
            "Cable Crossover": ("Pectoralis Major", "Anterior Deltoids"),
            "Push-ups": ("Pectoralis Major, Triceps, Anterior Deltoids", "Core, Serratus Anterior"),
            "Barbell Back Squat": ("Quadriceps, Glutes, Hamstrings", "Calves, Core, Lower Back"),
            "Leg Press": ("Quadriceps, Glutes", "Hamstrings, Calves"),
            "Romanian Deadlift": ("Hamstrings, Glutes", "Lower Back, Core"),
            "Leg Curl": ("Hamstrings", "Calves"),
            "Leg Extension": ("Quadriceps", "None"),
            "Hack Squat": ("Quadriceps, Glutes", "Hamstrings, Calves"),
            "Calf Raise Machine": ("Gastrocnemius, Soleus", "None"),
            "Barbell Overhead Press": ("Anterior Deltoids, Medial Deltoids, Triceps", "Upper Chest, Core"),
            "Dumbbell Lateral Raise": ("Medial Deltoids", "Anterior Deltoids, Trapezius"),
            "Face Pulls": ("Posterior Deltoids, Rotator Cuff", "Biceps, Rhomboids"),
            "Reverse Fly Machine": ("Posterior Deltoids", "Rhomboids, Middle Trapezius"),
            "Barbell Row": ("Latissimus Dorsi, Rhomboids, Biceps", "Posterior Deltoids, Lower Back"),
            "Pull-ups": ("Latissimus Dorsi, Biceps", "Rhomboids, Forearms"),
            "Lat Pulldown": ("Latissimus Dorsi, Biceps", "Rhomboids, Posterior Deltoids"),
            "Seated Cable Row": ("Latissimus Dorsi, Rhomboids, Biceps", "Posterior Deltoids, Lower Back"),
            "Deadlift": ("Erector Spinae, Glutes, Hamstrings", "Quadriceps, Core, Forearms"),
            "Barbell Bicep Curl": ("Biceps Brachii", "Brachialis, Forearms"),
            "Hammer Curl": ("Brachialis, Brachioradialis", "Biceps Brachii, Forearms"),
            "Tricep Pushdown": ("Triceps Brachii", "None"),
            "Skull Crushers": ("Triceps Brachii", "None"),
            "Tricep Dip Machine": ("Triceps Brachii, Pectoralis Major", "Anterior Deltoids"),
            "Plank": ("Transverse Abdominis, Rectus Abdominis", "Obliques, Lower Back"),
            "Cable Crunch": ("Rectus Abdominis", "Obliques"),
            "Hanging Leg Raise": ("Rectus Abdominis, Hip Flexors", "Obliques, Forearms"),
            "Russian Twist": ("Obliques, Rectus Abdominis", "Hip Flexors"),
            "Ab Rollout": ("Rectus Abdominis, Transverse Abdominis", "Obliques, Lower Back"),
            "Calf Raise": ("Gastrocnemius, Soleus", "None"),
            "Treadmill Running": ("Quadriceps, Hamstrings, Glutes, Calves", "Core, Hip Flexors"),
            "Rowing Machine": ("Latissimus Dorsi, Quadriceps, Glutes", "Biceps, Core, Hamstrings"),
            "Stationary Bike": ("Quadriceps, Hamstrings, Glutes", "Calves, Core"),
            "Elliptical": ("Quadriceps, Glutes, Latissimus Dorsi", "Hamstrings, Core, Biceps"),
            "Jump Rope": ("Calves, Quadriceps, Core", "Shoulders, Forearms"),
            "Battle Ropes": ("Shoulders, Core, Arms", "Back, Legs"),
        }
        for row in missing:
            name = row["name"]
            if name in muscle_data:
                primary, secondary = muscle_data[name]
                cursor.execute("UPDATE exercises SET primary_muscles = ?, secondary_muscles = ? WHERE name = ?", (primary, secondary, name))
        self.conn.commit()

    # === Exercise Operations ===
    def get_all_exercises(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM exercises ORDER BY category, muscle_group, name")
        return [dict(row) for row in cursor.fetchall()]

    def get_exercises_by_category(self, category: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM exercises WHERE category = ? ORDER BY muscle_group, name", (category,))
        return [dict(row) for row in cursor.fetchall()]

    def get_exercises_by_muscle(self, muscle_group: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM exercises WHERE muscle_group = ? ORDER BY name", (muscle_group,))
        return [dict(row) for row in cursor.fetchall()]

    def get_exercises_by_equipment(self, equipment: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM exercises WHERE equipment = ? ORDER BY muscle_group, name", (equipment,))
        return [dict(row) for row in cursor.fetchall()]

    def search_exercises(self, query: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM exercises WHERE name LIKE ? OR muscle_group LIKE ? OR category LIKE ? OR equipment LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_all_equipment_types(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT equipment FROM exercises ORDER BY equipment")
        return [row["equipment"] for row in cursor.fetchall()]

    # === Workout Operations ===
    def create_workout(self, name: str, workout_date: str = None) -> int:
        if workout_date is None:
            workout_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO workouts (name, date) VALUES (?, ?)", (name, workout_date))
        self.conn.commit()
        return cursor.lastrowid

    def get_workouts(self, limit: int = 50) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM workouts ORDER BY date DESC, created_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_workout(self, workout_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_workout(self, workout_id: int, **kwargs):
        allowed = {"name", "date", "duration", "notes", "completed", "distance"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [workout_id]
        self.conn.execute(f"UPDATE workouts SET {set_clause} WHERE id = ?", values)
        self.conn.commit()

    def delete_workout(self, workout_id: int):
        self.conn.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
        self.conn.commit()

    # === Workout Exercise Operations ===
    def add_exercise_to_workout(self, workout_id: int, exercise_id: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(order_num) FROM workout_exercises WHERE workout_id = ?", (workout_id,))
        max_order = cursor.fetchone()[0] or 0
        cursor.execute(
            "INSERT INTO workout_exercises (workout_id, exercise_id, order_num) VALUES (?, ?, ?)",
            (workout_id, exercise_id, max_order + 1)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_workout_exercises(self, workout_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT we.*, e.name as exercise_name, e.category, e.muscle_group
            FROM workout_exercises we
            JOIN exercises e ON we.exercise_id = e.id
            WHERE we.workout_id = ?
            ORDER BY we.order_num
        """, (workout_id,))
        return [dict(row) for row in cursor.fetchall()]

    def remove_exercise_from_workout(self, workout_exercise_id: int):
        self.conn.execute("DELETE FROM workout_exercises WHERE id = ?", (workout_exercise_id,))
        self.conn.commit()

    def update_workout_exercise(self, workout_exercise_id: int, **kwargs):
        allowed = {"completed", "order_num"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [workout_exercise_id]
        self.conn.execute(f"UPDATE workout_exercises SET {set_clause} WHERE id = ?", values)
        self.conn.commit()

    # === Set Operations ===
    def add_set(self, workout_exercise_id: int, set_number: int, reps: int = 0,
                weight: float = 0.0, weight_unit: str = "kg", rest_time: int = 60,
                calories: float = 0.0) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO workout_sets (workout_exercise_id, set_number, reps, weight, weight_unit, rest_time, calories) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (workout_exercise_id, set_number, reps, weight, weight_unit, rest_time, calories)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_sets_for_exercise(self, workout_exercise_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM workout_sets WHERE workout_exercise_id = ? ORDER BY set_number",
            (workout_exercise_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def update_set(self, set_id: int, **kwargs):
        allowed = {"reps", "weight", "weight_unit", "rest_time", "completed", "notes", "calories"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [set_id]
        self.conn.execute(f"UPDATE workout_sets SET {set_clause} WHERE id = ?", values)
        self.conn.commit()

    def delete_set(self, set_id: int):
        self.conn.execute("DELETE FROM workout_sets WHERE id = ?", (set_id,))
        self.conn.commit()

    def calculate_cardio_calories(self, exercise_name: str, duration_min: float, distance_km: float) -> float:
        met_values = {
            "Outdoor Running": 9.8,
            "Trail Running": 9.0,
            "Sprint Intervals": 12.0,
            "Hill Repeats": 10.5,
            "Fartlek Run": 9.5,
            "Tempo Run": 9.8,
            "Treadmill Running": 9.8,
            "Rowing Machine": 7.0,
            "Stationary Bike": 6.8,
            "Elliptical": 5.0,
            "Jump Rope": 11.0,
            "Battle Ropes": 10.0,
            "Outdoor Cycling": 7.5,
            "Mountain Biking": 8.5,
            "Cycling Intervals": 10.0,
            "Hill Cycling": 9.0,
        }
        met = met_values.get(exercise_name, 8.0)
        weight_kg = 75
        duration_hours = duration_min / 60.0
        calories = met * weight_kg * duration_hours
        return round(calories)

    def complete_set(self, set_id: int):
        self.conn.execute("UPDATE workout_sets SET completed = 1 WHERE id = ?", (set_id,))
        self.conn.commit()

    # === Body Metrics Operations ===
    def add_body_metric(self, metric_date: str = None, **kwargs) -> int:
        if metric_date is None:
            metric_date = date.today().isoformat()
        allowed = {"weight", "weight_unit", "height", "body_fat", "chest", "waist", "hips",
                    "biceps_left", "biceps_right", "thighs_left", "thighs_right", "notes"}
        data = {k: v for k, v in kwargs.items() if k in allowed}
        data["date"] = metric_date

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO body_metrics ({columns}) VALUES ({placeholders})", list(data.values()))
        self.conn.commit()
        return cursor.lastrowid

    def get_body_metrics(self, limit: int = 100) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM body_metrics ORDER BY date DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_latest_body_metric(self) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM body_metrics ORDER BY date DESC LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_body_metric(self, metric_id: int):
        self.conn.execute("DELETE FROM body_metrics WHERE id = ?", (metric_id,))
        self.conn.commit()

    def update_body_metric(self, metric_id: int, **kwargs):
        allowed = {"weight", "weight_unit", "height", "body_fat", "chest", "waist", "hips",
                    "biceps_left", "biceps_right", "thighs_left", "thighs_right", "notes", "date"}
        data = {k: v for k, v in kwargs.items() if k in allowed}
        if not data:
            return
        set_clause = ", ".join(f"{k} = ?" for k in data)
        values = list(data.values()) + [metric_id]
        self.conn.execute(f"UPDATE body_metrics SET {set_clause} WHERE id = ?", values)
        self.conn.commit()

    # === Nutrition Operations ===
    def add_nutrition_entry(self, meal_type: str, name: str, calories: float = 0,
                            protein: float = 0, carbs: float = 0, fat: float = 0,
                            entry_date: str = None) -> int:
        if entry_date is None:
            entry_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO nutrition_entries (date, meal_type, name, calories, protein, carbs, fat) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (entry_date, meal_type, name, calories, protein, carbs, fat)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_nutrition_entries_for_date(self, entry_date: str = None) -> List[Dict]:
        if entry_date is None:
            entry_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM nutrition_entries WHERE date = ? ORDER BY meal_type, created_at",
            (entry_date,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def delete_nutrition_entry(self, entry_id: int):
        self.conn.execute("DELETE FROM nutrition_entries WHERE id = ?", (entry_id,))
        self.conn.commit()

    def get_daily_nutrition_summary(self, entry_date: str = None) -> Dict:
        if entry_date is None:
            entry_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(calories), 0) as total_calories,
                   COALESCE(SUM(protein), 0) as total_protein,
                   COALESCE(SUM(carbs), 0) as total_carbs,
                   COALESCE(SUM(fat), 0) as total_fat
            FROM nutrition_entries WHERE date = ?
        """, (entry_date,))
        row = cursor.fetchone()
        return {
            "total_calories": row["total_calories"],
            "total_protein": row["total_protein"],
            "total_carbs": row["total_carbs"],
            "total_fat": row["total_fat"]
        }

    def add_water_intake(self, amount_ml: int, intake_date: str = None) -> int:
        if intake_date is None:
            intake_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO water_intake (date, amount_ml) VALUES (?, ?)",
            (intake_date, amount_ml)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_water_intake_for_date(self, intake_date: str = None) -> int:
        if intake_date is None:
            intake_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(amount_ml), 0) as total FROM water_intake WHERE date = ?",
            (intake_date,)
        )
        return cursor.fetchone()["total"]

    def delete_water_intake(self, intake_id: int):
        self.conn.execute("DELETE FROM water_intake WHERE id = ?", (intake_id,))
        self.conn.commit()

    def get_water_entries_for_date(self, intake_date: str = None) -> List[Dict]:
        if intake_date is None:
            intake_date = date.today().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM water_intake WHERE date = ? ORDER BY created_at",
            (intake_date,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_water_goal(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'water_goal'")
        row = cursor.fetchone()
        return int(row["value"]) if row else 2000

    def set_water_goal(self, goal_ml: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'water_goal'")
        if cursor.fetchone():
            cursor.execute("UPDATE settings SET value = ? WHERE key = 'water_goal'", (str(goal_ml),))
        else:
            cursor.execute("INSERT INTO settings (key, value) VALUES ('water_goal', ?)", (str(goal_ml),))
        self.conn.commit()

    # === Recipes ===
    def add_recipe(self, name: str, notes: str = "") -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO recipes (name, notes) VALUES (?, ?)",
            (name, notes)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_recipes(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM recipes ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def delete_recipe(self, recipe_id: int):
        self.conn.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
        self.conn.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        self.conn.commit()

    def add_recipe_ingredient(self, recipe_id: int, name: str, calories: int = 0,
                              protein: float = 0, carbs: float = 0, fat: float = 0) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO recipe_ingredients (recipe_id, name, calories, protein, carbs, fat) VALUES (?, ?, ?, ?, ?, ?)",
            (recipe_id, name, calories, protein, carbs, fat)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_recipe_ingredients(self, recipe_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
        return [dict(row) for row in cursor.fetchall()]

    def delete_recipe_ingredient(self, ingredient_id: int):
        self.conn.execute("DELETE FROM recipe_ingredients WHERE id = ?", (ingredient_id,))
        self.conn.commit()

    def get_recipe_totals(self, recipe_id: int) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(calories), 0) as total_calories,
                   COALESCE(SUM(protein), 0) as total_protein,
                   COALESCE(SUM(carbs), 0) as total_carbs,
                   COALESCE(SUM(fat), 0) as total_fat
            FROM recipe_ingredients WHERE recipe_id = ?
        """, (recipe_id,))
        row = cursor.fetchone()
        return dict(row) if row else {"total_calories": 0, "total_protein": 0, "total_carbs": 0, "total_fat": 0}

    # === Progress/Stats ===
    def get_exercise_progress(self, exercise_id: int, limit: int = 50) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ws.weight, ws.reps, w.date
            FROM workout_sets ws
            JOIN workout_exercises we ON ws.workout_exercise_id = we.id
            JOIN workouts w ON we.workout_id = w.id
            WHERE we.exercise_id = ? AND ws.completed = 1
            ORDER BY w.date DESC
            LIMIT ?
        """, (exercise_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def get_personal_record(self, exercise_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM personal_records WHERE exercise_id = ? ORDER BY value DESC, reps DESC LIMIT 1",
            (exercise_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_exercise_prs(self, exercise_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM personal_records
            WHERE exercise_id = ?
            ORDER BY date DESC
        """, (exercise_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_prs(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT pr.*, e.name as exercise_name
            FROM personal_records pr
            JOIN exercises e ON pr.exercise_id = e.id
            ORDER BY pr.date DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def check_and_save_pr(self, exercise_id: int, weight: float, reps: int,
                          workout_id: int = None, record_type: str = "weight") -> Optional[Dict]:
        existing = self.get_personal_record(exercise_id)

        if record_type == "weight":
            new_value = weight
        elif record_type == "1rm":
            new_value = weight * (1 + reps / 30.0)
        else:
            new_value = weight

        is_new_pr = False
        if existing is None:
            is_new_pr = True
        elif record_type == "1rm":
            old_1rm = existing["value"] * (1 + existing.get("reps", 1) / 30.0)
            if new_value > old_1rm:
                is_new_pr = True
        else:
            if new_value > existing["value"]:
                is_new_pr = True
            elif new_value == existing["value"] and reps > existing.get("reps", 0):
                is_new_pr = True

        if is_new_pr:
            workout_date = date.today().isoformat()
            if workout_id:
                workout = self.get_workout(workout_id)
                if workout:
                    workout_date = workout["date"]

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO personal_records (exercise_id, record_type, value, reps, workout_id, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (exercise_id, record_type, new_value, reps, workout_id, workout_date))
            self.conn.commit()

            return {
                "exercise_id": exercise_id,
                "record_type": record_type,
                "value": new_value,
                "reps": reps,
                "date": workout_date,
                "old_value": existing["value"] if existing else 0,
                "old_reps": existing.get("reps", 0) if existing else 0
            }

        return None

    def get_workout_stats(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM workouts")
        total_workouts = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM workouts WHERE date >= date('now', '-7 days')")
        this_week = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT SUM(duration) as total_duration FROM workouts
            WHERE date >= date('now', '-30 days')
        """)
        row = cursor.fetchone()
        monthly_minutes = row["total_duration"] or 0

        cursor.execute("""
            SELECT COUNT(DISTINCT w.date) as unique_days
            FROM workouts w
            WHERE w.date >= date('now', '-30 days')
        """)
        active_days = cursor.fetchone()["unique_days"]

        cursor.execute("""
            SELECT COALESCE(SUM(distance), 0) as total_distance
            FROM workouts WHERE date >= date('now', '-30 days') AND distance > 0
        """)
        monthly_distance = cursor.fetchone()["total_distance"]

        return {
            "total_workouts": total_workouts,
            "workouts_this_week": this_week,
            "monthly_minutes": monthly_minutes,
            "active_days_this_month": active_days,
            "monthly_distance": round(monthly_distance, 1)
        }

    def get_workout_stats_for_period(self, period: str) -> Dict:
        cursor = self.conn.cursor()
        if period == "week":
            date_filter = "date('now', '-7 days')"
        elif period == "month":
            date_filter = "date('now', '-30 days')"
        elif period == "year":
            date_filter = "date('now', '-365 days')"
        else:
            return self.get_workout_stats()

        cursor.execute(f"SELECT COUNT(*) as total FROM workouts WHERE date >= {date_filter}")
        workouts_count = cursor.fetchone()["total"]

        cursor.execute(f"""
            SELECT COALESCE(SUM(duration), 0) as total_duration FROM workouts
            WHERE date >= {date_filter}
        """)
        total_minutes = cursor.fetchone()["total_duration"]

        cursor.execute(f"""
            SELECT COUNT(DISTINCT date) as unique_days
            FROM workouts WHERE date >= {date_filter}
        """)
        active_days = cursor.fetchone()["unique_days"]

        return {
            "workouts_count": workouts_count,
            "total_minutes": total_minutes,
            "active_days": active_days,
        }

    def get_run_stats_for_period(self, period: str) -> Dict:
        cursor = self.conn.cursor()
        if period == "week":
            date_filter = "date('now', '-7 days')"
        elif period == "month":
            date_filter = "date('now', '-30 days')"
        elif period == "year":
            date_filter = "date('now', '-365 days')"
        else:
            date_filter = "date('now', '-36500 days')"

        cursor.execute(f"""
            SELECT COALESCE(SUM(distance), 0) as total_distance,
                   COALESCE(AVG(duration), 0) as avg_duration,
                   COALESCE(AVG(distance), 0) as avg_distance
            FROM workouts WHERE date >= {date_filter} AND distance > 0
        """)
        row = cursor.fetchone()
        total_distance = row["total_distance"]
        avg_duration = row["avg_duration"]
        avg_distance = row["avg_distance"]

        cursor.execute(f"""
            SELECT COUNT(*) as count FROM workouts
            WHERE date >= {date_filter} AND distance > 0
        """)
        run_count = cursor.fetchone()["count"]

        avg_pace = 0
        if total_distance > 0 and avg_duration > 0:
            avg_pace = avg_duration / total_distance

        cursor.execute(f"""
            SELECT duration, distance, date FROM workouts
            WHERE distance > 0 AND date >= {date_filter}
            ORDER BY (distance / NULLIF(duration, 0)) DESC LIMIT 1
        """)
        best_row = cursor.fetchone()
        best_pace = 0
        best_pace_date = ""
        if best_row and best_row["distance"] > 0 and best_row["duration"] > 0:
            best_pace = best_row["duration"] / best_row["distance"]
            best_pace_date = best_row["date"]

        return {
            "total_distance": round(total_distance, 1),
            "run_count": run_count,
            "avg_pace": round(avg_pace, 1),
            "best_pace": round(best_pace, 1),
            "best_pace_date": best_pace_date,
        }

    def get_calories_for_period(self, period: str) -> float:
        cursor = self.conn.cursor()
        if period == "week":
            date_filter = "date('now', '-7 days')"
        elif period == "month":
            date_filter = "date('now', '-30 days')"
        elif period == "year":
            date_filter = "date('now', '-365 days')"
        else:
            date_filter = "date('now', '-36500 days')"

        cursor.execute(f"""
            SELECT COALESCE(SUM(ws.calories), 0) as total_calories
            FROM workout_sets ws
            JOIN workout_exercises we ON ws.workout_exercise_id = we.id
            JOIN workouts w ON we.workout_id = w.id
            WHERE w.date >= {date_filter} AND ws.calories > 0
        """)
        return cursor.fetchone()["total_calories"]

    def get_weight_history(self, limit: int = 100) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT date, weight FROM body_metrics WHERE weight > 0 ORDER BY date DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_workout_frequency(self, period: str) -> List[Dict]:
        cursor = self.conn.cursor()
        if period == "week":
            rows = cursor.execute("""
                SELECT date, COUNT(*) as count FROM workouts
                WHERE date >= date('now', '-7 days')
                GROUP BY date ORDER BY date
            """).fetchall()
        elif period == "month":
            rows = cursor.execute("""
                SELECT date, COUNT(*) as count FROM workouts
                WHERE date >= date('now', '-30 days')
                GROUP BY date ORDER BY date
            """).fetchall()
        elif period == "year":
            rows = cursor.execute("""
                SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
                FROM workouts WHERE date >= date('now', '-365 days')
                GROUP BY month ORDER BY month
            """).fetchall()
        else:
            rows = []
        return [dict(row) for row in rows]

    def get_muscle_group_frequency(self, period: str) -> List[Dict]:
        cursor = self.conn.cursor()
        if period == "week":
            date_filter = "date('now', '-7 days')"
        elif period == "month":
            date_filter = "date('now', '-30 days')"
        elif period == "year":
            date_filter = "date('now', '-365 days')"
        else:
            return []
        rows = cursor.execute(f"""
            SELECT e.muscle_group, COUNT(*) as count
            FROM workout_sets ws
            JOIN workout_exercises we ON ws.workout_exercise_id = we.id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN workouts w ON we.workout_id = w.id
            WHERE w.date >= {date_filter}
            GROUP BY e.muscle_group ORDER BY count DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def get_all_personal_records(self) -> List[Dict]:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT pr.*, e.name as exercise_name
            FROM personal_records pr
            JOIN exercises e ON pr.exercise_id = e.id
            ORDER BY pr.date DESC LIMIT 10
        """).fetchall()
        return [dict(row) for row in rows]

    def get_workout_dates(self) -> List[str]:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT DISTINCT date FROM workouts ORDER BY date DESC
        """).fetchall()
        return [row["date"] for row in rows]

    def get_workout_dates_for_month(self, year: int, month: int) -> List[Dict]:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT DISTINCT date FROM workouts
            WHERE CAST(strftime('%Y', date) AS INTEGER) = ?
            AND CAST(strftime('%m', date) AS INTEGER) = ?
        """, (year, month)).fetchall()
        return [dict(row) for row in rows]

    def get_workouts_for_date(self, date_str: str) -> List[Dict]:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT * FROM workouts WHERE date = ? ORDER BY created_at
        """, (date_str,)).fetchall()
        return [dict(row) for row in rows]

    def get_workout_duration_trend(self, limit: int = 14) -> List[Dict]:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT date, duration FROM workouts
            WHERE duration > 0 ORDER BY date DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

    def get_volume_trend(self, limit: int = 14) -> List[Dict]:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT w.date, SUM(ws.weight * ws.reps) as volume
            FROM workout_sets ws
            JOIN workout_exercises we ON ws.workout_exercise_id = we.id
            JOIN workouts w ON we.workout_id = w.id
            WHERE ws.completed = 1 OR (ws.weight > 0 AND ws.reps > 0)
            GROUP BY w.date ORDER BY w.date DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

    def get_body_measurements_trend(self, limit: int = 10) -> Dict:
        cursor = self.conn.cursor()
        rows = cursor.execute("""
            SELECT date, chest, waist, hips, biceps_left, thighs_left
            FROM body_metrics
            WHERE chest > 0 OR waist > 0 OR hips > 0 OR biceps_left > 0 OR thighs_left > 0
            ORDER BY date DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

    def get_total_workouts(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM workouts")
        return cursor.fetchone()["total"]

    def get_total_sets(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM workout_sets")
        return cursor.fetchone()["total"]

    def get_longest_streak(self) -> int:
        dates = self.get_workout_dates()
        if not dates:
            return 0
        best = 0
        streak = 0
        sorted_dates = sorted(dates)
        for i, d in enumerate(sorted_dates):
            if i == 0:
                streak = 1
            else:
                prev = date.fromisoformat(sorted_dates[i - 1])
                curr = date.fromisoformat(d)
                if (curr - prev).days == 1:
                    streak += 1
                else:
                    streak = 1
            best = max(best, streak)
        return best

    def get_estimated_1rm_leaders(self, limit: int = 5) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.id, e.name, ws.weight, ws.reps, w.date,
                   CASE WHEN ws.reps > 1 THEN ws.weight * (1 + ws.reps / 30.0) ELSE ws.weight END as est_1rm
            FROM workout_sets ws
            JOIN workout_exercises we ON ws.workout_exercise_id = we.id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN workouts w ON we.workout_id = w.id
            WHERE ws.weight > 0 AND ws.reps > 0 AND ws.reps <= 12
            ORDER BY est_1rm DESC
            LIMIT ?
        """, (limit * 3,))
        rows = [dict(row) for row in cursor.fetchall()]

        best_by_exercise = {}
        for row in rows:
            ex_id = row["id"]
            if ex_id not in best_by_exercise or row["est_1rm"] > best_by_exercise[ex_id]["est_1rm"]:
                best_by_exercise[ex_id] = row

        leaders = sorted(best_by_exercise.values(), key=lambda x: x["est_1rm"], reverse=True)[:limit]
        return leaders

    # === Template Operations ===
    def create_template(self, name: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO workout_templates (name) VALUES (?)", (name,))
        self.conn.commit()
        return cursor.lastrowid

    def get_templates(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workout_templates ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def delete_template(self, template_id: int):
        self.conn.execute("DELETE FROM workout_templates WHERE id = ?", (template_id,))
        self.conn.commit()

    def save_workout_as_template(self, workout_id: int, template_name: str) -> int:
        template_id = self.create_template(template_name)
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM workout_exercises WHERE workout_id = ? ORDER BY order_num",
            (workout_id,)
        )
        exercises = cursor.fetchall()
        for we in exercises:
            cursor.execute(
                "INSERT INTO template_exercises (template_id, exercise_id, order_num) VALUES (?, ?, ?)",
                (template_id, we["exercise_id"], we["order_num"])
            )
            te_id = cursor.lastrowid
            cursor.execute(
                "SELECT * FROM workout_sets WHERE workout_exercise_id = ? ORDER BY set_number",
                (we["id"],)
            )
            sets = cursor.fetchall()
            for s in sets:
                cursor.execute(
                    "INSERT INTO template_sets (template_exercise_id, set_number, reps, weight, weight_unit, rest_time) VALUES (?, ?, ?, ?, ?, ?)",
                    (te_id, s["set_number"], s["reps"], s["weight"], s["weight_unit"], s["rest_time"])
                )
        self.conn.commit()
        return template_id

    def start_workout_from_template(self, template_id: int, workout_name: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workout_templates WHERE id = ?", (template_id,))
        template = cursor.fetchone()
        if not template:
            return None
        if not workout_name:
            workout_name = f"{template['name']} - {date.today().isoformat()}"
        workout_id = self.create_workout(workout_name)
        cursor.execute(
            "SELECT * FROM template_exercises WHERE template_id = ? ORDER BY order_num",
            (template_id,)
        )
        t_exercises = cursor.fetchall()
        for te in t_exercises:
            we_id = self.add_exercise_to_workout(workout_id, te["exercise_id"])
            cursor.execute(
                "SELECT * FROM template_sets WHERE template_exercise_id = ? ORDER BY set_number",
                (te["id"],)
            )
            t_sets = cursor.fetchall()
            for ts in t_sets:
                self.add_set(we_id, ts["set_number"], ts["reps"], ts["weight"], ts["weight_unit"], ts["rest_time"])
        return workout_id

    # === Weekly Plan Operations ===
    def _ensure_weekly_plan_days(self):
        cursor = self.conn.cursor()
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for day in days:
            cursor.execute("INSERT OR IGNORE INTO weekly_plan (day_of_week) VALUES (?)", (day,))
        self.conn.commit()

    def get_weekly_plan(self) -> Dict[str, List[Dict]]:
        self._ensure_weekly_plan_days()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM weekly_plan")
        plans = {row["day_of_week"]: {"id": row["id"], "exercises": []} for row in cursor.fetchall()}

        cursor.execute("""
            SELECT pe.*, e.name as exercise_name, e.muscle_group, e.category
            FROM plan_exercises pe
            JOIN exercises e ON pe.exercise_id = e.id
            ORDER BY pe.order_num
        """)
        for row in cursor.fetchall():
            for day_id, plan in plans.items():
                if plan["id"] == row["plan_id"]:
                    plan["exercises"].append(dict(row))
                    break

        return plans

    def add_exercise_to_plan(self, day_of_week: str, exercise_id: int, sets: int = 3, reps: str = "10") -> int:
        self._ensure_weekly_plan_days()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM weekly_plan WHERE day_of_week = ?", (day_of_week,))
        row = cursor.fetchone()
        if not row:
            return None
        plan_id = row["id"]

        cursor.execute("SELECT MAX(order_num) FROM plan_exercises WHERE plan_id = ?", (plan_id,))
        max_order = cursor.fetchone()[0] or 0

        cursor.execute(
            "INSERT INTO plan_exercises (plan_id, exercise_id, sets, reps, order_num) VALUES (?, ?, ?, ?, ?)",
            (plan_id, exercise_id, sets, reps, max_order + 1)
        )
        self.conn.commit()
        return cursor.lastrowid

    def remove_exercise_from_plan(self, plan_exercise_id: int):
        self.conn.execute("DELETE FROM plan_exercises WHERE id = ?", (plan_exercise_id,))
        self.conn.commit()

    def get_plan_exercises_for_day(self, day_of_week: str) -> List[Dict]:
        self._ensure_weekly_plan_days()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM weekly_plan WHERE day_of_week = ?", (day_of_week,))
        row = cursor.fetchone()
        if not row:
            return []
        plan_id = row["id"]

        cursor.execute("""
            SELECT pe.*, e.name as exercise_name, e.muscle_group, e.category
            FROM plan_exercises pe
            JOIN exercises e ON pe.exercise_id = e.id
            WHERE pe.plan_id = ?
            ORDER BY pe.order_num
        """, (plan_id,))
        return [dict(row) for row in cursor.fetchall()]

    def start_workout_from_plan(self, day_of_week: str) -> int:
        exercises = self.get_plan_exercises_for_day(day_of_week)
        if not exercises:
            return None

        workout_name = f"{day_of_week} Workout - {date.today().isoformat()}"
        workout_id = self.create_workout(workout_name)

        for pe in exercises:
            we_id = self.add_exercise_to_workout(workout_id, pe["exercise_id"])
            for s in range(1, pe["sets"] + 1):
                try:
                    reps_val = int(pe["reps"])
                except ValueError:
                    reps_val = 10
                self.add_set(we_id, s, reps=reps_val, weight=0, rest_time=60)

        return workout_id

    def close(self):
        self.conn.close()
