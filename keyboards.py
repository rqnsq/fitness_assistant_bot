from typing import Tuple, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from data import MENUS

NAVIGATION_KEYBOARD = [['Питание', 'Сон', 'Упражнения'], ['Тренер']]
REPLY_MARKUP = ReplyKeyboardMarkup(NAVIGATION_KEYBOARD, resize_keyboard=True)

def create_menu(menu_key: str) -> Tuple[Optional[InlineKeyboardMarkup], str]:
    """
    Генерирует клавиатуру и текст для указанного меню.
    
    Returns:
        Tuple: (Объект клавиатуры или None, Текст меню)
    """
    menu = MENUS.get(menu_key)
    if not menu:
        return None, "Меню не найдено"

    keyboard = []
    # Формируем ряды кнопок
    for row in menu['buttons']:
        keyboard_row = []
        for text, data in row:
            # Если данные начинаются с url:, создаем кнопку-ссылку
            if data.startswith('url:'):
                keyboard_row.append(InlineKeyboardButton(text, url=data[4:]))
            else:
                keyboard_row.append(InlineKeyboardButton(text, callback_data=data))
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard), menu['text']