import asyncio
import logging

# Импорты для VK‑бота (vkbottle 4.4.5)
from vkbottle import Bot as VKBot
from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import PeerRule


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import config_jkh
from handlers_jkh_vk import router_vk  # Ваш роутер для VK‑обработчиков

# Создание VK‑бота
vk_bot = VKBot(token=config_jkh.BOT_TOKEN_VK)


async def main():
    """Основная функция запуска VK‑бота"""
    logger.info("Запуск VK‑бота...")
    try:
        # Запускаем бота, передавая напрямую наш единственный роутер
        await vk_bot.run_polling(
            labeler=router_vk,  # Передаём router_vk вместо отдельного labeler
            auto_reload=True
        )
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info("VK‑бот остановлен")

if __name__ == "__main__":
    # Запуск системы логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # Основная точка входа в программу
    asyncio.run(main())