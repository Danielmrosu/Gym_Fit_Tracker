from datetime import date, timedelta
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock


class AddFoodPopup(Popup):
    def __init__(self, meal_type, on_save_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Add {meal_type}"
        self.size_hint = (0.85, 0.7)
        self.meal_type = meal_type
        self.on_save_callback = on_save_callback
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        content.add_widget(Label(
            text="Food Name",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20),
            halign="left"
        ))
        self.name_input = TextInput(
            hint_text="e.g., Chicken Breast",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        content.add_widget(self.name_input)

        macros_row = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(8))

        cal_box = BoxLayout(orientation="vertical")
        cal_box.add_widget(Label(text="Calories", font_size=dp(11), size_hint_y=None, height=dp(18)))
        self.cal_input = TextInput(hint_text="0", font_size=dp(14), input_filter="float", multiline=False, size_hint_y=None, height=dp(36))
        cal_box.add_widget(self.cal_input)
        macros_row.add_widget(cal_box)

        prot_box = BoxLayout(orientation="vertical")
        prot_box.add_widget(Label(text="Protein (g)", font_size=dp(11), size_hint_y=None, height=dp(18)))
        self.protein_input = TextInput(hint_text="0", font_size=dp(14), input_filter="float", multiline=False, size_hint_y=None, height=dp(36))
        prot_box.add_widget(self.protein_input)
        macros_row.add_widget(prot_box)

        carbs_box = BoxLayout(orientation="vertical")
        carbs_box.add_widget(Label(text="Carbs (g)", font_size=dp(11), size_hint_y=None, height=dp(18)))
        self.carbs_input = TextInput(hint_text="0", font_size=dp(14), input_filter="float", multiline=False, size_hint_y=None, height=dp(36))
        carbs_box.add_widget(self.carbs_input)
        macros_row.add_widget(carbs_box)

        fat_box = BoxLayout(orientation="vertical")
        fat_box.add_widget(Label(text="Fat (g)", font_size=dp(11), size_hint_y=None, height=dp(18)))
        self.fat_input = TextInput(hint_text="0", font_size=dp(14), input_filter="float", multiline=False, size_hint_y=None, height=dp(36))
        fat_box.add_widget(self.fat_input)
        macros_row.add_widget(fat_box)

        content.add_widget(macros_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Add", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _save(self, *args):
        app = App.get_running_app()
        name = self.name_input.text.strip()
        if not name:
            return

        try:
            calories = float(self.cal_input.text) if self.cal_input.text else 0
        except ValueError:
            calories = 0
        try:
            protein = float(self.protein_input.text) if self.protein_input.text else 0
        except ValueError:
            protein = 0
        try:
            carbs = float(self.carbs_input.text) if self.carbs_input.text else 0
        except ValueError:
            carbs = 0
        try:
            fat = float(self.fat_input.text) if self.fat_input.text else 0
        except ValueError:
            fat = 0

        app.db.add_nutrition_entry(
            self.meal_type, name, calories, protein, carbs, fat
        )
        self.dismiss()
        if self.on_save_callback:
            Clock.schedule_once(lambda dt: self.on_save_callback(), 0.1)


class AddWaterPopup(Popup):
    def __init__(self, on_save_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Add Water Intake"
        self.size_hint = (0.7, 0.4)
        self.on_save_callback = on_save_callback
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        content.add_widget(Label(
            text="Amount (ml)",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(24)
        ))

        self.amount_input = TextInput(
            text="250",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(44),
            input_filter="int",
            multiline=False,
            halign="center"
        )
        content.add_widget(self.amount_input)

        quick_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        for amount in [150, 250, 330, 500]:
            btn = Button(text=f"{amount}ml", font_size=dp(11))
            amt = amount
            btn.bind(on_press=lambda inst, a=amt: self._quick_add(a))
            quick_row.add_widget(btn)
        content.add_widget(quick_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        add = Button(text="Add", font_size=dp(14), background_color=(0.435, 0.545, 0.639, 1))
        add.bind(on_press=self._save)
        btn_row.add_widget(add)

        content.add_widget(btn_row)
        self.content = content

    def _quick_add(self, amount):
        app = App.get_running_app()
        app.db.add_water_intake(amount)
        self.dismiss()
        if self.on_save_callback:
            Clock.schedule_once(lambda dt: self.on_save_callback(), 0.1)

    def _save(self, *args):
        app = App.get_running_app()
        try:
            amount = int(self.amount_input.text) if self.amount_input.text else 0
        except ValueError:
            amount = 0

        if amount > 0:
            app.db.add_water_intake(amount)
        self.dismiss()
        if self.on_save_callback:
            Clock.schedule_once(lambda dt: self.on_save_callback(), 0.1)


class WaterEntriesPopup(Popup):
    def __init__(self, on_refresh_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Water Entries"
        self.size_hint = (0.75, 0.6)
        self.on_refresh_callback = on_refresh_callback
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        scroll = ScrollView()
        self.entries_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4)
        )
        self.entries_container.bind(minimum_height=self.entries_container.setter('height'))
        scroll.add_widget(self.entries_container)
        content.add_widget(scroll)

        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_color=(0.757, 0.267, 0.235, 1),
            color=(1, 1, 1, 1)
        )
        close_btn.bind(on_press=lambda x: self.dismiss())
        content.add_widget(close_btn)

        self.content = content
        self._load_entries()

    def _load_entries(self):
        app = App.get_running_app()
        water_entries = app.db.get_water_entries_for_date()
        self.entries_container.clear_widgets()

        if not water_entries:
            self.entries_container.add_widget(Label(
                text="No water entries today",
                font_size=dp(12),
                color=(0.48, 0.45, 0.41, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for entry in water_entries:
            row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
            row.add_widget(Label(
                text=f"{entry['amount_ml']}ml",
                font_size=dp(13),
                halign="left",
                size_hint_x=0.6
            ))
            del_btn = Button(
                text="Delete",
                size_hint_x=0.3,
                font_size=dp(11),
                background_color=(0.757, 0.267, 0.235, 1),
                color=(1, 1, 1, 1)
            )
            entry_id = entry["id"]
            del_btn.bind(on_press=lambda inst, eid=entry_id: self._delete_entry(eid))
            row.add_widget(del_btn)
            self.entries_container.add_widget(row)

    def _delete_entry(self, entry_id):
        app = App.get_running_app()
        app.db.delete_water_intake(entry_id)
        self._load_entries()
        if self.on_refresh_callback:
            self.on_refresh_callback()


class AddRecipePopup(Popup):
    def __init__(self, on_save_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Create Recipe"
        self.size_hint = (0.9, 0.85)
        self.on_save_callback = on_save_callback
        self.ingredients = []
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        content.add_widget(Label(
            text="Recipe Name",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20)
        ))
        self.name_input = TextInput(
            hint_text="e.g., Chicken Bowl",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        content.add_widget(self.name_input)

        content.add_widget(Label(
            text="Ingredients",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(24),
            halign="left"
        ))

        scroll = ScrollView()
        self.ingredients_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4)
        )
        self.ingredients_list.bind(minimum_height=self.ingredients_list.setter('height'))
        scroll.add_widget(self.ingredients_list)
        content.add_widget(scroll)

        self.totals_label = Label(
            text="Total: 0 cal | P: 0g | C: 0g | F: 0g",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(24),
            color=(0.478, 0.62, 0.435, 1)
        )
        content.add_widget(self.totals_label)

        add_ingredient_btn = Button(
            text="+ Add Ingredient",
            size_hint_y=None,
            height=dp(36),
            font_size=dp(13),
            background_color=(0.435, 0.545, 0.639, 1),
            color=(1, 1, 1, 1)
        )
        add_ingredient_btn.bind(on_press=self._show_add_ingredient)
        content.add_widget(add_ingredient_btn)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save Recipe", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _show_add_ingredient(self, *args):
        popup = _AddIngredientPopup(self._add_ingredient)
        popup.open()

    def _add_ingredient(self, name, calories, protein, carbs, fat):
        self.ingredients.append({
            "name": name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })
        self._refresh_ingredients()

    def _refresh_ingredients(self):
        self.ingredients_list.clear_widgets()
        total_cal = total_p = total_c = total_f = 0

        for i, ing in enumerate(self.ingredients):
            row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(6))

            row.add_widget(Label(
                text=f"{ing['name']}",
                font_size=dp(12),
                halign="left",
                size_hint_x=0.35
            ))
            row.add_widget(Label(
                text=f"{ing['calories']}cal",
                font_size=dp(11),
                size_hint_x=0.18
            ))
            row.add_widget(Label(
                text=f"P:{ing['protein']}g",
                font_size=dp(11),
                size_hint_x=0.17,
                color=(0.435, 0.545, 0.639, 1)
            ))

            edit_btn = Button(
                text="E",
                size_hint_x=0.1,
                font_size=dp(10),
                background_color=(0.435, 0.545, 0.639, 1),
                color=(1, 1, 1, 1)
            )
            idx = i
            edit_btn.bind(on_press=lambda inst, idx=idx: self._edit_ingredient(idx))
            row.add_widget(edit_btn)

            del_btn = Button(
                text="X",
                size_hint_x=0.1,
                font_size=dp(10),
                background_color=(0.757, 0.267, 0.235, 1),
                color=(1, 1, 1, 1)
            )
            idx = i
            del_btn.bind(on_press=lambda inst, idx=idx: self._remove_ingredient(idx))
            row.add_widget(del_btn)

            self.ingredients_list.add_widget(row)

            total_cal += ing["calories"]
            total_p += ing["protein"]
            total_c += ing["carbs"]
            total_f += ing["fat"]

        self.totals_label.text = f"Total: {int(total_cal)} cal | P: {total_p:.0f}g | C: {total_c:.0f}g | F: {total_f:.0f}g"

    def _remove_ingredient(self, index):
        if 0 <= index < len(self.ingredients):
            self.ingredients.pop(index)
            self._refresh_ingredients()

    def _edit_ingredient(self, index):
        if 0 <= index < len(self.ingredients):
            ing = self.ingredients[index]
            popup = _EditIngredientPopup(
                index, ing["name"], ing["calories"], ing["protein"], ing["carbs"], ing["fat"],
                self._update_ingredient
            )
            popup.open()

    def _update_ingredient(self, index, name, calories, protein, carbs, fat):
        if 0 <= index < len(self.ingredients):
            self.ingredients[index] = {
                "name": name,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat
            }
            self._refresh_ingredients()

    def _save(self, *args):
        app = App.get_running_app()
        name = self.name_input.text.strip()
        if not name:
            return

        recipe_id = app.db.add_recipe(name)
        for ing in self.ingredients:
            app.db.add_recipe_ingredient(
                recipe_id, ing["name"], ing["calories"],
                ing["protein"], ing["carbs"], ing["fat"]
            )

        self.dismiss()
        if self.on_save_callback:
            Clock.schedule_once(lambda dt: self.on_save_callback(), 0.1)


class EditRecipePopup(Popup):
    def __init__(self, recipe_id, on_save_callback, **kwargs):
        super().__init__(**kwargs)
        self.recipe_id = recipe_id
        self.title = "Edit Recipe"
        self.size_hint = (0.9, 0.85)
        self.on_save_callback = on_save_callback
        self.ingredients = []
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        app = App.get_running_app()
        recipe = [r for r in app.db.get_recipes() if r["id"] == self.recipe_id][0]

        content.add_widget(Label(
            text="Recipe Name",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20)
        ))
        self.name_input = TextInput(
            text=recipe["name"],
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        content.add_widget(self.name_input)

        content.add_widget(Label(
            text="Ingredients",
            font_size=dp(13),
            size_hint_y=None,
            height=dp(24),
            halign="left"
        ))

        scroll = ScrollView()
        self.ingredients_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(4)
        )
        self.ingredients_list.bind(minimum_height=self.ingredients_list.setter('height'))
        scroll.add_widget(self.ingredients_list)
        content.add_widget(scroll)

        self.totals_label = Label(
            text="Total: 0 cal | P: 0g | C: 0g | F: 0g",
            font_size=dp(12),
            size_hint_y=None,
            height=dp(24),
            color=(0.478, 0.62, 0.435, 1)
        )
        content.add_widget(self.totals_label)

        add_ingredient_btn = Button(
            text="+ Add Ingredient",
            size_hint_y=None,
            height=dp(36),
            font_size=dp(13),
            background_color=(0.435, 0.545, 0.639, 1),
            color=(1, 1, 1, 1)
        )
        add_ingredient_btn.bind(on_press=self._show_add_ingredient)
        content.add_widget(add_ingredient_btn)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save Changes", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

        existing_ingredients = app.db.get_recipe_ingredients(self.recipe_id)
        for ing in existing_ingredients:
            self.ingredients.append({
                "name": ing["name"],
                "calories": ing["calories"],
                "protein": ing["protein"],
                "carbs": ing["carbs"],
                "fat": ing["fat"]
            })
        self._refresh_ingredients()

    def _show_add_ingredient(self, *args):
        popup = _AddIngredientPopup(self._add_ingredient)
        popup.open()

    def _add_ingredient(self, name, calories, protein, carbs, fat):
        self.ingredients.append({
            "name": name,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        })
        self._refresh_ingredients()

    def _refresh_ingredients(self):
        self.ingredients_list.clear_widgets()
        total_cal = total_p = total_c = total_f = 0

        for i, ing in enumerate(self.ingredients):
            row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(6))

            row.add_widget(Label(
                text=f"{ing['name']}",
                font_size=dp(12),
                halign="left",
                size_hint_x=0.35
            ))
            row.add_widget(Label(
                text=f"{ing['calories']}cal",
                font_size=dp(11),
                size_hint_x=0.18
            ))
            row.add_widget(Label(
                text=f"P:{ing['protein']}g",
                font_size=dp(11),
                size_hint_x=0.17,
                color=(0.435, 0.545, 0.639, 1)
            ))

            edit_btn = Button(
                text="E",
                size_hint_x=0.1,
                font_size=dp(10),
                background_color=(0.435, 0.545, 0.639, 1),
                color=(1, 1, 1, 1)
            )
            idx = i
            edit_btn.bind(on_press=lambda inst, idx=idx: self._edit_ingredient(idx))
            row.add_widget(edit_btn)

            del_btn = Button(
                text="X",
                size_hint_x=0.1,
                font_size=dp(10),
                background_color=(0.757, 0.267, 0.235, 1),
                color=(1, 1, 1, 1)
            )
            idx = i
            del_btn.bind(on_press=lambda inst, idx=idx: self._remove_ingredient(idx))
            row.add_widget(del_btn)

            self.ingredients_list.add_widget(row)

            total_cal += ing["calories"]
            total_p += ing["protein"]
            total_c += ing["carbs"]
            total_f += ing["fat"]

        self.totals_label.text = f"Total: {int(total_cal)} cal | P: {total_p:.0f}g | C: {total_c:.0f}g | F: {total_f:.0f}g"

    def _remove_ingredient(self, index):
        if 0 <= index < len(self.ingredients):
            self.ingredients.pop(index)
            self._refresh_ingredients()

    def _edit_ingredient(self, index):
        if 0 <= index < len(self.ingredients):
            ing = self.ingredients[index]
            popup = _EditIngredientPopup(
                index, ing["name"], ing["calories"], ing["protein"], ing["carbs"], ing["fat"],
                self._update_ingredient
            )
            popup.open()

    def _update_ingredient(self, index, name, calories, protein, carbs, fat):
        if 0 <= index < len(self.ingredients):
            self.ingredients[index] = {
                "name": name,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat
            }
            self._refresh_ingredients()

    def _save(self, *args):
        app = App.get_running_app()
        name = self.name_input.text.strip()
        if not name:
            return

        app.db.delete_recipe(self.recipe_id)
        new_id = app.db.add_recipe(name)
        for ing in self.ingredients:
            app.db.add_recipe_ingredient(
                new_id, ing["name"], ing["calories"],
                ing["protein"], ing["carbs"], ing["fat"]
            )

        self.dismiss()
        if self.on_save_callback:
            Clock.schedule_once(lambda dt: self.on_save_callback(), 0.1)


