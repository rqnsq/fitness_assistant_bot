from typing import Optional
from telegram import Update, InputMediaPhoto, error
from telegram.ext import CallbackContext
from data import MENU_PHOTOS, MENUS
from keyboards import create_menu
import time

def get_menu_key(callback_data: str) -> Optional[str]:
    """
    Возвращает родительскую категорию (ключ меню) для callback_data.
    Динамически ищет его в структуре MENUS.
    
    Returns:
        str: Ключ меню (например, 'nutrition'), если найден.
        None: Если ключ не найден.
    """
    # Проходим по словарю MENUS, чтобы найти, к какому разделу относится кнопка
    for parent_key, menu_data in MENUS.items():
        for row in menu_data.get('buttons', []):
            for _, data in row:
                if data == callback_data:
                    return parent_key
    return None

def check_spam(context: CallbackContext) -> bool:
    """
    Проверяет, не совершено ли действие слишком быстро (анти-спам).
    
    Returns:
        bool: True, если это спам (нужно блокировать), False, если всё ок.
    """
    last_action = context.user_data.get('last_action_time', 0)
    
    # Ограничение: 1 секунда между действиями
    if time.time() - last_action < 1:
        return True
        
    context.user_data['last_action_time'] = time.time()
    return False

def send_menu_with_photo(update: Update, menu_key: str, context: CallbackContext) -> None:
    """
    Отправляет или редактирует сообщение, добавляя фото и клавиатуру.
    Определяет, нужно ли редактировать старое сообщение или слать новое.
    """
    keyboard, text = create_menu(menu_key)
    photo_url = MENU_PHOTOS.get(menu_key)
    
    # Сценарий 1: Пользователь нажал на инлайн-кнопку (Callback)
    if update.callback_query:
        query = update.callback_query
        chat_id = query.message.chat_id
        
        try:
            if photo_url:
                # Пытаемся заменить медиа (фото) на лету
                query.edit_message_media(
                    media=InputMediaPhoto(media=photo_url, caption=text),
                    reply_markup=keyboard
                )
            else:
                # Если фото нет, меняем только текст
                query.edit_message_text(text=text, reply_markup=keyboard)
        except error.BadRequest:
            # Бывает, что Телеграм не дает изменить сообщение (например, оно слишком старое).
            # В таком случае удаляем старое (если получится) и шлем новое.
            try:
                query.delete_message()
            except error.BadRequest:
                pass 
            
            if photo_url:
                context.bot.send_photo(chat_id=chat_id, photo=photo_url, caption=text, reply_markup=keyboard)
            else:
                context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)
    
    # Сценарий 2: Обычное текстовое сообщение (например, из нижнего меню)
    else:
        if photo_url:
            update.message.reply_photo(photo=photo_url, caption=text, reply_markup=keyboard)
        else:
            update.message.reply_text(text, reply_markup=keyboard)