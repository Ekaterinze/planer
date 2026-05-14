# screens.py
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import date
from widgets.calendar_widget import WeekCalendar, MonthCalendar
from widgets.cards import ActivityCard, DayProgressCard
from logic import (
    sort_activities_by_status, format_time_input, validate_time_format, 
    validate_time_range, get_ru_month_name
)
from widgets.variables import HEIGHT_DAY_IN_CALENDAR, HEIGHT_WEEKDAY_IN_CALENDAR


class MainScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref
        self.build_ui()
    
    def build_ui(self):
        root = MDBoxLayout(orientation='vertical')
        
        self.bottom_nav = MDBottomNavigation()
        
        # Вкладка "Планы"
        plans_tab = MDBottomNavigationItem(name='screen_plans', text='Планы', icon='calendar-check')
        plans_tab.add_widget(self._build_plans_tab())
        
        # Вкладка "Период"
        period_tab = MDBottomNavigationItem(name='screen_period', text='Период', icon='clock-outline')
        period_tab.add_widget(self._build_period_tab())
        
        # Вкладка "Расчет"
        calc_tab = MDBottomNavigationItem(name='screen_calc', text='Расчет', icon='calculator')
        calc_layout = MDBoxLayout(orientation='vertical', padding=dp(15))
        calc_layout.add_widget(MDLabel(text='Расчет', halign='center', text_color=self.app.dark_accent))
        calc_tab.add_widget(calc_layout)
        
        # Добавляем вкладки
        for tab in [plans_tab, period_tab, calc_tab]:
            self.bottom_nav.add_widget(tab)
        
        # Настраиваем цвета
        self.bottom_nav.panel_color = self.app.light
        self.bottom_nav.text_color_normal = self.app.dark
        self.bottom_nav.text_color_active = self.app.dark
        self.bottom_nav.selected_color_background = self.app.light_accent
        
        root.add_widget(self.bottom_nav)
        self.add_widget(root)
    
    def _build_plans_tab(self):
        layout = MDBoxLayout(orientation='vertical', padding=[dp(20), dp(44)], spacing=dp(10))
        
        # Навигация по неделям
        nav = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        prev_btn = MDIconButton(
            icon="chevron-left", icon_color=self.app.dark, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40))
        )
        prev_btn.bind(on_release=lambda x: self.app.prev_week())
        
        self.week_calendar = WeekCalendar()
        self.week_calendar.callback = self.app.on_day_selected
        
        next_btn = MDIconButton(
            icon="chevron-right", icon_color=self.app.dark, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40))
        )
        next_btn.bind(on_release=lambda x: self.app.next_week())
        
        nav.add_widget(prev_btn)
        nav.add_widget(self.week_calendar)
        nav.add_widget(next_btn)
        
        # Заголовок + кнопка добавления
        header = MDBoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        header.add_widget(MDLabel(text='Занятия на день', theme_text_color="Custom", 
                                  text_color=self.app.dark_accent, bold=True))
        header.add_widget(Widget())
        add_btn = MDIconButton(
            icon="plus", icon_color=self.app.dark_accent, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40))
        )
        add_btn.bind(on_release=lambda x: self.app.show_add_activity_screen())
        header.add_widget(add_btn)
        
        # Список занятий
        scroll = MDScrollView(bar_color=self.app.dark, bar_width=dp(3)  )
        self.activities_list = MDBoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.activities_list.bind(minimum_height=self.activities_list.setter('height'))
        scroll.add_widget(self.activities_list)
        
        layout.add_widget(nav)
        layout.add_widget(header)
        layout.add_widget(scroll)
        return layout
    
    def _build_period_tab(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(15))
        
        # Переключатель
        toggle = MDBoxLayout(
            size_hint=(1, None), height=dp(45), md_bg_color=self.app.dark_accent,
            padding=dp(5), spacing=dp(10), radius=[dp(8)]
        )
        
        self.btn_month = MDRectangleFlatButton(
            text="Месяц", size_hint=(0.5, 1), text_color=self.app.light,
            md_bg_color=self.app.dark_accent, line_color=self.app.light
        )
        self.btn_year = MDRectangleFlatButton(
            text="Год", size_hint=(0.5, 1), text_color=self.app.light,
            md_bg_color=self.app.dark_accent, line_color=self.app.light
        )
        
        self.btn_month.bind(on_release=lambda x: self.app.switch_tab("month_screen"))
        self.btn_year.bind(on_release=lambda x: self.app.switch_tab("year_screen"))
        
        toggle.add_widget(self.btn_month)
        toggle.add_widget(self.btn_year)
        
        # Внутренний ScreenManager
        self.inner_sm = ScreenManager(size_hint_y=1)
        
        # Экран месяца
        month_screen = Screen(name='month_screen')
        month_screen.add_widget(self._build_month_content())
        
        # Экран года
        year_screen = Screen(name='year_screen')
        year_layout = MDBoxLayout(orientation='vertical')
        year_layout.add_widget(MDLabel(text='Данные за Год', halign='center', text_color=self.app.dark_accent))
        year_screen.add_widget(year_layout)
        
        self.inner_sm.add_widget(month_screen)
        self.inner_sm.add_widget(year_screen)
        
        layout.add_widget(toggle)
        layout.add_widget(self.inner_sm)
        return layout
    
    def _build_month_content(self):
        layout = MDBoxLayout(orientation='vertical')
        
        # Навигация
        nav = MDBoxLayout(size_hint_y=None, height=dp(40))
        nav.add_widget(MDIconButton(
            icon="chevron-double-left", icon_color=self.app.dark, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40)),
            on_release=lambda x: self.app.prev_year()
        ))
        nav.add_widget(MDIconButton(
            icon="chevron-left", icon_color=self.app.dark, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40)),
            on_release=lambda x: self.app.prev_month()
        ))
        
        self.month_label = MDLabel(text="", halign="center", size_hint_x=1, text_color=self.app.dark_accent)
        nav.add_widget(self.month_label)
        
        nav.add_widget(MDIconButton(
            icon="chevron-right", icon_color=self.app.dark, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40)),
            on_release=lambda x: self.app.next_month()
        ))
        nav.add_widget(MDIconButton(
            icon="chevron-double-right", icon_color=self.app.dark, md_bg_color=self.app.light,
            size_hint_x=None, size=(dp(40), dp(40)),
            on_release=lambda x: self.app.next_year()
        ))
        
        # Календарь
        month_card = MDCard(
            orientation='vertical', line_color=self.app.dark, line_width=1,
            radius=[dp(8)], padding=dp(10), spacing=dp(5),
            size_hint_y=None, height=HEIGHT_WEEKDAY_IN_CALENDAR+6*(HEIGHT_DAY_IN_CALENDAR+5)
        )
        self.month_calendar = MonthCalendar()
        self.month_calendar.callback = self.app.on_day_selected
        month_card.add_widget(self.month_calendar)
        
        # Заметка
        note_layout = MDBoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(300))
        self.monthly_note_field = MDTextField(
            hint_text="Заметка на текущий месяц", multiline=True, size_hint_y=1,
            line_color_focus=self.app.dark, hint_text_color_focus=self.app.dark,
            text_color_focus=self.app.dark, padding=[dp(10)]*4
        )
        self.monthly_note_field.bind(text=lambda *a: self.app.check_monthly_delete_save_buttons_visibility())
        
        btn_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        self.btn_delete_monthly = MDRectangleFlatButton(
            text="Удалить", text_color=self.app.dark, line_color=self.app.dark,
            size_hint_x=None, width=dp(80), disabled=True, opacity=0,
            on_release=lambda x: self.app.delete_monthly_note()
        )
        self.btn_save_monthly = MDRectangleFlatButton(
            text="Сохранить", text_color=self.app.dark, line_color=self.app.dark,
            size_hint_x=None, width=dp(80), disabled=True, opacity=0,
            on_release=lambda x: self.app.save_monthly_note()
        )
        
        btn_layout.add_widget(self.btn_delete_monthly)
        btn_layout.add_widget(self.btn_save_monthly)
        note_layout.add_widget(self.monthly_note_field)
        note_layout.add_widget(btn_layout)
        
        layout.add_widget(nav)
        layout.add_widget(month_card)
        layout.add_widget(note_layout)
        return layout
    
    def render_activities(self, activities: list):
        """Отрисовка списка занятий (вызывается из app)"""
        if not hasattr(self, 'activities_list'):
            return
        
        self.activities_list.clear_widgets()
        
        if not activities:
            empty = MDCard(
                size_hint_y=None, height=dp(80), md_bg_color=(0,0,0,0),
                line_color=self.app.dark, line_width=1, radius=[dp(8)], elevation=0
            )
            empty.add_widget(MDLabel(
                text="Нет занятий на этот день", halign="center",
                theme_text_color="Custom", text_color=self.app.dark
            ))
            self.activities_list.add_widget(empty)
            return
        
        # Прогресс дня
        completed = [a for a in activities if a['_status'] == 'past']
        self.activities_list.add_widget(DayProgressCard(
            completed=len(completed), total=len(activities), colors=self.app.colors
        ))
        
        # Группы занятий
        sections = [
            ("Сейчас идёт", [a for a in activities if a['_status'] == 'ongoing']),
            ("Предстоящие", [a for a in activities if a['_status'] == 'upcoming']),
            ("Безвременные", [a for a in activities if a['_status'] == 'timeless']),
            ("Прошедшие или завершенные", completed),
        ]
        
        for title, items in sections:
            if items:
                self.activities_list.add_widget(MDLabel(
                    text=title, halign="left", bold=True,
                    size_hint_y=None, height=dp(30), text_color=self.app.dark
                ))
                for act in items:
                    card = ActivityCard(
                        activity=act, colors=self.app.colors,
                        on_check=self.app.toggle_activity_finished,
                        on_delete=self.app.delete_activity
                    )
                    self.activities_list.add_widget(card)
                self.activities_list.add_widget(Widget(size_hint_y=None, height=dp(10)))


