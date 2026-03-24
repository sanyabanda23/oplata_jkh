import asyncio

from vkbottle.framework.labeler import BotLabeler
from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import ABCRule
from vkbottle import CtxStorage

import mysql.connector as con
import config_jkh, utils_jkh, text_jkh, kb_jkh_vk

# Создаём Labeler (аналог Dispatcher в aiogram)
router_vk = BotLabeler()
ctx = CtxStorage()
driver_jkh = utils_jkh.SBOL()
from main_jkh_vk import vk_bot

# Функция для проверки чата
class MyRule(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        # Здесь можно добавить свою логику проверки чата
        # Например, проверка ID чата
        if event.chat_id == 1 and event.from_id == 9028754:  # Замените на ID вашего чата
            return True
        return False

@router_vk.message(MyRule(), text="/start")
async def start_handler(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer(text_jkh.hello_text, keyboard=kb_jkh_vk.start_kb())

@router_vk.message(MyRule())
async def echo_handler(message: Message):
    await message.answer(f"Вы написали: {message.text} в чат {message.chat_id}, {message.from_id}, {message.peer_id}")