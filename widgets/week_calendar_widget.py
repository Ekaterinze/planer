# widgets/calendar_widget.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.properties import ObjectProperty
import calendar
from datetime import date
from widgets.variables import dark_accent_hex, light_accent_hex, dark_hex, light_hex

light_color = get_color_from_hex(light_hex)
dark_color = get_color_from_hex(dark_hex)
light_accent_color = get_color_from_hex(light_accent_hex)

class WeekCalendar(GridLayout):
    callback = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.rows = 2
        self.spacing = [2, 2]
        self.size_hint = (1, None) 
        self.height = dp(70) 
        self.selected_button = None
        self.md_bg_color = light_color
        
        # Заголовки дней недели
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day_name in weekdays:
            label = Label(
                text=day_name,
                size_hint_y=None,
                height=dp(30),
                color=dark_color,
                halign='center',
                valign='middle'
            )
            label.bind(size=label.setter('text_size')) 
            self.add_widget(label)

        self.current_date = date.today()
                
        self.day_buttons = []
        for i in range(7):
            btn = Button(
                text='',
                background_normal='',
                background_color=light_color,
                color=dark_color,
                size_hint_y=None,
                height=dp(40),
                background_down = ''
            )
            btn.bind(on_release=self.on_button_press)
            self.add_widget(btn)
            self.day_buttons.append(btn)
        
        self.update_calendar()
    
    def on_button_press(self, instance):
        if hasattr(instance, 'day') and instance.day:
            self.current_date = date(instance.year, instance.month, instance.day)
            self.update_calendar()
            if self.callback:
                self.callback(instance.day, instance.month, instance.year)
    
    def update_calendar(self):
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        
        first_day_weekday, days_in_month = calendar.monthrange(year, month)

        day_num = None
        for i in range (0,4):
            current_start_day = i*7+8 - first_day_weekday
            if current_start_day <= days_in_month and day-current_start_day<7 and day-current_start_day>=0 : day_num = current_start_day

        last_days_in_month=None
        if day_num is None: 
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
            last_first_day_weekday, last_days_in_month = calendar.monthrange(year, month)
            day_num = last_days_in_month - first_day_weekday + 1
        

        for i, btn in enumerate(self.day_buttons):
            btn.text = ''
            btn.day = None
            btn.month = None
            btn.year = None
            
            if last_days_in_month is not None:
                if day_num > last_days_in_month:
                    day_num = 1
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
            else: 
                if day_num > days_in_month:
                    day_num = 1
                    if month == 12:
                        month = 1
                        year += 1
                    else:
                        month += 1
            btn.text = str(day_num)
            btn.day = day_num
            btn.month = month
            btn.year = year
            if day == day_num:
                btn.background_color = light_accent_color
            else: btn.background_color = light_color
            day_num += 1
        
    
    def go_prev_week(self):
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        day -=7 
        if day <= 0:
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
            last_first_day_weekday, last_days_in_month = calendar.monthrange(year, month)
            day = last_days_in_month + day
        self.current_date = self.current_date.replace(year=year, month=month, day=day)
        self.update_calendar()
    
    def go_next_week(self):
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        day += 7
        first_day_weekday, days_in_month = calendar.monthrange(year, month)
        if day > days_in_month:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            day = day - days_in_month
        self.current_date = self.current_date.replace(year=year, month=month, day=day)
        self.update_calendar()
