import json
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

Window.size = (360, 640)

KV = '''
<RecipeListScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Общежитский повар'
            size_hint_y: 0.11
            font_size: '28sp'
            bold: True
            color: 1, 0.8, 0.3, 1
        Label:
            text: 'Выбери блюдо:'
            size_hint_y: 0.05
            font_size: '16sp'
            color: 0.8, 0.8, 0.8, 1
        ScrollView:
            # Обертка для центрирования сетки
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                # Центрируем содержимое по горизонтали
                pos_hint: {'center_x': 0.5}
                size_hint_x: None
                width: self.minimum_width
                
                GridLayout:
                    id: recipes_grid
                    cols: 2
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(10)
                    row_default_height: dp(160)
                    row_force_default: True

<RecipeScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: 0.13
            padding: dp(8)
            spacing: dp(8)
            Button:
                text: '< Назад'
                size_hint_x: 0.32
                font_size: '18sp'
                background_normal: ''
                background_down: ''
                background_color: (0.95, 0.75, 0.35, 1)
                color: (0, 0, 0, 1)
                on_release: app.go_back()
            Label:
                text: root.title_text
                font_size: '21sp'
                bold: True
                color: 1, 0.8, 0.3, 1
                size_hint_x: 0.68
        Label:
            text: root.meta_text
            size_hint_y: 0.09
            font_size: '14sp'
            color: 0.75, 0.75, 0.75, 1
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(15)
                spacing: dp(12)
                Label:
                    text: 'Ингредиенты:'
                    size_hint_y: None
                    height: dp(34)
                    font_size: '20sp'
                    bold: True
                    color: 1, 0.8, 0.3, 1
                    text_size: self.width, None
                    halign: 'left'
                Label:
                    text: root.ingredients_text
                    size_hint_y: None
                    height: self.texture_size[1]
                    font_size: '17sp'
                    color: 0.95, 0.95, 0.95, 1
                    text_size: self.width, None
                    halign: 'left'
                Label:
                    text: 'Можно купить готовым (без готовки):'
                    size_hint_y: None
                    height: dp(34)
                    font_size: '18sp'
                    bold: True
                    color: 0.6, 0.9, 0.6, 1
                    text_size: self.width, None
                    halign: 'left'
                Label:
                    text: root.buy_text
                    size_hint_y: None
                    height: self.texture_size[1]
                    font_size: '17sp'
                    color: 0.85, 0.95, 0.85, 1
                    text_size: self.width, None
                    halign: 'left'
                Label:
                    text: 'Приготовление:'
                    size_hint_y: None
                    height: dp(34)
                    font_size: '20sp'
                    bold: True
                    color: 1, 0.8, 0.3, 1
                    text_size: self.width, None
                    halign: 'left'
                Label:
                    text: root.steps_text
                    size_hint_y: None
                    height: self.texture_size[1]
                    font_size: '17sp'
                    color: 0.95, 0.95, 0.95, 1
                    text_size: self.width, None
                    halign: 'left'
'''


class RoundedButton(Button):
    """Кнопка со скруглёнными углами."""
    radius = NumericProperty(dp(14))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        with self.canvas.before:
            self._color = Color(0.95, 0.75, 0.35, 1)
            self._rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[self.radius]
            )
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]


class RecipeListScreen(Screen):
    pass


class RecipeScreen(Screen):
    title_text = StringProperty('')
    meta_text = StringProperty('')
    ingredients_text = StringProperty('')
    buy_text = StringProperty('')
    steps_text = StringProperty('')


class CookDormApp(App):
    def build(self):
        self.title = 'Общежитский повар'
        self.sm = ScreenManager()
        self.list_screen = RecipeListScreen(name='list')
        self.recipe_screen = RecipeScreen(name='recipe')
        self.sm.add_widget(self.list_screen)
        self.sm.add_widget(self.recipe_screen)
        self.load_recipes()
        return self.sm

    def load_recipes(self):
        path = Path(__file__).parent / 'recipes.json'
        with open(path, encoding='utf-8') as f:
            self.recipes = json.load(f)

        grid = self.list_screen.ids.recipes_grid
        for r in self.recipes:
            grid.add_widget(self._make_recipe_button(r))

    def _make_recipe_button(self, recipe):
        tools = ', '.join(recipe.get('tools', []))
        # Используем markup для переноса текста
        text = (
            f"[b]{recipe['name']}[/b]\n"
            f"{recipe['time']} мин · {recipe['difficulty']}\n"
            f"[size=13sp]Оборудование: {tools}[/size]"
        )
        
        # Делаем кнопку фиксированного размера
        btn = RoundedButton(
            text=text,
            markup=True,
            size_hint=(None, None),
            size=(dp(155), dp(160)),
            font_size='16sp',
            color=(0, 0, 0, 1),
            halign='center',
            valign='middle',
        )
        # Включаем автоматический перенос строк внутри кнопки
        btn.text_size = (btn.width - dp(10), None)
        
        btn.bind(on_release=lambda *_: self.show_recipe(recipe))
        return btn

    def show_recipe(self, recipe):
        rs = self.recipe_screen
        rs.title_text = recipe['name']
        rs.meta_text = (
            f"{recipe['time']} мин  ·  {recipe['difficulty']}\n"
            f"Оборудование: {', '.join(recipe.get('tools', []))}"
        )
        rs.ingredients_text = '\n'.join(f'• {i}' for i in recipe['ingredients'])
        rs.buy_text = '\n'.join(f'• {i}' for i in recipe.get('buy', []))
        rs.steps_text = '\n\n'.join(
            f'{n}. {s}' for n, s in enumerate(recipe['steps'], 1)
        )
        self.sm.current = 'recipe'

    def go_back(self):
        self.sm.current = 'list'


if __name__ == '__main__':
    Builder.load_string(KV)
    CookDormApp().run()
