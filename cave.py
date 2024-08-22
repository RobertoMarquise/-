import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import random
import os

class TimerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []  # Список для хранения истории сообщений
        self.load_history()  # Загружаем историю при инициализации
        self.messages = self.load_messages()  # Загружаем сообщения из файла

    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.timer_label = Label(text='ММ:СС или в секундах')
        self.layout.add_widget(self.timer_label)
        
        self.time_input = TextInput(hint_text='Отведенное время', multiline=False)
        self.layout.add_widget(self.time_input)
        
        self.start_button = Button(text='Старт')
        self.start_button.bind(on_press=self.start_timer)
        self.layout.add_widget(self.start_button)

        # Кнопка "Посмотреть историю"
        self.view_history_button = Button(text='Посмотреть галерею')
        self.view_history_button.bind(on_press=self.show_history)
        self.layout.add_widget(self.view_history_button)

        # Кнопка "Не сложилось" изначально отключена
        self.cancel_button = Button(text='Не сложилось', disabled=True)
        self.cancel_button.bind(on_press=self.cancel_timer)

        return self.layout

    def start_timer(self, instance):
        try:
            time_str = self.time_input.text.strip()
            if ':' in time_str:  # Проверяем, есть ли двоеточие
                minutes, seconds = map(int, time_str.split(':'))
                self.time_left = minutes * 60 + seconds  # Преобразуем в секунды
            else:
                self.time_left = int(time_str)  # Ввод в секундах
            
            if self.time_left < 5:  # Проверяем, больше ли время 5 секунд
                raise ValueError("Время должно быть не менее 5 секунд.")
            
            self.timer_label.text = f'Осталось времени: {self.time_left} секунд'
            self.start_button.disabled = True
            self.cancel_button.disabled = False  # Активируем кнопку "Не сложилось"
            self.layout.add_widget(self.cancel_button)  # Добавляем кнопку в layout
            self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        except ValueError as e:
            self.timer_label.text = str(e)

    def update_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.text = f'Осталось времени: {self.time_left} секунд'
        else:
            self.timer_event.cancel()
            self.show_result_buttons()

    def cancel_timer(self, instance):
        self.timer_event.cancel()  # Останавливаем таймер
        self.time_left = 0  # Обнуляем время
        self.timer_label.text = 'Таймер остановлен.'
        self.start_button.disabled = False  # Активируем кнопку "Старт"
        self.cancel_button.disabled = True  # Деактивируем кнопку "Не сложилось"
        self.layout.remove_widget(self.cancel_button)  # Убираем кнопку из layout
        self.show_main_screen()  # Возвращаемся к основному экрану

    def show_result_buttons(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text='Время'))
        
        done_button = Button(text='Дело сделано')
        done_button.bind(on_press=self.show_message)
        self.layout.add_widget(done_button)
        
        not_done_button = Button(text='Не сложилось')
        not_done_button.bind(on_press=self.cancel_timer)
        self.layout.add_widget(not_done_button)

    def show_message(self, instance):
        message = random.choice(self.messages)  # Используем загруженные сообщения
        #emoji_choice = random.choice(["😊", "🎉", "👍"])
        
        # Добавляем сообщение в историю
        self.history.append(f'{message}')
        self.save_history()  # Сохраняем историю в файл
        
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text=f'{message}'))
        
        # Добавляем кнопку для просмотра истории
        view_history_button = Button(text='Посмотреть галерею')
        view_history_button.bind(on_press=self.show_history)
        self.layout.add_widget(view_history_button)

    def show_history(self, instance):
        self.layout.clear_widgets()
        
        # Создаем вертикальный BoxLayout для отображения истории
        history_layout = BoxLayout(orientation='vertical')
        
        # Добавляем метку с заголовком
        history_layout.add_widget(Label(text='Галерея', size_hint_y=None, height=30))
        
        # Добавляем метки для каждого сообщения в истории
        for message in self.history:
            history_layout.add_widget(Label(text=message))
        
        # Добавляем кнопку для возврата к основному экрану
        back_button = Button(text='Назад')
        back_button.bind(on_press=self.show_main_screen)
        history_layout.add_widget(back_button)
        
        self.layout.add_widget(history_layout)

    def show_main_screen(self, instance=None):
        self.layout.clear_widgets()
        self.layout.add_widget(self.timer_label)
        self.layout.add_widget(self.time_input)
        self.layout.add_widget(self.start_button)
        self.layout.add_widget(self.view_history_button)  # Добавляем кнопку "Посмотреть историю" обратно
        
        # Сбрасываем состояние кнопок
        self.start_button.disabled = False
        self.cancel_button.disabled = True
        if self.cancel_button in self.layout.children:
            self.layout.remove_widget(self.cancel_button)  # Убираем кнопку "Не сложилось"

    def save_history(self):
        with open('history.json', 'w') as f:
            json.dump(self.history, f)

    def load_history(self):
        if os.path.exists('history.json'):
            with open('history.json', 'r') as f:
                self.history = json.load(f)

    def load_messages(self):
        if os.path.exists('messages.json'):
            with open('messages.json', 'r') as f:
                data = json.load(f)
                return data.get("messages", [])
        else:
            return ["Это начало"]  # Сообщения по умолчанию

if __name__ == '__main__':
    TimerApp().run()
