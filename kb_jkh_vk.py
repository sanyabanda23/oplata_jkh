from vkbottle.bot import Message
from vkbottle import Keyboard, Text, OpenLink

def start_kb():
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("✅Войти в Сбербанк Онлайн", payload={"cmd": "start_sbol"}))
        .row()
        .add(Text("❌Очистить чат", payload={"cmd": "clear_chat"}))
        .row()
        .add(Text("🔎Информация о платежах и реквизитах", payload={"cmd": "info_pay_rek"}))
    )
    return keyboard