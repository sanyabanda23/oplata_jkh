from aiogram.fsm.state import StatesGroup, State

class Vhod(StatesGroup):
    sms_pasword = State()

class Clear(StatesGroup):
    delete = State()

### Оплата капитального ремонта
class Opl_kr_pt(StatesGroup):
    preparation = State()
    summ = State()

class Opl_kr_fr(StatesGroup):
    preparation = State()
    summ = State()

class Opl_kr_in(StatesGroup):
    preparation = State()
    summ = State()

class Opl_kr_dm(StatesGroup):
    preparation = State()
    summ = State()

### Оплата вывоз ТКО
class Opl_gb_dm(StatesGroup):
    preparation = State()
    summ = State()

class Opl_gb_in(StatesGroup):
    preparation = State()
    summ = State()

### Оплата УК
class Opl_yk_dm(StatesGroup):
    preparation = State()
    summ = State()

class Opl_yk_in(StatesGroup):
    preparation = State()
    summ = State()

class Opl_yk_fr(StatesGroup):
    pok_lt = State()
    pok_cwt = State()
    pok_hwt = State()
    preparation = State()
    summ = State()

### Оплата Теплоэнерго
class Opl_wm_in(StatesGroup):
    preparation = State()
    summ = State()

### Оплата Водоканал
class Opl_wt_dm(StatesGroup):
    pok_wt = State()
    preparation = State()
    summ = State()

class Opl_wt_pt(StatesGroup):
    preparation = State()
    summ = State()

class Opl_wt_in(StatesGroup):
    pok_hwt = State()
    pok_cwt = State()
    preparation = State()
    summ = State()

### Оплата ТНС Энерго
class Opl_lt_dm(StatesGroup):
    pok_lt = State()
    preparation = State()
    summ = State()

class Opl_lt_pt(StatesGroup):
    pok_lt = State()
    preparation = State()
    summ = State()

### Оплата Газпром
class Opl_gz_dm(StatesGroup):
    pok_gz = State()
    preparation = State()
    summ = State()

class Opl_gz_pt(StatesGroup):
    pok_gz = State()
    preparation = State()
    summ = State()

class Opl_gz_fr(StatesGroup):
    preparation = State()
    summ = State()

### Формирование отчетов
class Info_pay_mon(StatesGroup):
    mon = State()

class Info_pay_year(StatesGroup):
    year = State()
    kf = State()
    kp = State()
