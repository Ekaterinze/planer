from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

dark_green_hex = '#485935'
light_green_hex = '#CADBB7'
light_hex = '#FFFFFF'

KV = '''
MDScreen:

    MDBottomNavigation:
        panel_color: app.light_green
        text_color_normal: app.dark_green
        text_color_active: app.dark_green
        selected_color_background: app.light

        MDBottomNavigationItem:
            name: 'screen_plans'
            text: 'Планы'
            icon: 'calendar-check'
            MDLabel:
                text: 'Планы'
                halign: 'center'
                theme_text_color: "Custom"
                text_color: app.dark_green

        MDBottomNavigationItem:
            name: 'screen_period'
            text: 'Период'
            icon: 'clock-outline'
            
            MDBoxLayout:
                orientation: "vertical"
                
                # Панель кнопок
                MDBoxLayout:
                    adaptive_height: True
                    md_bg_color: app.light_green
                    padding: dp(5)
                    spacing: dp(5)
                    
                    # Кнопка "Месяц"
                    MDRectangleFlatButton:
                        id: btn_month
                        text: "Месяц"
                        theme_text_color: "Custom"
                        size_hint_x: 0.5
                        on_release: app.switch_tab("month_screen")
                        
                    # Кнопка "Год"
                    MDRectangleFlatButton:
                        id: btn_year
                        text: "Год"
                        theme_text_color: "Custom"
                        size_hint_x: 0.5
                        on_release: app.switch_tab("year_screen")

                # Экраны с контентом
                MDScreenManager:
                    id: inner_sm
                    
                    MDScreen:
                        name: "month_screen"
                        MDLabel:
                            text: "Данные за Месяц"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.dark_green

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
        
        # Цвета для активного и неактивного состояния
        self.active_color = self.dark_green
        self.inactive_color =self.dark_green
        self.inactive_line =self.light_green
        
        return Builder.load_string(KV)

    def on_start(self):
        # Устанавливаем начальное состояние после запуска
        self.switch_tab("month_screen")

    def switch_tab(self, screen_name):
        # Переключаем экран
        self.root.ids.inner_sm.current = screen_name
        
        # Получаем ссылки на кнопки
        btn_month = self.root.ids.btn_month
        btn_year = self.root.ids.btn_year
        
        # Обновляем цвета в зависимости от выбранного экрана
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

PlanerApp().run()