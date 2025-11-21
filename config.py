import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logger.critical("BOT_TOKEN не найден в переменных окружения")
    exit(1)

try:
    TRAINER_ID = int(os.getenv('TRAINER_ID', 0))
except ValueError:
    logger.critical("TRAINER_ID должен быть числом")
    exit(1)