class AddActivityScreen(Screen):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        toolbar = MDTopAppBar(
            title="Добавление занятия", elevation=2,
            md_bg_color=self.app.dark_accent, specific_text_color=self.app.light,
            left_action_items=[["arrow-left", lambda x: self.app.back_to_plans()]]
        )
        
        scroll = MDScrollView()
        form = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))
        
        self.name_field = MDTextField(
            hint_text="Название занятия *", required=True, mode="rectangle",
            line_color_focus=self.app.dark_accent
        )
        
        time_layout = MDBoxLayout(orientation='horizontal', spacing=dp(15), adaptive_height=True)
        
        self.start_field = MDTextField(
            hint_text="Время начала", helper_text="Формат: ЧЧ:ММ", helper_text_mode="on_focus",
            mode="rectangle", line_color_focus=self.app.dark_accent, size_hint_x=0.5
        )
        self.start_field.bind(text=lambda inst, val: self._on_time_change(inst))
        
        self.end_field = MDTextField(
            hint_text="Время окончания", helper_text="Формат: ЧЧ:ММ", helper_text_mode="on_focus",
            mode="rectangle", line_color_focus=self.app.dark_accent, size_hint_x=0.5
        )
        self.end_field.bind(text=lambda inst, val: self._on_time_change(inst))
        
        time_layout.add_widget(self.start_field)
        time_layout.add_widget(self.end_field)
        
        self.location_field = MDTextField(hint_text="Место", mode="rectangle", line_color_focus=self.app.dark_accent)
        self.recurrence_field = MDTextField(hint_text="Регулярность", text="none", mode="rectangle", line_color_focus=self.app.dark_accent)
        self.comment_field = MDTextField(hint_text="Комментарий", multiline=True, mode="rectangle", line_color_focus=self.app.dark_accent)
        self.contacts_field = MDTextField(hint_text="Контакты", mode="rectangle", line_color_focus=self.app.dark_accent)
        
        btn_layout = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50))
        btn_layout.add_widget(MDRectangleFlatButton(
            text="Выйти", theme_text_color="Custom", text_color=self.app.dark_accent,
            line_color=self.app.dark_accent, on_release=lambda x: self.app.back_to_plans()
        ))
        btn_layout.add_widget(MDRectangleFlatButton(
            text="Сохранить", theme_text_color="Custom", text_color=self.app.light,
            line_color=self.app.dark_accent, md_bg_color=self.app.dark_accent,
            on_release=lambda x: self.app.save_new_activity()
        ))
        
        for w in [self.name_field, time_layout, self.location_field, self.recurrence_field, 
                  self.comment_field, self.contacts_field, btn_layout]:
            form.add_widget(w)
        
        scroll.add_widget(form)
        layout.add_widget(toolbar)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def _on_time_change(self, instance):
        instance.text = format_time_input(instance.text, instance.focus)
        Clock.schedule_once(lambda dt: setattr(instance, 'cursor', (len(instance.text), 0)), 0)
    
    def clear_form(self):
        self.name_field.text = ""
        self.start_field.text = ""
        self.end_field.text = ""
        self.location_field.text = ""
        self.recurrence_field.text = "none"
        self.comment_field.text = ""
        self.contacts_field.text = ""
        self.name_field.error = False