FOOD_DATABASE = {
    # Meats
    "Chicken Breast": {"cal": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    "Chicken Thigh": {"cal": 209, "protein": 26, "carbs": 0, "fat": 10.9},
    "Ground Beef (lean)": {"cal": 250, "protein": 26, "carbs": 0, "fat": 15},
    "Ground Beef (80/20)": {"cal": 254, "protein": 17, "carbs": 0, "fat": 20},
    "Salmon": {"cal": 208, "protein": 20, "carbs": 0, "fat": 13},
    "Tuna (canned)": {"cal": 116, "protein": 26, "carbs": 0, "fat": 1},
    "Turkey Breast": {"cal": 135, "protein": 30, "carbs": 0, "fat": 1},
    "Pork Loin": {"cal": 143, "protein": 26, "carbs": 0, "fat": 3.5},
    "Beef Steak (sirloin)": {"cal": 183, "protein": 27, "carbs": 0, "fat": 8},
    "Shrimp": {"cal": 99, "protein": 24, "carbs": 0, "fat": 0.3},
    "Eggs": {"cal": 155, "protein": 13, "carbs": 1.1, "fat": 11},
    "Whole Egg": {"cal": 155, "protein": 13, "carbs": 1.1, "fat": 11},
    "Egg Whites": {"cal": 52, "protein": 11, "carbs": 0.7, "fat": 0.2},
    # Dairy
    "Greek Yogurt": {"cal": 59, "protein": 10, "carbs": 3.6, "fat": 0.4},
    "Cottage Cheese": {"cal": 98, "protein": 11, "carbs": 3.4, "fat": 4.3},
    "Milk (whole)": {"cal": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3},
    "Milk (skim)": {"cal": 34, "protein": 3.4, "carbs": 5, "fat": 0.1},
    "Cheese (cheddar)": {"cal": 403, "protein": 25, "carbs": 1.3, "fat": 33},
    "Mozzarella": {"cal": 280, "protein": 28, "carbs": 3.1, "fat": 17},
    "Whey Protein": {"cal": 352, "protein": 80, "carbs": 8, "fat": 1.5},
    # Carbs
    "White Rice (cooked)": {"cal": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    "Brown Rice (cooked)": {"cal": 112, "protein": 2.6, "carbs": 24, "fat": 0.9},
    "Oatmeal (cooked)": {"cal": 71, "protein": 2.5, "carbs": 12, "fat": 1.5},
    "Oats (dry)": {"cal": 389, "protein": 17, "carbs": 66, "fat": 7},
    "Pasta (cooked)": {"cal": 131, "protein": 5, "carbs": 25, "fat": 1.1},
    "Bread (white)": {"cal": 265, "protein": 9, "carbs": 49, "fat": 3.2},
    "Bread (whole wheat)": {"cal": 247, "protein": 13, "carbs": 41, "fat": 3.4},
    "Sweet Potato": {"cal": 86, "protein": 1.6, "carbs": 20, "fat": 0.1},
    "Potato": {"cal": 77, "protein": 2, "carbs": 17, "fat": 0.1},
    "Quinoa (cooked)": {"cal": 120, "protein": 4.4, "carbs": 21, "fat": 1.9},
    "Bread (toast)": {"cal": 265, "protein": 9, "carbs": 49, "fat": 3.2},
    # Fruits
    "Banana": {"cal": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
    "Apple": {"cal": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    "Orange": {"cal": 47, "protein": 0.9, "carbs": 12, "fat": 0.1},
    "Blueberries": {"cal": 57, "protein": 0.7, "carbs": 14, "fat": 0.3},
    "Strawberries": {"cal": 32, "protein": 0.7, "carbs": 8, "fat": 0.3},
    "Grapes": {"cal": 69, "protein": 0.7, "carbs": 18, "fat": 0.2},
    "Mango": {"cal": 60, "protein": 0.8, "carbs": 15, "fat": 0.4},
    "Pineapple": {"cal": 50, "protein": 0.5, "carbs": 13, "fat": 0.1},
    "Watermelon": {"cal": 30, "protein": 0.6, "carbs": 8, "fat": 0.2},
    "Kiwi": {"cal": 61, "protein": 1.1, "carbs": 15, "fat": 0.5},
    # Vegetables
    "Broccoli": {"cal": 34, "protein": 2.8, "carbs": 7, "fat": 0.4},
    "Spinach": {"cal": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
    "Carrots": {"cal": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
    "Bell Pepper": {"cal": 31, "protein": 1, "carbs": 6, "fat": 0.3},
    "Tomato": {"cal": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "Cucumber": {"cal": 16, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
    "Lettuce": {"cal": 15, "protein": 1.4, "carbs": 2.9, "fat": 0.2},
    "Avocado": {"cal": 160, "protein": 2, "carbs": 9, "fat": 15},
    "Mushrooms": {"cal": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3},
    "Onion": {"cal": 40, "protein": 1.1, "carbs": 9, "fat": 0.1},
    # Nuts & Seeds
    "Almonds": {"cal": 579, "protein": 21, "carbs": 22, "fat": 50},
    "Peanut Butter": {"cal": 588, "protein": 25, "carbs": 20, "fat": 50},
    "Peanuts": {"cal": 567, "protein": 26, "carbs": 16, "fat": 49},
    "Walnuts": {"cal": 654, "protein": 15, "carbs": 14, "fat": 65},
    "Cashews": {"cal": 553, "protein": 18, "carbs": 30, "fat": 44},
    "Chia Seeds": {"cal": 486, "protein": 17, "carbs": 42, "fat": 31},
    "Flax Seeds": {"cal": 534, "protein": 18, "carbs": 29, "fat": 42},
    "Sunflower Seeds": {"cal": 584, "protein": 21, "carbs": 20, "fat": 51},
    # Legumes
    "Black Beans (cooked)": {"cal": 132, "protein": 8.9, "carbs": 24, "fat": 0.5},
    "Lentils (cooked)": {"cal": 116, "protein": 9, "carbs": 20, "fat": 0.4},
    "Chickpeas (cooked)": {"cal": 164, "protein": 8.9, "carbs": 27, "fat": 2.6},
    "Kidney Beans": {"cal": 127, "protein": 8.7, "carbs": 23, "fat": 0.5},
    "Hummus": {"cal": 166, "protein": 7.9, "carbs": 14, "fat": 9.6},
    # Oils & Fats
    "Olive Oil": {"cal": 884, "protein": 0, "carbs": 0, "fat": 100},
    "Coconut Oil": {"cal": 862, "protein": 0, "carbs": 0, "fat": 100},
    "Butter": {"cal": 717, "protein": 0.9, "carbs": 0.1, "fat": 81},
    # Misc
    "Honey": {"cal": 304, "protein": 0.3, "carbs": 82, "fat": 0},
    "Dark Chocolate (70%)": {"cal": 598, "protein": 8, "carbs": 46, "fat": 43},
    "Protein Bar": {"cal": 350, "protein": 20, "carbs": 40, "fat": 12},
    "Tortilla (flour)": {"cal": 312, "protein": 8, "carbs": 52, "fat": 8},
    "Rice Cakes": {"cal": 387, "protein": 8, "carbs": 81, "fat": 2.8},
}


class _CustomIngredientPopup(Popup):
    def __init__(self, on_add_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Custom Ingredient"
        self.size_hint = (0.85, 0.65)
        self.on_add_callback = on_add_callback
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        content.add_widget(Label(text="Ingredient Name", font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.name_input = TextInput(hint_text="e.g., Custom Sauce", font_size=dp(14), size_hint_y=None, height=dp(36), multiline=False)
        content.add_widget(self.name_input)

        content.add_widget(Label(text="Per 100g", font_size=dp(11), size_hint_y=None, height=dp(18), color=(0.658, 0.631, 0.588, 1)))

        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))

        cal_box = BoxLayout(orientation="vertical")
        cal_box.add_widget(Label(text="Cal", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.cal_input = TextInput(hint_text="0", font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        cal_box.add_widget(self.cal_input)
        row.add_widget(cal_box)

        prot_box = BoxLayout(orientation="vertical")
        prot_box.add_widget(Label(text="Protein", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.protein_input = TextInput(hint_text="0", font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        prot_box.add_widget(self.protein_input)
        row.add_widget(prot_box)

        carbs_box = BoxLayout(orientation="vertical")
        carbs_box.add_widget(Label(text="Carbs", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.carbs_input = TextInput(hint_text="0", font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        carbs_box.add_widget(self.carbs_input)
        row.add_widget(carbs_box)

        fat_box = BoxLayout(orientation="vertical")
        fat_box.add_widget(Label(text="Fat", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.fat_input = TextInput(hint_text="0", font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        fat_box.add_widget(self.fat_input)
        row.add_widget(fat_box)

        content.add_widget(row)

        content.add_widget(Label(text="Weight (g)", font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.weight_input = TextInput(text="100", font_size=dp(14), size_hint_y=None, height=dp(36), input_filter="float", multiline=False, halign="center")
        self.weight_input.bind(text=self._on_weight_change)
        content.add_widget(self.weight_input)

        result_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(6))
        self.result_cal = Label(text="0cal", font_size=dp(11))
        result_row.add_widget(self.result_cal)
        self.result_prot = Label(text="P:0g", font_size=dp(11), color=(0.435, 0.545, 0.639, 1))
        result_row.add_widget(self.result_prot)
        self.result_carbs = Label(text="C:0g", font_size=dp(11), color=(0.788, 0.635, 0.294, 1))
        result_row.add_widget(self.result_carbs)
        self.result_fat = Label(text="F:0g", font_size=dp(11), color=(0.658, 0.631, 0.588, 1))
        result_row.add_widget(self.result_fat)
        content.add_widget(result_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(13))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        add = Button(text="Add", font_size=dp(13), background_color=(0.435, 0.545, 0.639, 1))
        add.bind(on_press=self._add)
        btn_row.add_widget(add)

        content.add_widget(btn_row)
        self.content = content

    def _on_weight_change(self, instance, text):
        try:
            weight = float(text) if text else 100
        except ValueError:
            weight = 100
        try:
            cal_per100 = float(self.cal_input.text) if self.cal_input.text else 0
        except ValueError:
            cal_per100 = 0
        try:
            prot_per100 = float(self.protein_input.text) if self.protein_input.text else 0
        except ValueError:
            prot_per100 = 0
        try:
            carbs_per100 = float(self.carbs_input.text) if self.carbs_input.text else 0
        except ValueError:
            carbs_per100 = 0
        try:
            fat_per100 = float(self.fat_input.text) if self.fat_input.text else 0
        except ValueError:
            fat_per100 = 0

        factor = weight / 100.0
        self.result_cal.text = f"{int(cal_per100 * factor)}cal"
        self.result_prot.text = f"P:{prot_per100 * factor:.1f}g"
        self.result_carbs.text = f"C:{carbs_per100 * factor:.1f}g"
        self.result_fat.text = f"F:{fat_per100 * factor:.1f}g"

    def _add(self, *args):
        name = self.name_input.text.strip()
        if not name:
            return
        try:
            cal = float(self.cal_input.text) if self.cal_input.text else 0
        except ValueError:
            cal = 0
        try:
            prot = float(self.protein_input.text) if self.protein_input.text else 0
        except ValueError:
            prot = 0
        try:
            carbs = float(self.carbs_input.text) if self.carbs_input.text else 0
        except ValueError:
            carbs = 0
        try:
            fat = float(self.fat_input.text) if self.fat_input.text else 0
        except ValueError:
            fat = 0
        try:
            weight = float(self.weight_input.text) if self.weight_input.text else 100
        except ValueError:
            weight = 100

        factor = weight / 100.0
        cal *= factor
        prot *= factor
        carbs *= factor
        fat *= factor

        display_name = f"{name} ({int(weight)}g)" if weight != 100 else name
        self.on_add_callback(display_name, cal, prot, carbs, fat)
        self.dismiss()


class _AddIngredientPopup(Popup):
    def __init__(self, on_add_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = "Add Ingredient"
        self.size_hint = (0.9, 0.85)
        self.on_add_callback = on_add_callback
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        content.add_widget(Label(text="Search Food", font_size=dp(13), size_hint_y=None, height=dp(20)))

        self.search_input = TextInput(
            hint_text="Type to search...",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(36),
            multiline=False
        )
        self.search_input.bind(text=self._on_search)
        content.add_widget(self.search_input)

        food_scroll = ScrollView()
        self.food_list = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2)
        )
        self.food_list.bind(minimum_height=self.food_list.setter('height'))
        food_scroll.add_widget(self.food_list)
        content.add_widget(food_scroll)

        self._populate_foods("")

        content.add_widget(Label(text="Weight (g)", font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.weight_input = TextInput(
            text="100",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(36),
            input_filter="float",
            multiline=False,
            halign="center"
        )
        self.weight_input.bind(text=self._on_weight_change)
        content.add_widget(self.weight_input)

        result_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))

        self.result_cal = Label(text="0cal", font_size=dp(11))
        result_row.add_widget(self.result_cal)
        self.result_prot = Label(text="P:0g", font_size=dp(11), color=(0.435, 0.545, 0.639, 1))
        result_row.add_widget(self.result_prot)
        self.result_carbs = Label(text="C:0g", font_size=dp(11), color=(0.788, 0.635, 0.294, 1))
        result_row.add_widget(self.result_carbs)
        self.result_fat = Label(text="F:0g", font_size=dp(11), color=(0.658, 0.631, 0.588, 1))
        result_row.add_widget(self.result_fat)
        content.add_widget(result_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(13))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        add = Button(text="Add", font_size=dp(13), background_color=(0.435, 0.545, 0.639, 1))
        add.bind(on_press=self._add)
        btn_row.add_widget(add)

        content.add_widget(btn_row)
        self.content = content
        self.selected_food = None

    def _on_search(self, instance, text):
        self._populate_foods(text)

    def _populate_foods(self, query):
        self.food_list.clear_widgets()
        query = query.lower()

        custom_btn = Button(
            text="+ Custom Ingredient (not in list)",
            size_hint_y=None,
            height=dp(36),
            font_size=dp(12),
            bold=True,
            background_color=(0.478, 0.62, 0.435, 1),
            color=(1, 1, 1, 1)
        )
        custom_btn.bind(on_press=self._open_custom)
        self.food_list.add_widget(custom_btn)

        foods = sorted(FOOD_DATABASE.keys())

        for food_name in foods:
            if query and query not in food_name.lower():
                continue
            data = FOOD_DATABASE[food_name]
            btn = Button(
                text=f"{food_name}  ({data['cal']}cal P:{data['protein']}g C:{data['carbs']}g F:{data['fat']}g)",
                size_hint_y=None,
                height=dp(32),
                font_size=dp(10),
                halign="left",
                background_color=(0.33, 0.31, 0.27, 1),
                color=(0.95, 0.93, 0.88, 1)
            )
            btn.bind(on_press=lambda inst, fn=food_name: self._select_food(fn))
            self.food_list.add_widget(btn)

    def _open_custom(self, *args):
        popup = _CustomIngredientPopup(self._on_custom_add)
        popup.open()

    def _on_custom_add(self, name, cal, prot, carbs, fat):
        self.on_add_callback(name, cal, prot, carbs, fat)
        self.dismiss()

    def _select_food(self, food_name):
        self.selected_food = food_name
        self.search_input.text = food_name
        self.food_list.clear_widgets()
        self._on_weight_change(None, self.weight_input.text)

    def _on_weight_change(self, instance, text):
        if not self.selected_food:
            return
        try:
            weight = float(text) if text else 0
        except ValueError:
            weight = 0

        data = FOOD_DATABASE[self.selected_food]
        factor = weight / 100.0

        cal = data["cal"] * factor
        prot = data["protein"] * factor
        carbs = data["carbs"] * factor
        fat = data["fat"] * factor

        self.result_cal.text = f"{int(cal)}cal"
        self.result_prot.text = f"P:{prot:.1f}g"
        self.result_carbs.text = f"C:{carbs:.1f}g"
        self.result_fat.text = f"F:{fat:.1f}g"

    def _add(self, *args):
        if not self.selected_food:
            return
        try:
            weight = float(self.weight_input.text) if self.weight_input.text else 0
        except ValueError:
            weight = 0

        data = FOOD_DATABASE[self.selected_food]
        factor = weight / 100.0

        cal = data["cal"] * factor
        prot = data["protein"] * factor
        carbs = data["carbs"] * factor
        fat = data["fat"] * factor

        name = f"{self.selected_food} ({int(weight)}g)"
        self.on_add_callback(name, cal, prot, carbs, fat)
        self.dismiss()


class _EditIngredientPopup(Popup):
    def __init__(self, index, name, calories, protein, carbs, fat, on_update_callback, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.title = "Edit Ingredient"
        self.size_hint = (0.8, 0.55)
        self.on_update_callback = on_update_callback
        self._build_content(name, calories, protein, carbs, fat)

    def _build_content(self, name, calories, protein, carbs, fat):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        content.add_widget(Label(text="Ingredient Name", font_size=dp(13), size_hint_y=None, height=dp(20)))
        self.name_input = TextInput(text=name, font_size=dp(14), size_hint_y=None, height=dp(36), multiline=False)
        content.add_widget(self.name_input)

        row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(6))

        cal_box = BoxLayout(orientation="vertical")
        cal_box.add_widget(Label(text="Cal", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.cal_input = TextInput(text=str(calories), font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        cal_box.add_widget(self.cal_input)
        row.add_widget(cal_box)

        prot_box = BoxLayout(orientation="vertical")
        prot_box.add_widget(Label(text="Protein", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.protein_input = TextInput(text=str(protein), font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        prot_box.add_widget(self.protein_input)
        row.add_widget(prot_box)

        carbs_box = BoxLayout(orientation="vertical")
        carbs_box.add_widget(Label(text="Carbs", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.carbs_input = TextInput(text=str(carbs), font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        carbs_box.add_widget(self.carbs_input)
        row.add_widget(carbs_box)

        fat_box = BoxLayout(orientation="vertical")
        fat_box.add_widget(Label(text="Fat", font_size=dp(10), size_hint_y=None, height=dp(16)))
        self.fat_input = TextInput(text=str(fat), font_size=dp(13), input_filter="float", multiline=False, size_hint_y=None, height=dp(30))
        fat_box.add_widget(self.fat_input)
        row.add_widget(fat_box)

        content.add_widget(row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(13))
        cancel.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save", font_size=dp(13), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=self._save)
        btn_row.add_widget(save)

        content.add_widget(btn_row)
        self.content = content

    def _save(self, *args):
        name = self.name_input.text.strip()
        if not name:
            return
        try:
            cal = float(self.cal_input.text) if self.cal_input.text else 0
        except ValueError:
            cal = 0
        try:
            prot = float(self.protein_input.text) if self.protein_input.text else 0
        except ValueError:
            prot = 0
        try:
            carbs = float(self.carbs_input.text) if self.carbs_input.text else 0
        except ValueError:
            carbs = 0
        try:
            fat = float(self.fat_input.text) if self.fat_input.text else 0
        except ValueError:
            fat = 0

        self.on_update_callback(self.index, name, cal, prot, carbs, fat)
        self.dismiss()


class RecipeListPopup(Popup):
    def __init__(self, meal_type, on_select_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Select Recipe for {meal_type}"
        self.size_hint = (0.85, 0.75)
        self.meal_type = meal_type
        self.on_select_callback = on_select_callback
        self._build_content()

    def _build_content(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))

        scroll = ScrollView()
        self.recipes_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(6)
        )
        self.recipes_container.bind(minimum_height=self.recipes_container.setter('height'))
        scroll.add_widget(self.recipes_container)
        content.add_widget(scroll)

        btn_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        close = Button(text="Close", font_size=dp(13))
        close.bind(on_press=lambda x: self.dismiss())
        btn_row.add_widget(close)
        content.add_widget(btn_row)

        self.content = content
        self._load_recipes()

    def _load_recipes(self):
        app = App.get_running_app()
        recipes = app.db.get_recipes()
        self.recipes_container.clear_widgets()

        if not recipes:
            self.recipes_container.add_widget(Label(
                text="No recipes yet. Create one first!",
                font_size=dp(12),
                color=(0.48, 0.45, 0.41, 1),
                size_hint_y=None,
                height=dp(50)
            ))
            return

        for recipe in recipes:
            totals = app.db.get_recipe_totals(recipe["id"])

            row = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))

            info = BoxLayout(orientation="vertical", size_hint_x=0.65)
            info.add_widget(Label(
                text=recipe["name"],
                font_size=dp(13),
                bold=True,
                halign="left",
                size_hint_y=None,
                height=dp(22)
            ))
            info.add_widget(Label(
                text=f"{int(totals['total_calories'])}cal | P:{totals['total_protein']:.0f}g | C:{totals['total_carbs']:.0f}g | F:{totals['total_fat']:.0f}g",
                font_size=dp(10),
                halign="left",
                size_hint_y=None,
                height=dp(18),
                color=(0.658, 0.631, 0.588, 1)
            ))
            row.add_widget(info)

            use_btn = Button(
                text="Use",
                size_hint_x=0.2,
                font_size=dp(12),
                background_color=(0.478, 0.62, 0.435, 1),
                color=(1, 1, 1, 1)
            )
            rid = recipe["id"]
            rname = recipe["name"]
            use_btn.bind(on_press=lambda inst, r=rid, n=rname: self._use_recipe(r, n))
            row.add_widget(use_btn)

            edit_btn = Button(
                text="Edit",
                size_hint_x=0.15,
                font_size=dp(12),
                background_color=(0.435, 0.545, 0.639, 1),
                color=(1, 1, 1, 1)
            )
            edit_btn.bind(on_press=lambda inst, r=rid: self._edit_recipe(r))
            row.add_widget(edit_btn)

            del_btn = Button(
                text="X",
                size_hint_x=0.1,
                font_size=dp(11),
                background_color=(0.757, 0.267, 0.235, 1),
                color=(1, 1, 1, 1)
            )
            del_btn.bind(on_press=lambda inst, r=rid: self._delete_recipe(r))
            row.add_widget(del_btn)

            self.recipes_container.add_widget(row)

    def _use_recipe(self, recipe_id, recipe_name):
        app = App.get_running_app()
        ingredients = app.db.get_recipe_ingredients(recipe_id)
        total_cal = sum(i["calories"] for i in ingredients)
        total_p = sum(i["protein"] for i in ingredients)
        total_c = sum(i["carbs"] for i in ingredients)
        total_f = sum(i["fat"] for i in ingredients)

        app.db.add_nutrition_entry(
            self.meal_type, recipe_name, total_cal, total_p, total_c, total_f
        )
        self.dismiss()
        if self.on_select_callback:
            Clock.schedule_once(lambda dt: self.on_select_callback(), 0.1)

    def _delete_recipe(self, recipe_id):
        app = App.get_running_app()
        app.db.delete_recipe(recipe_id)
        self._load_recipes()

    def _edit_recipe(self, recipe_id):
        self.dismiss()
        popup = EditRecipePopup(recipe_id, self.on_select_callback)
        popup.open()


class NutritionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = date.today().isoformat()

    def on_enter(self):
        self._load_data()

    def _load_data(self):
        app = App.get_running_app()
        summary = app.db.get_daily_nutrition_summary(self.current_date)
        entries = app.db.get_nutrition_entries_for_date(self.current_date)
        water = app.db.get_water_intake_for_date(self.current_date)
        water_goal = app.db.get_water_goal()
        water_entries = app.db.get_water_entries_for_date(self.current_date)

        self.ids.date_label.text = self._format_date(self.current_date)
        self.ids.total_calories.text = f"{summary['total_calories']:.0f}"
        self.ids.total_protein.text = f"{summary['total_protein']:.0f}g"
        self.ids.total_carbs.text = f"{summary['total_carbs']:.0f}g"
        self.ids.total_fat.text = f"{summary['total_fat']:.0f}g"
        self.ids.water_total.text = f"{water}ml / {water_goal}ml"

        percent = min(100, int((water / water_goal) * 100)) if water_goal > 0 else 0
        self.ids.water_percent.text = f"{percent}%"
        self.ids.water_goal_label.text = f"Goal: {water_goal}ml"

        for meal_type in ["Breakfast", "Lunch", "Dinner", "Snacks"]:
            container_id = f"{meal_type.lower()}_container"
            if container_id in self.ids:
                container = self.ids[container_id]
                container.clear_widgets()
                meal_entries = [e for e in entries if e["meal_type"] == meal_type]
                for entry in meal_entries:
                    row = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(8))
                    row.add_widget(Label(
                        text=f"{entry['name']} - {entry['calories']:.0f}cal (P:{entry['protein']:.0f} C:{entry['carbs']:.0f} F:{entry['fat']:.0f})",
                        font_size=dp(11),
                        halign="left",
                        size_hint_x=0.75
                    ))
                    del_btn = Button(
                        text="X",
                        size_hint_x=0.15,
                        font_size=dp(10),
                        background_color=(0.757, 0.267, 0.235, 1),
                        color=(1, 1, 1, 1)
                    )
                    entry_id = entry["id"]
                    del_btn.bind(on_press=lambda inst, eid=entry_id: self._delete_entry(eid))
                    row.add_widget(del_btn)
                    container.add_widget(row)

                if not meal_entries:
                    container.add_widget(Label(
                        text="No entries",
                        font_size=dp(11),
                        color=(0.48, 0.45, 0.41, 1),
                        size_hint_y=None,
                        height=dp(28)
                    ))

    def _format_date(self, date_str):
        d = date.fromisoformat(date_str)
        today = date.today()
        if d == today:
            return "Today"
        elif d == today - timedelta(days=1):
            return "Yesterday"
        return d.strftime("%a, %d %b")

    def prev_day(self):
        d = date.fromisoformat(self.current_date) - timedelta(days=1)
        self.current_date = d.isoformat()
        self._load_data()

    def next_day(self):
        d = date.fromisoformat(self.current_date) + timedelta(days=1)
        if d <= date.today():
            self.current_date = d.isoformat()
            self._load_data()

    def add_food(self, meal_type):
        popup = AddFoodPopup(meal_type, self._load_data)
        popup.open()

    def add_water(self):
        popup = AddWaterPopup(self._load_data)
        popup.open()

    def show_water_entries(self):
        popup = WaterEntriesPopup(self._load_data)
        popup.open()

    def show_recipes(self, meal_type):
        popup = RecipeListPopup(meal_type, self._load_data)
        popup.open()

    def create_recipe(self):
        popup = AddRecipePopup(self._load_data)
        popup.open()

    def _delete_entry(self, entry_id):
        app = App.get_running_app()
        app.db.delete_nutrition_entry(entry_id)
        self._load_data()

    def _delete_water(self, entry_id):
        app = App.get_running_app()
        app.db.delete_water_intake(entry_id)
        self._load_data()

    def set_water_goal(self):
        app = App.get_running_app()
        current_goal = app.db.get_water_goal()

        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(Label(
            text="Daily Water Goal (ml)",
            font_size=dp(14),
            size_hint_y=None,
            height=dp(24)
        ))

        goal_input = TextInput(
            text=str(current_goal),
            font_size=dp(18),
            size_hint_y=None,
            height=dp(44),
            input_filter="int",
            multiline=False,
            halign="center"
        )
        content.add_widget(goal_input)

        quick_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        for goal in [1500, 2000, 2500, 3000]:
            btn = Button(text=f"{goal}ml", font_size=dp(11))
            g = goal
            btn.bind(on_press=lambda inst, val=g: self._apply_goal(val))
            quick_row.add_widget(btn)
        content.add_widget(quick_row)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
        cancel = Button(text="Cancel", font_size=dp(14))
        cancel.bind(on_press=lambda x: self._goal_popup.dismiss())
        btn_row.add_widget(cancel)

        save = Button(text="Save", font_size=dp(14), background_color=(0.478, 0.62, 0.435, 1))
        save.bind(on_press=lambda inst: self._apply_goal(int(goal_input.text) if goal_input.text else 2000))
        btn_row.add_widget(save)

        content.add_widget(btn_row)

        self._goal_popup = Popup(
            title="Set Water Goal",
            content=content,
            size_hint=(0.75, 0.5)
        )
        self._goal_popup.open()

    def _apply_goal(self, goal):
        app = App.get_running_app()
        app.db.set_water_goal(goal)
        if self._goal_popup:
            self._goal_popup.dismiss()
        self._load_data()
