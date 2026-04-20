# widgets/calendar_widget.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.properties import ObjectProperty
import calendar
from datetime import date

dark_green_hex = '#485935'
light_green_hex = '#CADBB7'

class MonthCalendar(GridLayout):
    callback = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.rows = 7
        self.spacing = [2, 2]
        self.size_hint = (1, 1)
        self.selected_button = None
        
        # Заголовки дней недели
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day_name in weekdays:
            label = Label(
                text=day_name,
                size_hint_y=None,
                height=dp(30),
                color=get_color_from_hex(dark_green_hex),
                halign='center',
                valign='middle'
            )
            label.bind(size=label.setter('text_size')) 
            self.add_widget(label)
                
        # Ячейки для чисел месяца (всего 42)
        self.day_buttons = []
        for i in range(6 * 7):
            btn = Button(
                text='',
                background_normal='',
                background_color=get_color_from_hex('#FFFFFF'),
                color=get_color_from_hex(dark_green_hex),
                size_hint_y=None,
                height=dp(40),
                background_down = ''
            )
            btn.bind(on_release=self.on_button_press)
            self.add_widget(btn)
            self.day_buttons.append(btn)
        
        self.current_date = date.today()
        self.update_calendar()
    
    def on_button_press(self, instance):
        if hasattr(instance, 'day') and instance.day:
            if self.selected_button:
                self.selected_button.background_color = get_color_from_hex('#FFFFFF')
            instance.background_color = get_color_from_hex(light_green_hex)
            self.selected_button = instance
            if self.callback:
                self.callback(instance.day, instance.month, instance.year)
    
    def update_calendar(self):
        year = self.current_date.year
        month = self.current_date.month
        
        first_day_weekday, days_in_month = calendar.monthrange(year, month)
        start_offset = first_day_weekday  # 0 = понедельник
        
        day_num = 1
        for i, btn in enumerate(self.day_buttons):
            btn.text = ''
            btn.day = None
            btn.month = None
            btn.year = None
            
            if i >= start_offset and day_num <= days_in_month:
                btn.text = str(day_num)
                btn.day = day_num
                btn.month = month
                btn.year = year
                day_num += 1
        
        for btn in self.day_buttons:
            btn.background_color = get_color_from_hex('#FFFFFF')
    
    def go_prev_month(self):
        year = self.current_date.year
        month = self.current_date.month
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()
    
    def go_next_month(self):
        year = self.current_date.year
        month = self.current_date.month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()

    def go_prev_year(self):
        year = self.current_date.year
        month = self.current_date.month
        year -= 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()

    def go_next_year(self):
        year = self.current_date.year
        month = self.current_date.month
        year += 1
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()