from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from widgets.variables import CARD_HEIGHT, RADIUS


class ActivityCard(MDBoxLayout):
    """Карточка занятия с кнопками действий"""
    
    def __init__(self, activity: dict, colors: dict, 
                 on_check=None, on_delete=None, **kwargs):
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', CARD_HEIGHT)
        super().__init__(orientation='horizontal', **kwargs)
        
        self.activity = activity
        self.colors = colors
        self.on_check = on_check
        self.on_delete = on_delete
        
        self._build_ui()
    
    def _build_ui(self):
        # Формируем отображаемый текст
        time_str = self._format_time()
        location_str = f" • {self.activity['location']}" if self.activity['location'] else ""
        display_text = f"{time_str}{self.activity['name']}{location_str}"
        
        # Цвета в зависимости от статуса
        border_color, content_bg, text_color, border_width = self._get_colors()
        
        # Внешняя рамка
        border_card = MDCard(
            size_hint_y=None,
            height=CARD_HEIGHT + 2 * border_width,
            md_bg_color=border_color,
            radius=[RADIUS + border_width],
            elevation=0,
            padding=border_width,
            orientation='horizontal'
        )
        
        # Внутренний контент
        content_card = MDCard(
            size_hint_y=None,
            height=CARD_HEIGHT,
            md_bg_color=content_bg,
            radius=[RADIUS],
            elevation=0,
            padding=dp(10),
            spacing=dp(10),
            orientation='horizontal'
        )
        
        # Текст занятия
        label = MDLabel(
            text=display_text, halign="left",
            theme_text_color="Custom", text_color=text_color,
            size_hint_x=1, shorten=True, shorten_from="right"
        )
        content_card.add_widget(label)
        
        # Кнопки действий
        btn_size = min(dp(50), dp((CARD_HEIGHT - 5)) // 2)
        buttons = self._create_buttons(btn_size)
        content_card.add_widget(buttons)
        
        border_card.add_widget(content_card)
        self.add_widget(border_card)
    
    def _format_time(self) -> str:
        act = self.activity
        if act['start_time'] and act['end_time']:
            return f"{act['start_time']}–{act['end_time']}  "
        elif act['start_time']:
            return f"с {act['start_time']}  "
        return ""
    
    def _get_colors(self) -> tuple:
        status = self.activity['_status']
        colors = self.colors
        
        if status == 'ongoing':
            return colors['dark_accent'], colors['light'], colors['dark_accent'], dp(3)
        elif status == 'past':
            return colors['dark_semi'], colors['light'], colors['dark_semi'], dp(1)
        else:
            return colors['dark_transparent'], colors['light'], colors['dark'], dp(1)
    
    def _create_buttons(self, size: float) -> FloatLayout:
        container = FloatLayout(size_hint_x=None, size=(dp(size), dp(CARD_HEIGHT)))
        
        check_btn = MDIconButton(
            icon="check-all" if self.activity['finished'] else "check",
            icon_color=self.colors['dark_accent'],
            size=(dp(size), dp(size)),
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        if self.on_check:
            check_btn.bind(on_release=lambda x: self.on_check(self.activity['id']))
        
        del_btn = MDIconButton(
            icon="delete-outline",
            icon_color=self.colors['dark_accent'],
            size=(dp(size), dp(size)),
            pos_hint={'center_x': 0.5, 'center_y': 0.25}
        )
        if self.on_delete:
            del_btn.bind(on_release=lambda x: self.on_delete(self.activity['id']))
        
        container.add_widget(check_btn)
        container.add_widget(del_btn)
        return container


class DayProgressCard(MDBoxLayout):
    """Карточка прогресса дня"""
    
    def __init__(self, completed: int, total: int, colors: dict, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        from logic import get_progress_text, calculate_progress_percent
        
        border_width = dp(1)
        
        border_card = MDCard(
            size_hint_y=None,
            height=CARD_HEIGHT + 2 * border_width,
            md_bg_color=colors['dark'],
            radius=[RADIUS + border_width],
            elevation=0,
            padding=border_width,
            orientation='horizontal'
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None, height=CARD_HEIGHT,
            md_bg_color=colors['light'],
            radius=[RADIUS],
            padding=dp(10), spacing=dp(10)
        )
        
        # Верхняя строка
        header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=CARD_HEIGHT//2)
        header.add_widget(MDLabel(text='Прогресс дня', halign="left", text_color=colors['dark']))
        header.add_widget(MDLabel(
            text=get_progress_text(completed, total), 
            halign="right", text_color=colors['dark']
        ))
        
        # Прогресс-бар
        progress = MDProgressBar(
            value=calculate_progress_percent(completed, total),
            color=colors['dark_accent'],
            back_color=colors['dark_accent_dark_light']
        )
        
        content.add_widget(header)
        content.add_widget(progress)
        border_card.add_widget(content)
        self.add_widget(border_card)