import asyncio
import json
import logging
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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

# Функция для хендлера payload. Аналог callback 
class PayloadABCRule(ABCRule[Message]):
    async def check(self, message: Message) -> bool:
        payload = message.payload
        if not payload:
            return False
        else:
            payload_dict = json.loads(payload)
        
        # Проверяем, что payload - это JSON
        if isinstance(payload_dict, dict):
            cmd_value = payload_dict.get("cmd")
            return cmd_value == self.cmd if cmd_value else False
        else:
            return False

    def __init__(self, cmd: str):
        self.cmd = cmd
    
@router_vk.message(MyRule(), text="/start")
async def start_handler(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    logger.info("Вызвано главное меню")
    await message.answer(text_jkh.hello_text, keyboard=kb_jkh_vk.start_kb())

### Реакция на кнопку гравное меню
@router_vk.message(MyRule(), PayloadABCRule('main_menu'))
async def main_menu(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    driver_jkh.quit_driver()
    logger.info("Вызвано главное меню")
    await message.answer('Главное меню', keyboard=kb_jkh_vk.start_kb())

@router_vk.message(MyRule(), PayloadABCRule('main_menu_info'))
async def main_menu_info(message: Message):
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    logger.info("Вызвано главное меню")
    await message.answer('Главное меню', keyboard=kb_jkh_vk.start_kb())

### Формирование отчетов
@router_vk.message(MyRule(), PayloadABCRule('info_pay_rek'))
async def vibor_info(message: Message):
    logger.info(f"Вызвано меню отчетов. cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer(text_jkh.vibor_info, keyboard=kb_jkh_vk.vibor_info_rek_kb())

@router_vk.message(MyRule(), PayloadABCRule('info_rek'))
async def vibor_info_rek(message: Message):
    logger.info(f"cmd={message.payload}")
    try:
        await vk_bot.state_dispenser.delete(message.peer_id)
    except KeyError:
        pass  # Состояние не найдено — игнорируем
    await message.answer('Выбери тип отчета о реквизитах', keyboard=kb_jkh_vk.vibor_info_post_lsch_kb())



@router_vk.message()
async def check_all(message: Message):
    logger.info(f"Вызвано меню отчетов. cmd={message.payload}")