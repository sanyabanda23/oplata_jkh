import asyncio
import logging


from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties


import config_jkh
from handlers_jkh import router_jkh


# созданиие бота для работы с TelegramAPI, с форматированиием сообщений в формате HTML
bot = Bot(token=config_jkh.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))



async def main():
    storage = RedisStorage.from_url('redis://127.0.0.1:6379/0')
    # создание диспетчера для обработки входящих сообщений и других обновлений, поступающих от Telegram в оперативной памяти
    dp = Dispatcher(storage=storage)
    dp.include_router(router_jkh)
    # удаляет все обновления из оперативной памяти после работы бота
    await bot.delete_webhook(drop_pending_updates=True)
    # запусскает бота и начинает опрашивать сервер на наличие новых сообщений, с учетом зарегистрированных обработчиков
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    # запуск системы логирирования, где уровень логирирования начинается с INFO
    logging.basicConfig(level=logging.INFO)
    # используется в качестве основной точки входа в программу
    asyncio.run(main())
                                                                                                                                                                   