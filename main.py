# main.py
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivymd.app import MDApp
from datetime import date
from widgets.mouth_calendar_widget import MonthCalendar   # импортируем вынесенный класс
from db.database import DatabaseHelper

dark_green_hex = '#485935'
light_green_hex = '#CADBB7'
light_hex = '#FFFFFF'

KV = '''
MDScreen:
    MDBottomNavigation:
        id: bottom_nav
        panel_color: app.light_green
        text_color_normal: app.dark_green
        text_color_active: app.dark_green
        selected_color_background: app.light

        MDBottomNavigationItem:
            name: 'screen_plans'
            text: 'Планы'
            icon: 'calendar-check'
            MDBoxLayout:                     
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                
                MDLabel:
                    id: plans_label
                    text: 'Выберите дату в календаре'
                    halign: 'center'
                    theme_text_color: "Custom"
                    text_color: app.dark_green
                    size_hint_y: None
                    height: dp(40)
                
                # Горизонтальный контейнер для заметки и кнопки
                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(150)
                    
                    MDTextField:
                        id: daily_note_field
                        hint_text: "Заметка на выбранный день"
                        multiline: True
                        size_hint_x: 1 
                        size_hint_y: 1 
                        on_text: app.check_daily_delete_button_visibility()
                        line_color_focus: app.dark_green 
                        hint_text_color_focus: app.dark_green
                        text_color_focus: app.dark_green
                        padding: [dp(10), dp(10), dp(10), dp(10)] 

                    MDRectangleFlatButton:
                        id: btn_delete_daily
                        text: "Удалить"
                        theme_text_color: "Custom"
                        text_color: app.dark_green
                        line_color: app.dark_green
                        size_hint_x: None
                        width: dp(80) 
                        on_release: app.delete_daily_note()

        MDBottomNavigationItem:
            name: 'screen_period'
            text: 'Период'
            icon: 'clock-outline'
            
            MDBoxLayout:
                orientation: "vertical"
                
                MDBoxLayout:
                    adaptive_height: True
                    md_bg_color: app.light_green
                    padding: dp(5)
                    spacing: dp(5)
                    
                    MDRectangleFlatButton:
                        id: btn_month
                        text: "Месяц"
                        theme_text_color: "Custom"
                        size_hint_x: 0.5
                        on_release: app.switch_tab("month_screen")
                        
                    MDRectangleFlatButton:
                        id: btn_year
                        text: "Год"
                        theme_text_color: "Custom"
                        size_hint_x: 0.5
                        on_release: app.switch_tab("year_screen")

                MDScreenManager:
                    id: inner_sm
                    
                    MDScreen:
                        name: "month_screen"
                        BoxLayout:
                            orientation: "vertical"
                            padding: dp(10)
                            spacing: dp(10)
                            
                            BoxLayout:
                                size_hint_y: None
                                height: dp(40)
                                spacing: dp(5)
                                
                                MDRectangleFlatButton:
                                    text: "<<"
                                    size_hint_x: None
                                    width: dp(50)
                                    on_release: app.prev_year()
                                    text_color: app.dark_green
                                    line_color: app.dark_green  
                                
                                MDRectangleFlatButton:
                                    text: "<"
                                    size_hint_x: None
                                    width: dp(50)
                                    on_release: app.prev_month()
                                    text_color: app.dark_green
                                    line_color: app.dark_green  
                                
                                MDLabel:
                                    id: month_label
                                    text: ""
                                    halign: "center"
                                    theme_text_color: "Custom"
                                    text_color: app.dark_green 
                                
                                MDRectangleFlatButton:
                                    text: ">"
                                    size_hint_x: None
                                    width: dp(50)
                                    on_release: app.next_month()
                                    text_color: app.dark_green
                                    line_color: app.dark_green  
                                
                                MDRectangleFlatButton:
                                    text: ">>"
                                    size_hint_x: None
                                    width: dp(50)
                                    on_release: app.next_year()
                                    text_color: app.dark_green
                                    line_color: app.dark_green  
                            
                            MonthCalendar:   
                                id: calendar
                            
                            # Горизонтальный контейнер для месячной заметки и кнопки
                            MDBoxLayout:
                                orientation: 'horizontal'
                                spacing: dp(10)
                                size_hint_y: None
                                height: dp(150)
                                
                                MDTextField:
                                    id: monthly_note_field
                                    hint_text: "Заметка на текущий месяц"
                                    multiline: True
                                    size_hint_x: 1
                                    size_hint_y: 1
                                    on_text: app.check_monthly_delete_button_visibility()
                                    line_color_focus: app.dark_green 
                                    hint_text_color_focus: app.dark_green
                                    text_color_focus: app.dark_green
                                    padding: [dp(10), dp(10), dp(10), dp(10)]

                                MDRectangleFlatButton:
                                    id: btn_delete_monthly
                                    text: "Удалить"
                                    theme_text_color: "Custom"
                                    text_color: app.dark_green
                                    line_color: app.dark_green
                                    size_hint_x: None
                                    width: dp(80)
                                    on_release: app.delete_monthly_note()

                    MDScreen:
                        name: "year_screen"
                        MDLabel:
                            text: "Данные за Год"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.dark_green

        MDBottomNavigationItem:
            name: 'screen_calc'
            text: 'Расчет'
            icon: 'calculator'
            MDLabel:
                text: 'Расчет'
                halign: 'center'
                theme_text_color: "Custom"
                text_color: app.dark_green
'''

class PlanerApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.dark_green = get_color_from_hex(dark_green_hex)
        self.light_green = get_color_from_hex(light_green_hex)
        self.light = get_color_from_hex(light_hex)

        self.db = DatabaseHelper()            # инициализация БД
        self.current_month_year = None 
        
        self.active_color = self.dark_green
        self.inactive_color = self.dark_green
        self.inactive_line = self.light_green
        
        self.selected_date = None
        
        return Builder.load_string(KV)
    
    def on_start(self):
        self.root.ids.calendar.callback = self.on_day_selected
        todate=date.today()
        self.on_day_selected( todate.day, todate.month, todate.year )
        self.switch_tab("month_screen")
        self.update_month_header()
        self.load_monthly_note()
        self.check_daily_delete_button_visibility()
        self.check_monthly_delete_button_visibility()
    
    
    def update_month_header(self):
        calendar_widget = self.root.ids.calendar
        month_name = calendar_widget.current_date.strftime('%B %Y')
        self.root.ids.month_label.text = month_name.capitalize()
        self.current_month_year = (calendar_widget.current_date.year, calendar_widget.current_date.month)
        self.load_monthly_note()
    
    def prev_month(self):
        self.root.ids.calendar.go_prev_month()
        self.update_month_header()
    
    def next_month(self):
        self.root.ids.calendar.go_next_month()
        self.update_month_header()

    def prev_year(self):
        self.root.ids.calendar.go_prev_year()
        self.update_month_header()
    
    def next_year(self):
        self.root.ids.calendar.go_next_year()
        self.update_month_header()
    
    def on_day_selected(self, day, month, year):
        self.selected_date = date(year, month, day)
        self.root.ids.plans_label.text = f'Выбрана дата: {self.selected_date.strftime("%d.%m.%Y")}'
        self.root.ids.bottom_nav.switch_tab('screen_plans')
        self.load_daily_note()
    
    def switch_tab(self, screen_name):
        self.root.ids.inner_sm.current = screen_name
        
        btn_month = self.root.ids.btn_month
        btn_year = self.root.ids.btn_year
        
        if screen_name == "month_screen":
            btn_month.text_color = self.active_color
            btn_month.line_color = self.active_color
            btn_year.text_color = self.inactive_color
            btn_year.line_color = self.inactive_line
        else:
            btn_year.text_color = self.active_color
            btn_year.line_color = self.active_color
            btn_month.text_color = self.inactive_color
            btn_month.line_color = self.inactive_line


    def load_daily_note(self):
        if self.selected_date:
            note = self.db.get_daily_note(self.selected_date)
            self.root.ids.daily_note_field.text = note
            self.check_daily_delete_button_visibility()
    
    def save_daily_note(self):
        if self.selected_date:
            note = self.root.ids.daily_note_field.text
            self.db.save_daily_note(self.selected_date, note)

    def check_daily_delete_button_visibility(self):
        """Скрывает кнопку, если поле ежедневной заметки пустое"""
        note_text = self.root.ids.daily_note_field.text
        btn = self.root.ids.btn_delete_daily
        # Если текст пустой или состоит только из пробелов - скрываем
        if not note_text.strip():
            btn.opacity = 0
            btn.disabled = True
        else:
            btn.opacity = 1
            btn.disabled = False

    def delete_daily_note(self):
        if self.selected_date:
            self.root.ids.daily_note_field.text = ""
            self.db.save_daily_note(self.selected_date, "")
            self.check_daily_delete_button_visibility()
    
    def load_monthly_note(self):
        if self.current_month_year:
            year, month = self.current_month_year
            note = self.db.get_monthly_note(year, month)
            self.root.ids.monthly_note_field.text = note
            self.check_monthly_delete_button_visibility()
    
    def save_monthly_note(self):
        if self.current_month_year:
            year, month = self.current_month_year
            note = self.root.ids.monthly_note_field.text
            self.db.save_monthly_note(year, month, note)

    def check_monthly_delete_button_visibility(self):
        """Скрывает кнопку, если поле ежемесячной заметки пустое"""
        note_text = self.root.ids.monthly_note_field.text
        btn = self.root.ids.btn_delete_monthly
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
            self.check_monthly_delete_button_visibility()

if __name__ == '__main__':
    PlanerApp().run()