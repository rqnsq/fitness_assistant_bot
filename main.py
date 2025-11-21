from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from config import TOKEN
from handlers import start, callback_query_handler, message_handler, logger

def main() -> None:
    if not TOKEN:
        logger.error("Токен не установлен. Проверьте файл .env")
        return

    updater = Updater(TOKEN)
    dp = updater.dispatcher
    
    # Регистрация обработчиков
    dp.add_handler(CommandHandler('start', start))
    # Фильтр text & ~command означает "текст, но НЕ команды вроде /start"
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    
    logger.info("||| Бот запущен...")
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()