# main.py
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarListItem, IconLeftWidget, OneLineAvatarIconListItem
from datetime import date, datetime, timedelta
from db.database import DatabaseHelper
from kivy.core.window import Window
from kivy.clock import Clock
from widgets.month_calendar_widget import MonthCalendar
from widgets.week_calendar_widget import WeekCalendar
from widgets.variables import dark_green_hex, light_green_hex, dark_hex, light_hex, BORDER_WIDTH, CARD_HEIGHT, RADIUS
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.uix.widget import Widget  
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.progressbar import MDProgressBar

is_tests = 1


KV = '''
MDScreenManager:
    id: main_sm
    
    MDScreen:
        name: 'main'

        MDBottomNavigation:
            id: bottom_nav
            on_parent: app.bottom_nav = self
            panel_color: app.light
            text_color_normal: app.dark
            text_color_active: app.dark
            selected_color_background: app.light_green

            MDBottomNavigationItem:
                name: 'screen_plans'
                text: 'Планы'
                icon: 'calendar-check'
                MDBoxLayout:                     
                    orientation: 'vertical'
                    padding: [dp(20), dp(44)]
                    spacing: dp(10)
                    

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None

                        MDIconButton:
                            icon: "chevron-left"
                            on_release: app.prev_week()
                            user_color: app.dark
                            user_md_bg_color: app.light
                            size_hint_x: None
                            width: dp(40)
                            height: dp(40)
                        
                        WeekCalendar:   
                            id: calendar_week
                        
                        MDIconButton:
                            icon: "chevron-right"
                            on_release: app.next_week()
                            user_color: app.dark
                            user_md_bg_color: app.light
                            size_hint_x: None
                            width: dp(40)
                            height: dp(40) 
                             

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(10)
                    
                        MDLabel:
                            text: 'Занятия на день'
                            theme_text_color: "Custom"
                            text_color: app.dark_green
                            bold: True
                        
                        Widget:
                        
                        MDIconButton:
                            icon: "plus"
                            user_color: app.light
                            user_md_bg_color: app.dark_green
                            size_hint_x: None
                            size: (dp(40), dp(40))
                            on_release: app.show_add_activity_screen()

                    # 🔹 Список занятий
                    ScrollView:
                        MDList:
                            id: activities_list
                        
                        

            MDBottomNavigationItem:
                name: 'screen_period'
                text: 'Период'
                icon: 'clock-outline'
                
                MDBoxLayout:
                    orientation: "vertical"
                    padding: dp(15)
                    
                    MDBoxLayout:
                        adaptive_height: True
                        md_bg_color: app.dark_green
                        padding: dp(5)
                        radius: dp(8)
                        
                        MDRectangleFlatButton:
                            id: btn_month
                            text: "Месяц"
                            size_hint_x: 0.5
                            on_release: app.switch_tab("month_screen")
                            
                        MDRectangleFlatButton:
                            id: btn_year
                            text: "Год"
                            size_hint_x: 0.5
                            on_release: app.switch_tab("year_screen")

                    MDScreenManager:
                        id: inner_sm
                        size_hint_y: 1
                        
                        MDScreen:
                            name: "month_screen"
                            MDBoxLayout:
                                orientation: "vertical"
                                
                                MDBoxLayout:

                                    MDIconButton:
                                        icon: "chevron-double-left"
                                        on_release: app.prev_year()
                                        user_color: app.dark
                                        user_md_bg_color: app.light
                                        size_hint_x: None
                                        width: dp(40)
                                        height: dp(40) 
                                    
                                    MDIconButton:
                                        icon: "chevron-left"
                                        on_release: app.prev_month()
                                        user_color: app.dark
                                        user_md_bg_color: app.light
                                        size_hint_x: None
                                        width: dp(40)
                                        height: dp(40)
                                    
                                    MDLabel:
                                        id: month_label
                                        text: ""
                                        halign: "center"
                                        size_hint_x: 1
                                        text_color: app.dark_green 
                                    
                                    MDIconButton:
                                        icon: "chevron-right"
                                        on_release: app.next_month()
                                        user_color: app.dark
                                        user_md_bg_color: app.light
                                        size_hint_x: None
                                        width: dp(40)
                                        height: dp(40) 
                                    
                                    MDIconButton:
                                        icon: "chevron-double-right"
                                        on_release: app.next_year()
                                        user_color: app.dark
                                        user_md_bg_color: app.light
                                        size_hint_x: None
                                        width: dp(40)
                                        height: dp(40)   
                                    
                                
                                MDCard:
                                    orientation: 'vertical'
                                    line_color: app.dark
                                    line_width: 1
                                    radius: dp(8)
                                    padding: dp(10)
                                    spacing: dp(5)
                                    size_hint_y: None
                                    height: self.minimum_height
                                    
                                    MonthCalendar:   
                                        id: calendar_month
                                
                                MDBoxLayout:
                                    orientation: 'vertical'
                                    spacing: dp(10)
                                    size_hint_y: None
                                    height: dp(300)
                                    
                                    MDTextField:
                                        id: monthly_note_field
                                        hint_text: "Заметка на текущий месяц"
                                        multiline: True
                                        size_hint_y: 1
                                        on_text: app.check_monthly_delete_save_buttons_visibility()
                                        line_color_focus: app.dark 
                                        hint_text_color_focus: app.dark
                                        text_color_focus: app.dark
                                        padding: [dp(10), dp(10), dp(10), dp(10)]

                                    MDBoxLayout:
                                        orientation: 'horizontal'
                                        spacing: dp(10)
                                        size_hint_y: None
                                        height: dp(40)

                                        MDRectangleFlatButton:
                                            id: btn_delete_monthly
                                            text: "Удалить"
                                            text_color: app.dark
                                            line_color: app.dark
                                            size_hint_x: None
                                            width: dp(80)
                                            on_release: app.delete_monthly_note()

                                        MDRectangleFlatButton:
                                            id: btn_save_monthly
                                            text: "Сохранить"
                                            text_color: app.dark
                                            line_color: app.dark
                                            size_hint_x: None
                                            width: dp(80) 
                                            on_release: app.save_monthly_note()

                        MDScreen:
                            name: "year_screen"
                            MDLabel:
                                text: "Данные за Год"
                                halign: "center"
                                text_color: app.dark_green

            MDBottomNavigationItem:
                name: 'screen_calc'
                text: 'Расчет'
                icon: 'calculator'
                MDLabel:
                    text: 'Расчет'
                    halign: 'center'
                    text_color: app.dark_green

    MDScreen:
        name: 'add_activity_screen'
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(15)
            
            MDTopAppBar:
                title: "Добавление занятия"
                elevation: 2
                left_action_items: [["arrow-left", lambda x: app.back_to_plans()]]
                md_bg_color: app.dark_green
                specific_text_color: app.light
            
            ScrollView:
                MDBoxLayout:
                    id: add_activity_form
                    orientation: 'vertical'
                    spacing: dp(10)
                    padding: dp(15)
                    size_hint_y: None
                    height: self.minimum_height
                    
                    MDTextField:
                        id: activity_name
                        hint_text: "Название занятия *"
                        required: True
                        mode: "rectangle"
                        line_color_focus: app.dark_green

                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(15)
                        adaptive_height: True 
                        
                        MDTextField:
                            id: activity_start_time
                            hint_text: "Время начала"
                            helper_text: "Формат: ЧЧ:ММ"
                            helper_text_mode: "on_focus"
                            mode: "rectangle"
                            line_color_focus: app.dark_green
                            on_text: app.auto_format_time(self)
                            size_hint_x: 0.5
                            
                        MDTextField:
                            id: activity_end_time
                            hint_text: "Время окончания"
                            helper_text: "Формат: ЧЧ:ММ"
                            helper_text_mode: "on_focus"
                            mode: "rectangle"
                            line_color_focus: app.dark_green
                            on_text: app.auto_format_time(self)
                            size_hint_x: 0.5
                        
                    MDTextField:
                        id: activity_location
                        hint_text: "Место"
                        mode: "rectangle"
                        line_color_focus: app.dark_green
                        
                    MDTextField:
                        id: activity_recurrence
                        hint_text: "Регулярность"
                        text: "none"
                        mode: "rectangle"
                        line_color_focus: app.dark_green
                        
                    MDTextField:
                        id: activity_comment
                        hint_text: "Комментарий"
                        multiline: True
                        mode: "rectangle"
                        line_color_focus: app.dark_green
                        
                    MDTextField:
                        id: activity_contacts
                        hint_text: "Контакты"
                        mode: "rectangle"
                        line_color_focus: app.dark_green
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)
                        
                        MDRectangleFlatButton:
                            text: "Выйти"
                            theme_text_color: "Custom"
                            text_color: app.dark_green
                            line_color: app.dark_green
                            on_release: app.back_to_plans()
                        
                        MDRectangleFlatButton:
                            text: "Сохранить"
                            theme_text_color: "Custom"
                            text_color: app.light
                            line_color: app.dark_green
                            md_bg_color: app.dark_green
                            on_release: app.save_new_activity_fixed()
'''

class PlanerApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.initcolor()

        self.db = DatabaseHelper()            # инициализация БД
        self.current_month_year = None 
        self.selected_date = None

        if is_tests: 
            Window.left = 100   # X координата
            Window.top = 40
            Window.size = (375, 810) 

        root = Builder.load_string(KV)
        
        # Сохраняем ссылки на нужные виджеты
        root.current = 'main'
        
        return root
    
    def initcolor(self):
        self.dark_green = get_color_from_hex(dark_green_hex)
        self.dark_green_semi = (self.dark_green[0], self.dark_green[1], self.dark_green[2], 0.5)
        self.dark_green_transparent = (self.dark_green[0], self.dark_green[1], self.dark_green[2], 0.3)
        self.dark_green_dark_light = (self.dark_green[0], self.dark_green[1], self.dark_green[2], 0.1)

        self.light_green = get_color_from_hex(light_green_hex)
        self.light_green_semi = (self.light_green[0], self.light_green[1], self.light_green[2], 0.5)
        self.light_green_transparent = (self.light_green[0], self.light_green[1], self.light_green[2], 0.3)
        self.light_green_light_light = (self.light_green[0], self.light_green[1], self.light_green[2], 0.1)

        self.light = get_color_from_hex(light_hex)
        self.light_semi = (self.light[0], self.light[1], self.light[2], 0.5)
        self.light_transparent = (self.light[0], self.light[1], self.light[2], 0.3)
        self.light_light = (self.light[0], self.light[1], self.light[2], 0.1)

        self.dark = get_color_from_hex(dark_hex)
        self.dark_semi = (self.dark[0], self.dark[1], self.dark[2], 0.5)
        self.dark_transparent = (self.dark[0], self.dark[1], self.dark[2], 0.3)
        self.dark_light = (self.dark[0], self.dark[1], self.dark[2], 0.1)


    def get_color_with_alpha(self, color_rgba, alpha):
        """Возвращает цвет с заданной прозрачностью"""
        return (color_rgba[0], color_rgba[1], color_rgba[2], alpha)
    
    def on_start(self):

        self.main_screen = self.root.get_screen('main')
        self.add_screen = self.root.get_screen('add_activity_screen')

        self.root.ids.calendar_month.callback = self.on_day_selected
        self.root.ids.calendar_week.callback = self.on_day_selected
        todate=date.today()
        self.on_day_selected( todate.day, todate.month, todate.year )
        self.switch_tab("month_screen")
        self.update_month_header()
        self.load_monthly_note()
        Clock.schedule_interval(self.refresh_activities_if_needed, 60)
    
    def refresh_activities_if_needed(self, dt):
        """Перезагружает список, если выбрана сегодняшая дата"""
        if self.selected_date == date.today():
            self.load_activities()
    
    def switch_tab(self, screen_name):
        self.root.ids.inner_sm.current = screen_name
        
        btn_month = self.root.ids.btn_month
        btn_year = self.root.ids.btn_year
        
        if screen_name == "month_screen":
            btn_month.text_color = self.dark
            btn_month.md_bg_color = self.light
            btn_year.text_color = self.light
            btn_year.md_bg_color = self.dark_green

        else:
            btn_year.text_color = self.dark
            btn_year.md_bg_color = self.light
            btn_month.text_color = self.light
            btn_month.md_bg_color = self.dark_green

        btn_month.line_color = btn_month.md_bg_color
        btn_year.line_color = btn_year.md_bg_color
    
    def update_month_header(self):
        calendar_widget = self.root.ids.calendar_month
        month = calendar_widget.current_date.month
        year = calendar_widget.current_date.year
        RUSSIAN_MONTHS = [
            '', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        month_name = RUSSIAN_MONTHS[month]
        self.root.ids.month_label.text = f'{month_name} {year}'
        self.current_month_year = (year, month)
        self.load_monthly_note()
    
    def prev_week(self):
        self.root.ids.calendar_week.go_prev_week()
        self.update_month_header()
    
    def next_week(self):
        self.root.ids.calendar_week.go_next_week()
        self.update_month_header()

    def prev_month(self):
        self.root.ids.calendar_month.go_prev_month()
        self.update_month_header()
    
    def next_month(self):
        self.root.ids.calendar_month.go_next_month()
        self.update_month_header()

    def prev_year(self):
        self.root.ids.calendar_month.go_prev_year()
        self.update_month_header()
    
    def next_year(self):
        self.root.ids.calendar_month.go_next_year()
        self.update_month_header()
    
    def on_day_selected(self, day, month, year):
        self.selected_date = date(year, month, day)
        self.root.ids.bottom_nav.switch_tab('screen_plans')
        self.root.ids.calendar_week.current_date = date(year, month, day)
        self.root.ids.calendar_week.update_calendar()
        self.root.ids.calendar_month.current_date = date(year, month, day)
        self.root.ids.calendar_month.update_calendar()
        self.load_activities()

    def show_add_activity_screen(self):
        """Переключает на экран добавления занятия"""
        # Очищаем поля
        self.clear_activity_form()
        self.root.current = 'add_activity_screen'
    
    def back_to_plans(self):
        """Возврат к главному экрану с планами"""
        self.root.current = 'main'
        self.bottom_nav.switch_tab('screen_plans')
        self.load_activities()
    
    def load_activities(self):
        """Загружает и отображает занятия в виде карточек-рамок"""
        if not self.selected_date:
            return
            
        activities = self.db.get_activities_by_date(self.selected_date)
        sorted_activities = self._sort_activities_by_status(activities)
        
        activities_list = self.root.ids.activities_list
        activities_list.clear_widgets()
        
        if not sorted_activities:
            empty_card = MDCard(
                size_hint_y=None, height=dp(80),
                md_bg_color=(0, 0, 0, 0),  # Прозрачный фон
                line_color=self.dark, line_width=1,
                radius=[dp(8)], elevation=0
            )
            empty_card.add_widget(MDLabel(
                text="Нет занятий на этот день", 
                halign="center", 
                theme_text_color="Custom", 
                text_color=self.dark
            ))
            activities_list.add_widget(empty_card)
            return
        
        card_height = CARD_HEIGHT
        radius = RADIUS
        border_width = dp(1) 
        

        border_card = MDCard(
            size_hint_y=None, 
            height=card_height + 2*border_width,
            md_bg_color=self.dark,
            radius=[radius + border_width],
            elevation=0,
            padding=border_width,
            orientation='horizontal'
        )

        # Внутренняя карточка с контентом
        v_content_card = MDCard(
            size_hint_y=None,
            height=card_height,
            md_bg_color=self.light,
            radius=[radius],
            elevation=0,
            padding=dp(10),
            spacing=dp(10),
            orientation='vertical'
        )

        # Внутренняя карточка с контентом
        h_content_card = MDCard(
            size_hint_y=None,
            height=card_height//2,
            md_bg_color=self.light,
            radius=[radius],
            elevation=0,
            padding=dp(10),
            spacing=dp(10),
            orientation='horizontal'
        )
        
        # Наполняем внутреннюю карточку
        label_name= MDLabel(
            text='Прогресс дня', halign="left", text_color=self.dark,
            size_hint_x=1, shorten=True, shorten_from="right"
        )
        completed = [a for a in sorted_activities if a['_status'] == 'past']
        text_progress = str(len(completed))+' из ' + str(len(sorted_activities))
        label_progress = MDLabel(
            text=text_progress, halign="right", text_color=self.dark,
            size_hint_x=1, shorten=True, shorten_from="right"
        )
        progress = MDProgressBar(
            value = len(completed)*100 //len(sorted_activities),
            color= self.dark_green,
            back_color = self.dark_green_dark_light
        )

        h_content_card.add_widget(label_name)
        h_content_card.add_widget(label_progress)
        v_content_card.add_widget(h_content_card)
        v_content_card.add_widget(progress)
        border_card.add_widget(v_content_card)
        activities_list.add_widget(border_card)
        # Группировка по статусам
        sections = [
            ("Сейчас идёт",[a for a in sorted_activities if a['_status'] == 'ongoing']),
            ("Предстоящие", [a for a in sorted_activities if a['_status'] == 'upcoming']),
            ("Безвременные", [a for a in sorted_activities if a['_status'] == 'timeless']),
            ("Прошедшие или завершенные", completed),
        ]
        
        for section_title, items in sections:
            if items:
                header = MDLabel(
                    text=section_title, halign="left", bold=True, 
                    size_hint_y=None, height=dp(30)
                )
                header.text_color = self.dark
                activities_list.add_widget(header)
                
                for act in items:
                    # Формируем текст
                    time_str = ""
                    if act['start_time'] and act['end_time']:
                        time_str = f"{act['start_time']}–{act['end_time']}  "
                    elif act['start_time']:
                        time_str = f"с {act['start_time']}  "
                    
                    location_str = f" • {act['location']}" if act['location'] else ""
                    display_text = f"{time_str}{act['name']}{location_str}"
                    
                    # Определяем цвета в зависимости от статуса
                    if act['_status'] == 'ongoing':
                        border_color = self.dark_green      # Цвет рамки
                        content_bg = self.light             # Фон контента
                        text_color = self.dark_green
                        border_width = dp(3) 
                    elif act['_status'] == 'past':
                        border_color = self.dark_semi
                        content_bg = self.light
                        text_color = self.dark_semi
                    else:
                        # Для обычных: либо скрыть рамку, либо сделать нейтральной
                        border_color = self.dark_transparent  # Почти невидимая
                        content_bg = self.light
                        text_color = self.dark
                    
                    
                    # Внешняя карточка-рамка
                    border_card = MDCard(
                        size_hint_y=None, 
                        height=card_height + 2*border_width,
                        md_bg_color=border_color,
                        radius=[radius + border_width],
                        elevation=0,
                        padding=border_width,
                        orientation='horizontal'
                    )
                    
                    # Внутренняя карточка с контентом
                    content_card = MDCard(
                        size_hint_y=None,
                        height=card_height,
                        md_bg_color=content_bg,
                        radius=[radius],
                        elevation=0,
                        padding=dp(10),
                        spacing=dp(10),
                        orientation='horizontal'
                    )
                    
                    # Наполняем внутреннюю карточку
                    label = MDLabel(
                        text=display_text, halign="left", 
                        theme_text_color="Custom", text_color=text_color,
                        size_hint_x=1, shorten=True, shorten_from="right"
                    )
                    content_card.add_widget(label)

                    btn_size = min( dp(50), dp((card_height - 5))//2)

                    buttons_container = FloatLayout(
                        size_hint_x=None,
                        size=(dp(btn_size), dp(card_height)) 
                    )

                    check_btn = MDIconButton(
                        icon="check-all" if act['finished'] else "check",
                        user_color=self.dark_green,
                        size_hint=(None, None),
                        size=(dp(btn_size ), dp(btn_size )),
                        pos_hint={'center_x': 0.5, 'center_y': 0.75},
                        on_release=lambda x, aid=act['id']: self.toggle_activity_finished(aid)
                    )

                    del_btn = MDIconButton(
                        icon="delete-outline",
                        user_color=self.dark_green,
                        size_hint=(None, None),
                        size=(dp(btn_size ), dp(btn_size )),
                        pos_hint={'center_x': 0.5, 'center_y': 0.25},
                        on_release=lambda x, aid=act['id']: self.delete_activity(aid)
                    )

                    buttons_container.add_widget(check_btn)
                    buttons_container.add_widget(del_btn)
                    content_card.add_widget(buttons_container)
                    border_card.add_widget(content_card)
                    # Добавляем в список ВНЕШНЮЮ карточку
                    activities_list.add_widget(border_card)
                    
                activities_list.add_widget(Widget(size_hint_y=None, height=dp(10)))

    def _sort_activities_by_status(self, activities: list) -> list:
        """
        Сортирует занятия:
        1. Сейчас идущие (start <= now <= end)
        2. Предстоящие (start > now)
        3. Прошедшие (end < now)
        4. Безвременные
        Внутри групп сортировка по start_time
        """
        now = datetime.now()
        result = {'ongoing': [], 'upcoming': [], 'past': [], 'timeless': []}
        
        for act in activities:
            start = None
            end = None
            
            if act['start_time']:
                start = datetime.combine(self.selected_date, datetime.strptime(act['start_time'], "%H:%M").time())
            if act['end_time']:
                end = datetime.combine(self.selected_date, datetime.strptime(act['end_time'], "%H:%M").time())
            
            # Определяем статус
            if (start is None or end is None ) and not act['finished']:
                act['_status'] = 'timeless'
                result['timeless'].append(act)
            elif start and end and start <= now <= end and not act['finished']:
                act['_status'] = 'ongoing'
                result['ongoing'].append(act)
            elif start and start > now and not act['finished']:
                act['_status'] = 'upcoming'
                result['upcoming'].append(act)
            else:
                act['_status'] = 'past'
                result['past'].append(act)
        
        # Сортируем внутри групп по start_time (None в конце)
        def sort_key(a):
            return a['start_time'] if a['start_time'] else "99:99"
        
        for key in result:
            result[key].sort(key=sort_key)
        
        # Объединяем в нужном порядке
        return result['ongoing'] + result['upcoming'] + result['timeless'] +  result['past']
    
    def toggle_activity_finished(self, activity_id):
        """Переключает статус выполнения занятия"""
        self.db.toggle_activity_finished(activity_id)
        self.load_activities()  # Обновляем список

    def delete_activity(self, activity_id: int):
        """Удаляет занятие и обновляет список"""
        self.db.delete_activity(activity_id)
        self.load_activities()
    
    def clear_activity_form(self):
        """Очищает все поля формы добавления занятия"""
        self.root.ids.activity_name.text = ""
        self.root.ids.activity_start_time.text = ""
        self.root.ids.activity_end_time.text = ""
        self.root.ids.activity_location.text = ""
        self.root.ids.activity_recurrence.text = "none"
        self.root.ids.activity_comment.text = ""
        self.root.ids.activity_contacts.text = ""
        
        # Сбрасываем ошибки
        self.root.ids.activity_name.error = False

    def auto_format_time(self, widget):
        """Автоматически форматирует ввод в ЧЧ:ММ без багов с курсором"""
        if getattr(widget, '_is_formatting', False):
            return
        widget._is_formatting = True

        # Оставляем только цифры (макс 4)
        digits = ''.join(c for c in widget.text if c.isdigit())
        if len(digits) > 4:
            digits = digits[:4]

        # Формируем строку
        if len(digits) >= 3:
            formatted = f"{digits[:2]}:{digits[2:]}"
        elif len(digits) == 2 and widget.focus:
            formatted = f"{digits}:"
        else:
            formatted = digits

        # Меняем текст только если он отличается
        if formatted != widget.text:
            widget.text = formatted
            # 🔹 Курсор двигаем отложенно, чтобы избежать бага "13:43"
            Clock.schedule_once(lambda dt: setattr(widget, 'cursor', (len(widget.text), 0)), 0)

        widget._is_formatting = False
    
    def _validate_time_format(self, time_str: str) -> bool:
        """Проверяет, что время в формате ЧЧ:ММ"""
        if not time_str:
            return True  # Пустое значение допустимо
        try:
            datetime.strptime(time_str.strip(), "%H:%M")
            return True
        except ValueError:
            return False
    
    def save_new_activity_fixed(self, *args):
        """Сохраняет новое занятие с валидацией времени"""
        name = self.root.ids.activity_name.text.strip()
        
        if not name:
            self.root.ids.activity_name.error = True
            self.root.ids.activity_name.hint_text = "Название обязательно *"
            return
        
        start_time = self.root.ids.activity_start_time.text.strip()
        end_time = self.root.ids.activity_end_time.text.strip()
        
        # 🔹 Валидация формата времени
        if start_time and not self._validate_time_format(start_time):
            self.root.ids.activity_start_time.error = True
            self.root.ids.activity_start_time.helper_text = "Формат: ЧЧ:ММ"
            return
        
        if end_time and not self._validate_time_format(end_time):
            self.root.ids.activity_end_time.error = True
            self.root.ids.activity_end_time.helper_text = "Формат: ЧЧ:ММ"
            return
        
        # 🔹 Логическая проверка: конец не раньше начала
        if start_time and end_time:
            start_dt = datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.strptime(end_time, "%H:%M")
            if end_dt < start_dt:
                self.root.ids.activity_end_time.error = True
                self.root.ids.activity_end_time.helper_text = "Окончание раньше начала"
                return
        
        # Сохраняем в БД
        self.db.add_activity(
            date_obj=self.selected_date,
            name=name,
            start_time=start_time or None,
            end_time=end_time or None,
            location=self.root.ids.activity_location.text.strip() or None,
            recurrence=self.root.ids.activity_recurrence.text.strip() or "none",
            comment=self.root.ids.activity_comment.text.strip() or None,
            contacts=self.root.ids.activity_contacts.text.strip() or None,
        )
        
        self.back_to_plans( )
    
    def load_monthly_note(self):
        if self.current_month_year:
            year, month = self.current_month_year
            note = self.db.get_monthly_note(year, month)
            self.root.ids.monthly_note_field.text = note
            self.check_monthly_delete_save_buttons_visibility()
    
    def save_monthly_note(self):
        if self.current_month_year:
            year, month = self.current_month_year
            note = self.root.ids.monthly_note_field.text
            self.db.save_monthly_note(year, month, note)

    def check_monthly_delete_save_buttons_visibility(self):
        """Скрывает кнопку, если поле ежемесячной заметки пустое"""
        note_text = self.root.ids.monthly_note_field.text
        btn = self.root.ids.btn_delete_monthly
        if not note_text.strip():
            btn.opacity = 0
            btn.disabled = True
        else:
            btn.opacity = 1
            btn.disabled = False
        btn = self.root.ids.btn_save_monthly
        if not note_text.strip():
            btn.opacity = 0
            btn.disabled = True
        else:
            btn.opacity = 1
            btn.disabled = False

    def delete_monthly_note(self):
        if self.current_month_year:
            year, month = self.current_month_year
            self.root.ids.monthly_note_field.text = ""
            self.db.save_monthly_note(year, month, "")
            self.check_monthly_delete_save_buttons_visibility()


if __name__ == '__main__':
    PlanerApp().run()