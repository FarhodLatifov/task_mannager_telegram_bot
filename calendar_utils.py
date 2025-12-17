from datetime import date, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
import calendar

class CalendarCallback(CallbackData, prefix="calendar"):
    action: str
    year: int
    month: int
    day: int

def generate_calendar(year: int = None, month: int = None):
    if year is None: year = date.today().year
    if month is None: month = date.today().month

    markup = []
    
    # Month Year Header
    month_name = calendar.month_name[month]
    markup.append([InlineKeyboardButton(text=f"{month_name} {year}", callback_data="ignore")])

    # Days of Week
    days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    markup.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in days])

    # Days
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=CalendarCallback(action="day", year=year, month=month, day=day).pack()))
        markup.append(row)

    # Navigation
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
        
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    markup.append([
        InlineKeyboardButton(text="<", callback_data=CalendarCallback(action="nav", year=prev_year, month=prev_month, day=1).pack()),
        InlineKeyboardButton(text="Skip", callback_data="skip_date"),
        InlineKeyboardButton(text=">", callback_data=CalendarCallback(action="nav", year=next_year, month=next_month, day=1).pack()),
    ])

    return InlineKeyboardMarkup(inline_keyboard=markup)
