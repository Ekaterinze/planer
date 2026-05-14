# main.py
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.clock import Clock
from datetime import date, datetime, timedelta
from db.database import DatabaseHelper
from widgets.variables import dark_accent_hex, light_accent_hex, dark_hex, light_hex
from screens import MainScreen, AddActivityScreen

is_tests = 1


class PlanerApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self._init_colors()
        self.db = DatabaseHelper()
        self.current_month_year = None
        self.selected_date = None
        
        if is_tests:
            Window.left, Window.top, Window.size = 100, 40, (375, 810)
        
        self.sm = ScreenManager()
        self.main_screen = MainScreen(self, name='main')
        self.add_screen = AddActivityScreen(self, name='add_activity_screen')
        
        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.add_screen)
        self.sm.current = 'main'
        return self.sm
    
    def _init_colors(self):
        """Инициализация цветов — один раз"""
        def rgba(hex_val): return get_color_from_hex(hex_val)
        def semi(c): return (c[0], c[1], c[2], 0.5)
        def trans(c): return (c[0], c[1], c[2], 0.3)
        def light(c): return (c[0], c[1], c[2], 0.1)
        
        self.dark_accent = rgba(dark_accent_hex)
        self.light_accent = rgba(light_accent_hex)
        self.light = rgba(light_hex)
        self.dark = rgba(dark_hex)
        
        # Словарь для передачи в виджеты
        self.colors = {
            'dark': self.dark,
            'light': self.light,
            'dark_accent': self.dark_accent,
            'dark_accent_dark_light': light(self.dark_accent),
            'dark_semi': semi(self.dark),
            'dark_transparent': trans(self.dark),
        }
    
    def on_start(self):
        today = date.today()
        self.on_day_selected(today.day, today.month, today.year)
        self.main_screen.app.switch_tab("month_screen")
        self._update_month_header()
        self._update_week_activities()
        self._load_monthly_note()
        Clock.schedule_interval(self._refresh_if_today, 60)
    
    def _refresh_if_today(self, dt):
        if self.selected_date == date.today():
            self.load_activities()
    
    # === Навигация по календарю ===
    def prev_week(self): self.main_screen.week_calendar.go_prev_week();self._update_week_activities(); self._update_month_header()
    def next_week(self): self.main_screen.week_calendar.go_next_week(); self._update_week_activities(); self._update_month_header()
    def prev_month(self): self.main_screen.month_calendar.go_prev_month(); self._update_month_header()
    def next_month(self): self.main_screen.month_calendar.go_next_month(); self._update_month_header()
    def prev_year(self): self.main_screen.month_calendar.go_prev_year(); self._update_month_header()
    def next_year(self): self.main_screen.month_calendar.go_next_year(); self._update_month_header()
    
    def switch_tab(self, name):
        self.main_screen.inner_sm.current = name
        active, inactive = (self.main_screen.btn_month, self.main_screen.btn_year) if name == "month_screen" \
                         else (self.main_screen.btn_year, self.main_screen.btn_month)
        active.text_color, active.md_bg_color = self.dark, self.light
        inactive.text_color, inactive.md_bg_color = self.light, self.dark_accent
        active.line_color, inactive.line_color = active.md_bg_color, inactive.md_bg_color
    
    def _update_month_header(self):
        if hasattr(self.main_screen, 'month_calendar'):
            m = self.main_screen.month_calendar.current_date.month
            y = self.main_screen.month_calendar.current_date.year
            from logic import get_ru_month_name
            self.main_screen.month_label.text = f'{get_ru_month_name(m)} {y}'
            self.current_month_year = (y, m)
            activity_map = self.load_activities_for_month(y, m)
            self.main_screen.month_calendar.set_activity_map(activity_map)
            self._load_monthly_note()

    def _update_week_activities(self):
        """Обновляет активности для текущей недели в календаре недели"""
        if hasattr(self.main_screen, 'week_calendar'):
            current_date = self.main_screen.week_calendar.current_date
            start_of_week = self.main_screen.week_calendar._get_week_start(current_date)
            activity_map = self.load_activities_for_week(start_of_week)
            self.main_screen.week_calendar.set_activity_map(activity_map)

    
    # === Работа с занятиями ===
    def on_day_selected(self, day, month, year):
        self.selected_date = date(year, month, day)
        if hasattr(self.main_screen, 'bottom_nav'):
            self.main_screen.bottom_nav.switch_tab('screen_plans')
        if hasattr(self.main_screen, 'week_calendar'):
            self.main_screen.week_calendar.current_date = self.selected_date
            self.main_screen.week_calendar.update_calendar()
        if hasattr(self.main_screen, 'month_calendar'):
            self.main_screen.month_calendar.current_date = self.selected_date
            self.main_screen.month_calendar.update_calendar()
        self._update_week_activities()
        self.load_activities()
    
    def load_activities(self):
        if not self.selected_date: return
        from logic import sort_activities_by_status
        acts = self.db.get_activities_by_date(self.selected_date)
        sorted_acts = sort_activities_by_status(acts, self.selected_date)
        self.main_screen.render_activities(sorted_acts)

    # В main_pure_python.py
    def load_activities_for_month(self, year, month):
        """Загружает активности за месяц и возвращает словарь для отображения точек"""
        from datetime import timedelta
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        activities = self.db.get_activities_by_range(start_date, end_date)
        
        activity_map = {}
        for activity in activities:
            # ПРЕОБРАЗУЕМ строку в объект date
            activity_date = activity['date']
            if isinstance(activity_date, str):
                activity_date = datetime.strptime(activity_date, '%Y-%m-%d').date()
            
            if activity_date in activity_map:
                activity_map[activity_date] += 1
            else:
                activity_map[activity_date] = 1
        
        return activity_map
    
    def load_activities_for_week(self, week_start_date):
        """Загружает активности за неделю и возвращает словарь для отображения точек"""
        # Вычисляем конец недели (7 дней от начала)
        week_end_date = week_start_date + timedelta(days=6)
        
        activities = self.db.get_activities_by_range(week_start_date, week_end_date)
        
        activity_map = {}
        for activity in activities:
            activity_date = activity['date']
            if isinstance(activity_date, str):
                activity_date = datetime.strptime(activity_date, '%Y-%m-%d').date()
            
            if activity_date in activity_map:
                activity_map[activity_date] += 1
            else:
                activity_map[activity_date] = 1
        
        return activity_map
        
    def toggle_activity_finished(self, aid):
        self.db.toggle_activity_finished(aid); self.load_activities()
    
    def delete_activity(self, aid):
        self.db.delete_activity(aid); self.load_activities()
    
    # === Экраны ===
    def show_add_activity_screen(self):
        self.add_screen.clear_form()
        self.sm.current = 'add_activity_screen'
    
    def back_to_plans(self):
        self.sm.current = 'main'
        if hasattr(self.main_screen, 'bottom_nav'):
            self.main_screen.bottom_nav.switch_tab('screen_plans')
        self.load_activities()
    
    # === Сохранение занятия ===
    def save_new_activity(self):
        name = self.add_screen.name_field.text.strip()
        if not name:
            self.add_screen.name_field.error = True
            self.add_screen.name_field.hint_text = "Название обязательно *"
            return
        
        start = self.add_screen.start_field.text.strip()
        end = self.add_screen.end_field.text.strip()
        
        from logic import validate_time_format, validate_time_range
        if start and not validate_time_format(start): self.add_screen.start_field.error = True; return
        if end and not validate_time_format(end): self.add_screen.end_field.error = True; return
        if start and end and not validate_time_range(start, end): self.add_screen.end_field.error = True; return
        
        self.db.add_activity(
            date_obj=self.selected_date, name=name,
            start_time=start or None, end_time=end or None,
            location=self.add_screen.location_field.text.strip() or None,
            recurrence=self.add_screen.recurrence_field.text.strip() or "none",
            comment=self.add_screen.comment_field.text.strip() or None,
            contacts=self.add_screen.contacts_field.text.strip() or None,
        )
        self.back_to_plans()
    
    # === Заметки на месяц ===
    def _load_monthly_note(self):
        if self.current_month_year:
            y, m = self.current_month_year
            self.main_screen.monthly_note_field.text = self.db.get_monthly_note(y, m)
            self.check_monthly_delete_save_buttons_visibility()
    
    def save_monthly_note(self):
        if self.current_month_year:
            y, m = self.current_month_year
            self.db.save_monthly_note(y, m, self.main_screen.monthly_note_field.text)
            self.check_monthly_delete_save_buttons_visibility()
    
    def delete_monthly_note(self):
        if self.current_month_year:
            y, m = self.current_month_year
            self.main_screen.monthly_note_field.text = ""
            self.db.save_monthly_note(y, m, "")
    
    def check_monthly_delete_save_buttons_visibility(self):
        note = self.main_screen.monthly_note_field.text.strip() if hasattr(self.main_screen, 'monthly_note_field') else ""
        for btn in [getattr(self.main_screen, 'btn_delete_monthly', None), getattr(self.main_screen, 'btn_save_monthly', None)]:
            if btn:
                btn.opacity, btn.disabled = (1, False) if note else (0, True)


if __name__ == '__main__':
    PlanerApp().run()