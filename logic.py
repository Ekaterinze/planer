# logic.py
from datetime import datetime, date
from typing import List, Dict


def sort_activities_by_status(activities: List[Dict], selected_date: date) -> List[Dict]:
    """Сортирует занятия по статусам: ongoing → upcoming → timeless → past"""
    now = datetime.now()
    result = {'ongoing': [], 'upcoming': [], 'past': [], 'timeless': []}
    
    for act in activities:
        status = _determine_activity_status(act, selected_date, now)
        act['_status'] = status
        result[status].append(act)
    
    # Сортировка внутри групп по времени начала
    for key in result:
        result[key].sort(key=lambda a: a['start_time'] or '99:99')
    
    return result['ongoing'] + result['upcoming'] + result['timeless'] + result['past']


def _determine_activity_status(act: Dict, selected_date: date, now: datetime) -> str:
    """Определяет статус занятия"""
    start = end = None
    
    if act['start_time']:
        start = datetime.combine(selected_date, datetime.strptime(act['start_time'], "%H:%M").time())
    if act['end_time']:
        end = datetime.combine(selected_date, datetime.strptime(act['end_time'], "%H:%M").time())
    
    if (start is None or end is None) and not act['finished']:
        return 'timeless'
    elif start and end and start <= now <= end and not act['finished']:
        return 'ongoing'
    elif start and start > now and not act['finished']:
        return 'upcoming'
    else:
        return 'past'


def format_time_input(text: str, is_focused: bool) -> str:
    """Автоформатирование времени: 1230 → 12:30"""
    digits = ''.join(c for c in text if c.isdigit())[:4]
    
    if len(digits) >= 3:
        return f"{digits[:2]}:{digits[2:]}"
    elif len(digits) == 2 and is_focused:
        return f"{digits}:"
    return digits


def validate_time_format(time_str: str) -> bool:
    """Проверка формата ЧЧ:ММ"""
    if not time_str:
        return True
    try:
        datetime.strptime(time_str.strip(), "%H:%M")
        return True
    except ValueError:
        return False


def validate_time_range(start: str, end: str) -> bool:
    """Проверка: конец не раньше начала"""
    if not start or not end:
        return True
    return datetime.strptime(end, "%H:%M") >= datetime.strptime(start, "%H:%M")


def get_progress_text(completed: int, total: int) -> str:
    """Текст прогресса дня"""
    return f"{completed} из {total}"


def calculate_progress_percent(completed: int, total: int) -> int:
    """Процент выполнения"""
    return (completed * 100 // total) if total > 0 else 0


def get_ru_month_name(month: int) -> str:
    """Название месяца по-русски"""
    months = ['', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
              'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    return months[month] if 0 < month <= 12 else ''