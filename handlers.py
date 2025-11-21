from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, error
from telegram.ext import CallbackContext
from data import MENUS, RESPONSES
from keyboards import REPLY_MARKUP
from config import TRAINER_ID, logger
from utils import get_menu_key, send_menu_with_photo, check_spam

def start(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start. Показывает главное меню."""
    update.message.reply_text("Выберите раздел:", reply_markup=REPLY_MARKUP)

def callback_query_handler(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия на инлайн-кнопки."""
    query = update.callback_query
    
    # 1. Проверка на частые клики
    if check_spam(context):
        query.answer("Слишком быстро! Подождите секунду.", show_alert=False)
        return

    query.answer() # Убираем часики загрузки на кнопке
    data = query.data

    # 2. Логика: Задать вопрос тренеру
    if data == 'ask_question':
        try:
            # Вместо удаления просто меняем текст на приглашение к вводу
            query.edit_message_text(
                text="Напишите ваш вопрос одним сообщением:",
                reply_markup=None # Убираем кнопки, чтобы не мешали
            )
        except error.BadRequest:
            # Если не вышло изменить, шлем новое
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Напишите ваш вопрос одним сообщением:"
            )
        
        # Ставим флаг, что следующее сообщение от юзера — это вопрос
        context.user_data['waiting_for_question'] = True
        return

    # 3. Логика: Вывод ответа из базы знаний (RESPONSES)
    if data in RESPONSES:
        parent_menu = get_menu_key(data)
        # Кнопка "Назад" возвращает в предыдущее меню
        back_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton('Назад', callback_data=f'back_to_{parent_menu}')]
        ])
        try:
            query.edit_message_text(text=RESPONSES[data], reply_markup=back_btn)
        except error.BadRequest:
            query.delete_message()
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=RESPONSES[data],
                reply_markup=back_btn
            )
    
    # 4. Логика: Обработка кнопки "Назад"
    elif data.startswith('back_to_'):
        # Вытаскиваем ключ меню из callback_data (например, back_to_nutrition -> nutrition)
        menu_key = data.split('back_to_')[1]
        if menu_key in MENUS:
            send_menu_with_photo(update, menu_key, context)

def message_handler(update: Update, context: CallbackContext) -> None:
    """Обработка всех текстовых сообщений."""
    user_text = update.message.text
    
    # Анти-спам
    if check_spam(context):
        return 
    
    # Если режим ожидания вопроса активен
    if context.user_data.get('waiting_for_question'):
        user = update.message.from_user
        user_ref = f"@{user.username}" if user.username else f"ID: {user.id}"
        
        admin_msg = f"Вопрос от {user_ref}:\n\n{user_text}"
        
        if TRAINER_ID != 0:
            try:
                context.bot.send_message(chat_id=TRAINER_ID, text=admin_msg)
                update.message.reply_text("Вопрос отправлен тренеру.")
            except error.TelegramError as e:
                logger.error(f"Не удалось отправить вопрос: {e}")
                update.message.reply_text("Ошибка доставки. Попробуйте позже.")
        else:
            update.message.reply_text("ID тренера не настроен.")

        # Сбрасываем флаг и возвращаем меню
        context.user_data['waiting_for_question'] = False
        start(update, context)
        return

    # Маппинг для нижнего меню (Reply Keyboard)
    mapping = {
        'Питание': 'nutrition',
        'Упражнения': 'exercises',
        'Тренер': 'trainer',
        'Сон': 'sleep'
    }
    
    if user_text in mapping:
        send_menu_with_photo(update, mapping[user_text], context)
    else:
        # На любой непонятный текст кидаем в начало
        start(update, context)