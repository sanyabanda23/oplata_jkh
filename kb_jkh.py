from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, WebAppInfo

def start_kb():
    kb_list = [
        [InlineKeyboardButton(text="✅Войти в Сбербанк Онлайн", callback_data='start_sbol')],
        [InlineKeyboardButton(text="❌Очистить чат", callback_data='clear_chat')],
        [InlineKeyboardButton(text="🔎Информация о платежах и реквизитах", callback_data='info_pay_rek')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def vibor_info_rek_kb():
    kb_list = [
        [InlineKeyboardButton(text="🔎Информация о платежах", callback_data='info_pay')],
        [InlineKeyboardButton(text="🔎Информация о реквизитах для оплаты", callback_data='info_rek')],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data='main_menu_info')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def vibor_info_pay():
    kb_list = [
        [InlineKeyboardButton(text="🔎Информация за месяц", callback_data='info_pay_mon')],
        [InlineKeyboardButton(text="🔎Информация по объекту и поставщику", callback_data='info_pay_kf_kp')],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data='main_menu_info')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def vibor_info_post_lsch_kb():
    kb_list = [
        [InlineKeyboardButton(text="🔎Реквизиты поставщиков", callback_data='info_pos')],
        [InlineKeyboardButton(text="🔎Лицевые счета для оплаты", callback_data='info_lsch')],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data='main_menu_info')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def vibor_post_info_kb():
    kb_list = [
        [InlineKeyboardButton(text="ЕРЦ Экотранс", callback_data='gb')],
        [InlineKeyboardButton(text="Газпром межрегионгаз Ростов-на-Дону", callback_data='gz')],
        [InlineKeyboardButton(text="Фонд капиатльного ремонта", callback_data='kr')],
        [InlineKeyboardButton(text="ТНС энерго Ростов-на-Дону", callback_data='lt')],
        [InlineKeyboardButton(text="Теплоэнерго", callback_data='wm')],
        [InlineKeyboardButton(text="Управление Водоканал", callback_data='wt')],
        [InlineKeyboardButton(text="ИВЦ ЖКХ Петровский Квартал", callback_data='ykd')],
        [InlineKeyboardButton(text="РЦ Континент", callback_data='ykf')],
        [InlineKeyboardButton(text="РЦ Тагансервис", callback_data='yki')],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data='main_menu_info')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def vibor_kv_info_kb():
    kb_list = [
        [InlineKeyboardButton(text="1-й Крепостной 24", callback_data='dm')],
        [InlineKeyboardButton(text="Петровская 41", callback_data='pt')],
        [InlineKeyboardButton(text="Фрунзе 79/5,", callback_data='fr')],
        [InlineKeyboardButton(text="Инструментальная 19/3", callback_data='in')],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data='main_menu_info')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def vibor_kv_kb():
    kb_list = [
        [InlineKeyboardButton(text="1-й Крепостной 24", callback_data='dm')],
        [InlineKeyboardButton(text="Петровская 41", callback_data='pt')],
        [InlineKeyboardButton(text="Фрунзе 79/5,", callback_data='fr')],
        [InlineKeyboardButton(text="Инструментальная 19/3", callback_data='in')],
        [InlineKeyboardButton(text="◀️ Главное меню", callback_data='main_menu')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

yes_no_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да")], [KeyboardButton(text="Нет")]], one_time_keyboard=True, resize_keyboard=True)

def opl_zkh_dm():
    kb_list = [
        [InlineKeyboardButton(text="Услуги электроснабжения", callback_data='ltdm')],
        [InlineKeyboardButton(text="Услугии газоснабжения", callback_data='gzdm')],
        [InlineKeyboardButton(text="Услуги управляющей компании", callback_data='ykdm')],
        [InlineKeyboardButton(text="Услуги по обращению с ТКО", callback_data='gbdm')],
        [InlineKeyboardButton(text="Ежемесячный взнос на капитальный ремонт", callback_data='krdm')],
        [InlineKeyboardButton(text="Услуги водоснабжения", callback_data='wtdm')],
        [InlineKeyboardButton(text="◀️ Выбрать другую квартиру для оплаты услуг ЖКХ", callback_data='vibor_kv_menu')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def opl_zkh_pt():
    kb_list = [
        [InlineKeyboardButton(text="Услуги электроснабжения", callback_data='ltpt')],
        [InlineKeyboardButton(text="Услугии газоснабжения", callback_data='gzpt')],
        [InlineKeyboardButton(text="Ежемесячный взнос на капитальный ремонт", callback_data='krpt')],
        [InlineKeyboardButton(text="Услуги водоснабжения", callback_data='wtpt')],
        [InlineKeyboardButton(text="◀️ Выбрать другую квартиру для оплаты услуг ЖКХ", callback_data='vibor_kv_menu')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def opl_zkh_fr():
    kb_list = [
        [InlineKeyboardButton(text="Услугии газоснабжения", callback_data='gzfr')],
        [InlineKeyboardButton(text="Услуги управляющей компании", callback_data='ykfr')],
        [InlineKeyboardButton(text="Ежемесячный взнос на капитальный ремонт", callback_data='krfr')],
        [InlineKeyboardButton(text="◀️ Выбрать другую квартиру для оплаты услуг ЖКХ", callback_data='vibor_kv_menu')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard

def opl_zkh_in():
    kb_list = [
        [InlineKeyboardButton(text="Услуги управляющей компании", callback_data='ykin')],
        [InlineKeyboardButton(text="Услуги по обращению с ТКО", callback_data='gbin')],
        [InlineKeyboardButton(text="Ежемесячный взнос на капитальный ремонт", callback_data='krin')],
        [InlineKeyboardButton(text="Услуги водоснабжения", callback_data='wtin')],
        [InlineKeyboardButton(text="Услуги Теплоэнерго", callback_data='wmin')],
        [InlineKeyboardButton(text="◀️ Выбрать другую квартиру для оплаты услуг ЖКХ", callback_data='vibor_kv_menu')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb_list)
    return keyboard