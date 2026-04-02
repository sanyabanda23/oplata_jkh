from vkbottle.bot import Message
from vkbottle import Keyboard, Text, OpenLink

def start_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("✅Войти в Сбербанк Онлайн", payload={"cmd": "start_sbol"}))
        .row()
        .add(Text("❌Очистить чат", payload={"cmd": "clear_chat"}))
        .row()
        .add(Text("🔎Информация о платежах и реквизитах", payload={"cmd": "info_pay_rek"}))
    )
    return keyboard

def vibor_info_rek_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("🔎Информация о платежах", payload={"cmd": "info_pay"}))
        .row()
        .add(Text("🔎Информация о реквизитах для оплаты", payload={"cmd": "info_rek"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}))
    )
    return keyboard

def vibor_info_post_lsch_kb():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("🔎Реквизиты поставщиков", payload={"cmd": "info_pos"}))
        .row()
        .add(Text("🔎Лицевые счета для оплаты", payload={"cmd": "info_lsch"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}))
    )
    return keyboard

def vibor_info_pay():
    keyboard = (
        Keyboard(one_time=False, inline=True)
        .add(Text("🔎Информация за месяц", payload={"cmd": "info_pay_mon"}))
        .row()
        .add(Text("🔎Информация по объекту и поставщику", payload={"cmd": "info_pay_kf_kp"}))
        .row()
        .add(Text("◀️ Главное меню", payload={"cmd": "main_menu_info"}))
    )
    return keyboard