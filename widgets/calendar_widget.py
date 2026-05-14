# widgets/calendar_widget.py
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Ellipse, InstructionGroup
import calendar
from datetime import date,timedelta
from kivy.clock import Clock
from widgets.variables import dark_accent_hex, light_accent_hex, dark_hex, light_hex, HEIGHT_DAY_IN_CALENDAR, HEIGHT_WEEKDAY_IN_CALENDAR, DOT_SIZE

light_color = get_color_from_hex(light_hex)
dark_color = get_color_from_hex(dark_hex)
light_accent_color = get_color_from_hex(light_accent_hex)
dark_accent_color = get_color_from_hex(dark_accent_hex)
DOT_COLOR = dark_accent_color  # Цвет индикатора занятости


class BaseCalendar(GridLayout):
    """Базовый класс календаря с поддержкой индикаторов активности"""
    callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.activity_map = {}  # {date_obj: count}
        self.day_buttons = []

    def set_activity_map(self, date_map):
        """Принимает dict {date: count} и обновляет отрисовку"""
        self.activity_map = date_map
        self.update_calendar()

    def _clear_dot(self, btn):
        """Безопасно удаляет кружочек с кнопки"""
        if hasattr(btn, '_dot_group'):
            try:
                btn.canvas.after.remove(btn._dot_group)
            except:
                pass
            del btn._dot_group

    def _draw_dot(self, btn):
        """Рисует кружочек внизу кнопки с автоматическим обновлением позиции"""
        self._clear_dot(btn)
        
        dot_size = DOT_SIZE
        
        group = InstructionGroup()
        group.add(Color(rgba=DOT_COLOR))
        ellipse = Ellipse(size=(dot_size, dot_size))
        group.add(ellipse)
        
        btn.canvas.after.add(group)
        btn._dot_group = group
        btn._dot_ellipse = ellipse
        
        def update_position(*args):
            if btn.width > 0 and btn.height > 0:
                new_x = btn.x + btn.width - dot_size -dp(3)
                new_y = btn.y + dp(3)
                ellipse.pos = (new_x, new_y)
        
        btn.bind(pos=update_position, size=update_position)
        Clock.schedule_once(lambda dt: update_position(), 0.1)

    def on_button_press(self, instance):
        if hasattr(instance, 'day') and instance.day:
            self.current_date = date(instance.year, instance.month, instance.day)
            self.update_calendar()
            if self.callback:
                self.callback(instance.day, instance.month, instance.year)

    def _get_week_start(self, current_date):
        """Возвращает дату понедельника текущей недели"""
        days_to_monday = current_date.weekday()
        start_of_week = current_date - timedelta(days=days_to_monday)
        return start_of_week


