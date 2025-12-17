from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from translations import get_text

def main_menu(lang: str = 'en'):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text(lang, 'menu_list')), KeyboardButton(text=get_text(lang, 'menu_add'))],
            [KeyboardButton(text=get_text(lang, 'menu_search')), KeyboardButton(text=get_text(lang, 'menu_lang'))],
        ],
        resize_keyboard=True,
    )

def categories(lang: str = 'en'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, 'cat_work'), callback_data="cat_Work"), InlineKeyboardButton(text=get_text(lang, 'cat_personal'), callback_data="cat_Personal")],
            [InlineKeyboardButton(text=get_text(lang, 'cat_shopping'), callback_data="cat_Shopping"), InlineKeyboardButton(text=get_text(lang, 'cat_others'), callback_data="cat_Others")],
        ]
    )

def priorities(lang: str = 'en'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, 'prio_high'), callback_data="prio_High"), InlineKeyboardButton(text=get_text(lang, 'prio_medium'), callback_data="prio_Medium"), InlineKeyboardButton(text=get_text(lang, 'prio_low'), callback_data="prio_Low")],
            [InlineKeyboardButton(text=get_text(lang, 'skip'), callback_data="skip_prio")]
        ]
    )

def skip_attachment(lang: str = 'en'):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=get_text(lang, 'skip'), callback_data="skip_att")]]
    )

def task_actions(task_id: int, lang: str = 'en'):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text(lang, 'done'), callback_data=f"done_{task_id}"),
                InlineKeyboardButton(text=get_text(lang, 'delete'), callback_data=f"delete_{task_id}"),
            ]
        ]
    )

language_selection = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"), InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
    ]
)