class MonthCalendar(BaseCalendar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.rows = 7
        self.spacing = [2, 2]
        self.size_hint = (1, None)
        self.height = HEIGHT_WEEKDAY_IN_CALENDAR + 6 * HEIGHT_DAY_IN_CALENDAR
        self.selected_button = None
        self.md_bg_color = light_color

        # Заголовки дней недели
        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day_name in weekdays:
            label = Label(
                text=day_name, size_hint_y=None, height=HEIGHT_WEEKDAY_IN_CALENDAR,
                color=dark_color, halign='center', valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            self.add_widget(label)

        # Ячейки месяца (42 шт)
        for _ in range(6 * 7):
            btn = Button(
                text='', background_normal='', background_color=light_color,
                color=dark_color, size_hint_y=None, height=HEIGHT_DAY_IN_CALENDAR,
                background_down=''
            )
            btn.bind(on_release=self.on_button_press)
            self.add_widget(btn)
            self.day_buttons.append(btn)

        self.current_date = date.today()
        self.update_calendar()
        
        # Привязываем обновление позиций точек к изменению размера календаря
        self.bind(size=self._on_calendar_resize)
    
    def _on_calendar_resize(self, *args):
        """При изменении размера календаря перерисовываем все точки"""
        for btn in self.day_buttons:
            if hasattr(btn, '_dot_group'):
                self._draw_dot(btn)

    def update_calendar(self):
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day
        first_day_weekday, days_in_month = calendar.monthrange(year, month)
        start_offset = first_day_weekday

        day_num = 1
        for i, btn in enumerate(self.day_buttons):
            btn.text = ''
            btn.day = None
            btn.month = None
            btn.year = None
            self._clear_dot(btn)

            if i >= start_offset and day_num <= days_in_month:
                btn.text = str(day_num)
                btn.day = day_num
                btn.month = month
                btn.year = year
                
                current_date_obj = date(year, month, day_num)
                if current_date_obj in self.activity_map:
                    self._draw_dot(btn)

                btn.background_color = light_accent_color if day == day_num else light_color
                day_num += 1
            else:
                btn.background_color = light_color

    def go_prev_month(self):
        year, month = self.current_date.year, self.current_date.month
        month = 12 if month == 1 else month - 1
        year = year - 1 if month == 12 else year
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()

    def go_next_month(self):
        year, month = self.current_date.year, self.current_date.month
        month = 1 if month == 12 else month + 1
        year = year + 1 if month == 1 else year
        self.current_date = self.current_date.replace(year=year, month=month, day=1)
        self.update_calendar()

    def go_prev_year(self):
        self.current_date = self.current_date.replace(year=self.current_date.year - 1, day=1)
        self.update_calendar()

    def go_next_year(self):
        self.current_date = self.current_date.replace(year=self.current_date.year + 1, day=1)
        self.update_calendar()


class WeekCalendar(BaseCalendar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.rows = 2
        self.spacing = [2, 2]
        self.size_hint = (1, None)
        self.height = HEIGHT_DAY_IN_CALENDAR + HEIGHT_WEEKDAY_IN_CALENDAR
        self.selected_button = None
        self.md_bg_color = light_color

        weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day_name in weekdays:
            label = Label(
                text=day_name, size_hint_y=None, height=HEIGHT_WEEKDAY_IN_CALENDAR,
                color=dark_color, halign='center', valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            self.add_widget(label)

        # Ячейки недели (7 шт)
        for _ in range(7):
            btn = Button(
                text='', background_normal='', background_color=light_color,
                color=dark_color, size_hint_y=None, height=HEIGHT_DAY_IN_CALENDAR,
                background_down=''
            )
            btn.bind(on_release=self.on_button_press)
            self.add_widget(btn)
            self.day_buttons.append(btn)

        self.current_date = date.today()
        self.update_calendar()
        
        self.bind(size=self._on_calendar_resize, pos=self._on_calendar_resize)
    
    def _on_calendar_resize(self, *args):
        """При изменении размера или позиции календаря перерисовываем все точки"""
        Clock.schedule_once(lambda dt: self._refresh_all_dots(), 0.1)
    
    def _refresh_all_dots(self):
        """Обновляет все точки на кнопках"""
        for i, btn in enumerate(self.day_buttons):
            # Проверяем, должна ли быть точка на этой кнопке
            if hasattr(btn, 'day') and btn.day and hasattr(btn, 'month') and btn.month:
                current_date_obj = date(btn.year, btn.month, btn.day)
                if current_date_obj in self.activity_map:
                    if not hasattr(btn, '_dot_group'):
                        self._draw_dot(btn)
                    else:
                        self._update_dot_position(btn)
                else:
                    if hasattr(btn, '_dot_group'):
                        self._clear_dot(btn)
    
    def _update_dot_position(self, btn):
        """Обновляет позицию существующей точки"""
        if not hasattr(btn, '_dot_group') or not hasattr(btn, '_dot_ellipse'):
            return
        
        dot_size = DOT_SIZE
        new_x = btn.x + btn.width - dot_size - dp(3)
        new_y = btn.y + dp(3)
        btn._dot_ellipse.pos = (new_x, new_y)

    def update_calendar(self):
        year = self.current_date.year
        month = self.current_date.month
        day = self.current_date.day

        day_num = self._get_week_start(self.current_date)

        self.current_display_year = year
        self.current_display_month = month

        for i, btn in enumerate(self.day_buttons):
            btn.text = ''
            btn.day = None
            btn.month = None
            btn.year = None
            self._clear_dot(btn)

            btn.text = str(day_num.day)
            btn.day = day_num.day
            btn.month = month
            btn.year = year
            
            if day_num in self.activity_map:
                self._draw_dot(btn)

            btn.background_color = light_accent_color if day == day_num.day else light_color
            day_num = day_num + timedelta(1)
        
        Clock.schedule_once(lambda dt: self._refresh_all_dots(), 0.1)

    def go_prev_week(self):
        year, month, day = self.current_date.year, self.current_date.month, self.current_date.day
        day -= 7
        if day <= 0:
            month = 12 if month == 1 else month - 1
            year = year - 1 if month == 12 else year
            _, last_days = calendar.monthrange(year, month)
            day = last_days + day
        self.current_date = self.current_date.replace(year=year, month=month, day=day)
        self.update_calendar()

    def go_next_week(self):
        year, month, day = self.current_date.year, self.current_date.month, self.current_date.day
        day += 7
        _, days_in_month = calendar.monthrange(year, month)
        if day > days_in_month:
            month = 1 if month == 12 else month + 1
            year = year + 1 if month == 1 else year
            day = day - days_in_month
        self.current_date = self.current_date.replace(year=year, month=month, day=day)
        self.update_calendar()