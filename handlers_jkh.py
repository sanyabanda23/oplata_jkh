import asyncio
from aiogram import F, Router, types, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.input_file import FSInputFile
import mysql.connector as con

import kb_jkh, utils_jkh, text_jkh
from config_jkh import settings
from state_jkh import Vhod, Clear, Opl_kr_pt, Opl_kr_fr, Opl_kr_in, Opl_kr_dm
from state_jkh import Opl_gb_dm, Opl_gb_in, Opl_yk_dm, Opl_yk_in, Opl_yk_fr
from state_jkh import Opl_wm_in, Opl_wt_dm, Opl_wt_pt, Opl_wt_in, Opl_lt_dm
from state_jkh import Opl_lt_pt, Opl_gz_dm, Opl_gz_pt, Opl_gz_fr, Info_pay_mon, Info_pay_year

router_jkh = Router()
driver_jkh = utils_jkh.SBOL()
from main_jkh import bot as b
# выполнение команды старт
@router_jkh.message(F.from_user.id == settings.tg_user_id, CommandStart())
async def start_handler(msg: Message, state: FSMContext):
    await state.clear() # завершение сценарии, которые не довели до конца (используй во всех коммандах!!!)
    await msg.answer(text_jkh.hello_text, reply_markup=kb_jkh.start_kb())

### Вход в Сбербанк оннлайнн
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'start_sbol')
async def start_vhod_sbol(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Начата процедура входа')
    if driver_jkh.initialize_driver():
        driver_jkh.open_website(settings.URL_vhod)
        await call.message.edit_text('Введите пароль из СМС-сообщения')
        if driver_jkh.vhod_tel_parol():
            await state.set_state(Vhod.sms_pasword)
        else:
            driver_jkh.close_driver()
            await call.message.answer(text_jkh.falling_vhod, reply_markup=kb_jkh.start_kb())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Vhod.sms_pasword)
async def input_sms(msg: Message, state: FSMContext):
    await state.update_data(sms_pasword=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Код из СМС принят')
    data = await state.get_data()
    if driver_jkh.vvod_is_sms(data.get("sms_pasword")):
        await msg.answer(text_jkh.success_vhod, reply_markup=kb_jkh.vibor_kv_kb())
        await state.clear()
    else:
        await state.clear()
        driver_jkh.close_driver()
        await msg.answer(text_jkh.falling_vhod, reply_markup=kb_jkh.start_kb())

### Реакция на кнопку гравное меню
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'main_menu')
async def main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    driver_jkh.quit_driver()
    await call.message.answer('Главное меню', reply_markup=kb_jkh.start_kb())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'main_menu_info')
async def main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Главное меню', reply_markup=kb_jkh.start_kb())

### Удаление сообщение из чата
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'clear_chat')
async def cmd_clear(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Удалить сообщения из чата?', reply_markup=kb_jkh.yes_no_kb)
    await state.set_state(Clear.delete)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Clear.delete)
async def delete_msg(msg: Message, state: FSMContext):
    await state.update_data(delete=msg.text)
    try:  
        # Все сообщения, начиная с текущего и до первого (message_id = 0)  
        for i in range(msg.message_id, 0, -1):  
            await b.delete_message(msg.from_user.id, i)
        await msg.edit_reply_markup(reply_markup=None)
        await state.clear()  
    except TelegramBadRequest as ex:  
        # Если сообщение не найдено (уже удалено или не существует), код ошибки — «Bad Request: message to delete not found»  
        if ex.message == 'Bad Request: message to delete not found':
            await state.clear()  
            print("Все сообщения удалены")

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Clear.delete)
async def delete_msg(msg: Message, state: FSMContext):
    await msg.edit_reply_markup(reply_markup=None)
    await state.clear()

### Формирование отчетов
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_pay_rek')
async def vibor_info(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text_jkh.vibor_info, reply_markup=kb_jkh.vibor_info_rek_kb())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_rek')
async def vibor_info_rek(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Выбери тип отчета о реквизитах', reply_markup=kb_jkh.vibor_info_post_lsch_kb())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_pay')
async def vibor_info_pay(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Выбери тип отчета о платежах', reply_markup=kb_jkh.vibor_info_pay())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_pos')
async def vibor_rek_pos_info(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отчет формируется')
    utils_jkh.select_from_postav()
    doc = FSInputFile('postavshiki.pdf')
    await call.message.answer_photo(photo=doc)
    await b.send_document(call.message.chat.id, document=doc)  
    await call.message.answer('Отправляю вам отчет в формате PDF')

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_lsch')
async def vibor_rek_lsch_info(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отчет формируется')
    utils_jkh.select_from_lsch()
    doc = FSInputFile('l_sch.pdf')
    await call.message.answer_photo(photo=doc)
    await b.send_document(call.message.chat.id, document=doc)  
    await call.message.answer('Отправляю вам отчет в формате PDF')

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_pay_mon')
async def info_pay_mon(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(text_jkh.info_pay_mon)
    await state.set_state(Info_pay_mon.mon)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Info_pay_mon.mon)
async def info_pay_mon(msg: Message, state: FSMContext):        
    await state.update_data(mon=msg.text)
    data_mon = await state.get_data()
    await msg.answer('Отчет формируется')
    summ = utils_jkh.select_from_pay_month(month=data_mon.get('mon'))
    doc = FSInputFile('month_pay.pdf')
    await msg.answer_photo(caption='Cумма платежей составила - {:.2f}'.format(summ), photo=doc)
    await b.send_document(msg.chat.id, document=doc)  
    await msg.answer('Отправляю вам отчет в формате PDF')
    await state.clear()

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'info_pay_kf_kp')
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Выбери квартиру', reply_markup=kb_jkh.vibor_kv_info_kb())
    await state.set_state(Info_pay_year.kf)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'dm', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='dm')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'pt', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='pt')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'fr', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='fr')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'in', Info_pay_year.kf)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kf='in')
    await call.message.edit_text('Выбери поставщика', reply_markup=kb_jkh.vibor_post_info_kb())
    await state.set_state(Info_pay_year.kp)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gb', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='gb')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gz', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='gz')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'kr', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='kr')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'lt', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='lt')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wm', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='wm')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykd', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='ykd')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykf', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='ykf')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'yki', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='yki')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wt', Info_pay_year.kp)
async def info_pay_year(call: CallbackQuery, state: FSMContext):
    await state.update_data(kp='wt')
    await call.message.answer(text_jkh.info_pay_year)
    await state.set_state(Info_pay_year.year)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Info_pay_year.year)
async def info_pay_year(msg: Message, state: FSMContext):        
    await state.update_data(year=msg.text)
    data = await state.get_data()
    await msg.answer('Отчет формируется')
    utils_jkh.select_from_pay_year(kf=data.get('kf'), kp=data.get('kp'), year=data.get('year'))
    doc = FSInputFile('year_pay.pdf')
    await msg.answer_photo(photo=doc)
    await b.send_document(msg.chat.id, document=doc)  
    await msg.answer('Отправляю вам отчет в формате PDF')
    await state.clear()


### Реакция на кнопки в клавиатуре выбор квартиры
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'dm')
async def opl_zkh_dm(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'dm' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await call.message.edit_text(text_jkh.oplata_za.format(data[0][0]), reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'fr')
async def opl_zkh_fr(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'fr' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await call.message.edit_text(text_jkh.oplata_za.format(data[0][0]), reply_markup=kb_jkh.opl_zkh_fr())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'pt')
async def opl_zkh_pt(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'pt' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await call.message.edit_text(text_jkh.oplata_za.format(data[0][0]), reply_markup=kb_jkh.opl_zkh_pt())

@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'in')
async def opl_zkh_in(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    select = ''' SELECT name FROM flat_ls WHERE kf = 'in' '''
    cursor.execute(select)
    data = cursor.fetchall()
    connection.commit()
    print('Данные получены')
    cursor.close()
    connection.close()
    await call.message.edit_text(text_jkh.oplata_za.format(data[0][0]), reply_markup=kb_jkh.opl_zkh_in())

###### Реакция кнопок в клавиатуре оплата ЖКХ
# Обратно для выбора квартиры 
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'vibor_kv_menu')
async def back_vibor_kv(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Выбери квартиру для оплаты услуг ЖКХ', reply_markup=kb_jkh.vibor_kv_kb())


### Оплата кап ремонт Петровская
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'krpt')
async def opl_kr_pt_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
      host=settings.con_sql[0],
      user=settings.con_sql[1],
      password=settings.con_sql[2],
      database=settings.con_sql[3]
    )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_pt.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_kr_pt.preparation)
async def opl_kr_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'pt', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_kr_pt.preparation)
async def opl_kr_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_kr_pt.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_kr_pt.summ)
async def opl_kr_pt(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_pt.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())

# Оплата кап ремонт Фрунзе
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'krfr')
async def opl_kr_fr_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_fr.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_kr_fr.preparation)
async def opl_kr_fr(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'fr', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_fr())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_fr())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_kr_fr.preparation)
async def opl_kr_fr(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_kr_fr.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_kr_fr.summ)
async def opl_kr_fr(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_fr.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())

# Оплата кап ремонт Инструментальная
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'krin')
async def opl_kr_in_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_in.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_kr_in.preparation)
async def opl_kr_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_kr_in.preparation)
async def opl_kr_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_kr_in.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_kr_in.summ)
async def opl_kr_in(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_in.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

# Оплата кап ремонт Дом
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'krdm')
async def opl_kr_dm_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr_dm(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_dm.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_kr_dm.preparation)
async def opl_kr_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_kr_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'kr', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_kr_dm.preparation)
async def opl_kr_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_kr_dm.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_kr_dm.summ)
async def opl_kr_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, kap_rem, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'kr' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_kr(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_kr_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

### Оплата вывоз ТКО Дом
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gbdm')
async def opl_gb_dm_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gb_dm.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_gb_dm.preparation)
async def opl_gb_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_gb_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'gb', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_gb_dm.preparation)
async def opl_gb_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_gb_dm.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gb_dm.summ)
async def opl_gb_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gb_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

### Оплата вывоз ТКО Инструментальная
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gbin')
async def opl_gb_in_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gb_in.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_gb_in.preparation)
async def opl_gb_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_gb_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'gb', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_gb_in.preparation)
async def opl_gb_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_gb_in.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gb_in.summ)
async def opl_gb_in(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, garbage, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'gb' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gb(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gb_in.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

### Оплата УК дом
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykdm')
async def opl_yk_dm_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'ykd' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        summ = str(data[0][4])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_yk_dm(inn=inn, l_sch=l_sch, schet=schet, bik=bik, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_yk_dm.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_yk_dm.preparation)
async def opl_yk_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_yk_dm_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'ykd', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_yk_dm.preparation)
async def opl_yk_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_yk_dm.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_yk_dm.summ)
async def opl_yk_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'ykd' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_yk_dm(inn=inn, l_sch=l_sch, schet=schet, bik=bik, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_yk_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

### Оплата УК Инструментальная
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykin')
async def opl_yk_in_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT yk, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'yki' '''
        cursor.execute(select)
        data = cursor.fetchall()
        l_sch = data[0][0]
        summ = str(data[0][1])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_yk_in(l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_yk_in.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_yk_in.preparation)
async def opl_yk_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_yk_in_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'yki', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_yk_in.preparation)
async def opl_yk_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_yk_in.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_yk_in.summ)
async def opl_yk_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT yk, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'yki' '''
        cursor.execute(select)
        data = cursor.fetchall()
        l_sch = data[0][0]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_yk_in(l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_yk_in.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

### Оплата УК Фрунзе
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ykfr')
async def opl_yk_fr_pok_lt(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Укажи показания счетчика электроэнергии.')
    await state.set_state(Opl_yk_fr.pok_lt)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_yk_fr.pok_lt)
async def opl_yk_fr_cwt(msg: Message, state: FSMContext):        
    await state.update_data(pok_lt=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи показания счетчика холодной воды.')
    await state.set_state(Opl_yk_fr.pok_cwt)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_yk_fr.pok_cwt)
async def opl_yk_fr_hwt(msg: Message, state: FSMContext):        
    await state.update_data(pok_cwt=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи показания счетчика горячей воды.')
    await state.set_state(Opl_yk_fr.pok_hwt)    
    
@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_yk_fr.pok_hwt)
async def opl_yk_fr_preparetion(msg: Message, state: FSMContext):        
    await state.update_data(pok_hwt=msg.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'ykf' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        summ = str(data[0][4])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    data_pokaz = await state.get_data()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_yk_fr(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok_lt=data_pokaz.get('pok_lt'), pok_cwt=data_pokaz.get('pok_cwt'), pok_hwt=data_pokaz.get('pok_hwt'), summ=summ)
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_fr.format(input_value[2], input_value[3], input_value[4], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_yk_fr.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_yk_fr.preparation)
async def opl_yk_fr(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_yk_fr_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        data_pokaz = await state.get_data()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            pokaz_lt = data_pokaz.get('pok_lt')
            pokaz_cwt = data_pokaz.get('pok_cwt')
            pokaz_hwt = data_pokaz.get('pok_hwt')
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'fr', 'ykf', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                new_pokaz_lt = (pokaz_lt, 'fr', 'lt')
                request_to_update_pokaz_lt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND kp = %s"
                cursor.execute(request_to_update_pokaz_lt, new_pokaz_lt)

                new_pokaz_cwt = (pokaz_cwt, 'fr', 'cwt')
                request_to_update_pokaz_cwt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND tip_wt = %s"
                cursor.execute(request_to_update_pokaz_cwt, new_pokaz_cwt)

                new_pokaz_hwt = (pokaz_hwt, 'fr', 'hwt')
                request_to_update_pokaz_hwt = "UPDATE pokazania SET pokaz = %s WHERE kf = %s AND tip_wt = %s"
                cursor.execute(request_to_update_pokaz_hwt, new_pokaz_hwt) 
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_fr())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_fr())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_yk_fr.preparation)
async def opl_yk_fr(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_yk_fr.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_yk_fr.summ)
async def opl_yk_fr(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, yk, schet, bik, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'ykf' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_yk_fr(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok_lt=data_summ.get('pok_lt'), pok_cwt=data_summ.get('pok_cwt'), pok_hwt=data_summ.get('pok_hwt'), summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_fr.format(input_value[2], input_value[3], input_value[4], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_yk_fr.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())
        await state.clear()

# Оплата теплоэнерго Инструментальная
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wmin')
async def opl_wm_in_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, warm, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wm' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        summ = str(data[0][2])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wm(inn=inn, l_sch=l_sch, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wm_in.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_wm_in.preparation)
async def opl_wm_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_wm_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'wm', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_wm_in.preparation)
async def opl_wm_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_wm_in.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_wm_in.summ)
async def opl_wm_in(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, warm, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wm' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wm(inn=inn, l_sch=l_sch, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wm_in.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

### Оплата Водоснабжение Дом
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wtdm')
async def opl_wt_dm_pok(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Укажи показания счетчика воды.')
    await state.set_state(Opl_wt_dm.pok_wt)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_wt_dm.pok_wt)
async def opl_wt_dm_preparetion(msg: Message, state: FSMContext):        
    await state.update_data(pok_wt=msg.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    data_pokaz = await state.get_data()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=data_pokaz.get('pok_wt'), summ=summ)
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_wt.format('0', input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_wt_dm.preparation)
async def opl_wt_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_wt_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        data_pokaz = await state.get_data()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = data_pokaz.get('pok_wt')
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'wt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_wt_dm.preparation)
async def opl_wt_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_wt_dm.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_wt_dm.summ)
async def opl_wt_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=data_summ.get('pok_wt'), summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_wt.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

# Оплата Водоснабжения Петровская
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wtpt')
async def opl_wt_pt_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=pok, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_pt.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_wt_pt.preparation)
async def opl_wt_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_wt_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'pt', 'wt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_wt_pt.preparation)
async def opl_wt_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_wt_pt.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_wt_pt.summ)
async def opl_wt_pt(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=pok, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_pt.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())

# Оплата Водоснабжения Инструментальная
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'wtin')
async def opl_wt_in_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=pok, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_in.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_wt_in.preparation)
async def opl_wt_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_wt_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'in', 'wt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_in())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_wt_in.preparation)
async def opl_wt_in(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_wt_in.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_wt_in.summ)
async def opl_wt_in(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, water, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'in' AND postavshiki.kp = 'wt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_wt(inn=inn, l_sch=l_sch, pok=pok, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_in.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_in())

### Оплата Электроснабжение Дом
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ltdm')
async def opl_lt_dm_pok(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Укажи показания счетчика электроэнергии.')
    await state.set_state(Opl_lt_dm.pok_lt)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_lt_dm.pok_lt)
async def opl_lt_dm_preparetion(msg: Message, state: FSMContext):        
    await state.update_data(pok_lt=msg.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, light, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'lt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    data_pokaz = await state.get_data()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_lt(inn=inn, l_sch=l_sch, pok=data_pokaz.get('pok_lt'), summ=summ)
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_lt.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_lt_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_lt_dm.preparation)
async def opl_lt_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_lt_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        data_pokaz = await state.get_data()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = data_pokaz.get('pok_lt')
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'lt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_lt_dm.preparation)
async def opl_lt_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_lt_dm.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_lt_dm.summ)
async def opl_lt_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, light, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'lt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_lt(inn=inn, l_sch=l_sch, pok=data_summ.get('pok_lt'), summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_lt.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_lt_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

### Оплата Электроснабжение Петровская
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'ltpt')
async def opl_lt_pt_pok(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Укажи показания счетчика электроэнергии.')
    await state.set_state(Opl_lt_pt.pok_lt)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_lt_pt.pok_lt)
async def opl_lt_pt_preparetion(msg: Message, state: FSMContext):        
    await state.update_data(pok_lt=msg.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, light, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'lt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        pok = data[0][2]
        summ = str(data[0][3])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    data_pokaz = await state.get_data()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_lt(inn=inn, l_sch=l_sch, pok=data_pokaz.get('pok_lt'), summ=summ)
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_lt.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_lt_pt.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_lt_pt.preparation)
async def opl_lt_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_lt_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        data_pokaz = await state.get_data()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = data_pokaz.get('pok_lt')
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'pt', 'lt', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_lt_pt.preparation)
async def opl_lt_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_lt_pt.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_lt_pt.summ)
async def opl_lt_pt(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, light, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'lt' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_lt(inn=inn, l_sch=l_sch, pok=data_summ.get('pok_lt'), summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_lt.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_lt_pt.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())
        await state.clear()

### Оплата Газоснабжения Дом
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gzdm')
async def opl_gz_dm_pok(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Укажи показания счетчика газа.')
    await state.set_state(Opl_gz_dm.pok_gz)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gz_dm.pok_gz)
async def opl_gz_dm_preparetion(msg: Message, state: FSMContext):        
    await state.update_data(pok_gz=msg.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, gaz, schet, bik, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gz' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        pok = data[0][4]
        summ = str(data[0][5])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    data_pokaz = await state.get_data()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gz(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok=data_pokaz.get('pok_gz'), summ=summ)
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_gz.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gz_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_gz_dm.preparation)
async def opl_gz_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_gz_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        data_pokaz = await state.get_data()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = data_pokaz.get('pok_gz')
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'dm', 'gz', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_dm())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_gz_dm.preparation)
async def opl_gz_dm(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_gz_dm.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gz_dm.summ)
async def opl_gz_dm(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, gaz, schet, bik FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gz' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gz(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok=data_summ.get('pok_gz'), summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_gz.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gz_dm.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_dm())
        await state.clear()

### Оплата Газоснабжения Петровская
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gzpt')
async def opl_gz_pt_pok(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Укажи показания счетчика газа.')
    await state.set_state(Opl_gz_pt.pok_gz)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gz_pt.pok_gz)
async def opl_gz_pt_preparetion(msg: Message, state: FSMContext):        
    await state.update_data(pok_gz=msg.text)
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, gaz, schet, bik, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'pt' AND postavshiki.kp = 'gz' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        pok = data[0][4]
        summ = str(data[0][5])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    data_pokaz = await state.get_data()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gz(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok=data_pokaz.get('pok_gz'), summ=summ)
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_gz.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gz_pt.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_gz_pt.preparation)
async def opl_gz_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_gz_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        data_pokaz = await state.get_data()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = data_pokaz.get('pok_gz')
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'pt', 'gz', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)

                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_pt())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_gz_pt.preparation)
async def opl_gz_pt(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_gz_pt.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gz_pt.summ)
async def opl_gz_pt(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, gaz, schet, bik FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'dm' AND postavshiki.kp = 'gz' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gz(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok=data_summ.get('pok_gz'), summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay_gz.format(input_value[2], input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_wt_pt.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_pt())
        await state.clear()

# Оплата Газоснабжения Фрунзе
@router_jkh.callback_query(F.from_user.id == settings.tg_user_id, F.data == 'gzfr')
async def opl_gz_fr_preparetion(call: CallbackQuery, state: FSMContext):
    await state.clear()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, gaz, schet, bik, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'gz' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        pok = data[0][4]
        summ = str(data[0][5])
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await call.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gz(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok=pok, summ=summ)
    if input_value[0] is True:
        await call.message.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gz_fr.preparation)
    else:
        await call.message.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Да', Opl_gz_fr.preparation)
async def opl_gz_fr(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    if driver_jkh.oplata_gz_yes():    
        rekviz = utils_jkh.get_info_from_chek()
        if rekviz:
            num = rekviz[0]
            date = rekviz[1]
            usl = rekviz[2]
            card = rekviz[3]
            summ = rekviz[4]
            pokaz = rekviz[5]
            chek = f'<b>************Чек по операции************</b>\n' \
                   f'<b>Дата и время платежа</b>\n' \
                   f'{date:>45}\n' \
                   f'<b>Идентификатор платежа</b>\n' \
                   f'{num:>45}\n' \
                   f'<b>Вид услуги</b>\n' \
                   f'{usl:>45}\n' \
                   f'<b>Показания счетчика</b>\n' \
                   f'{pokaz:>45}\n' \
                   f'<b>Способ оплаты</b>\n' \
                   f'{card:>45} \n' \
                   f'<b>Сумма платежа</b>\n' \
                   f'{summ:>45} руб.'
            date_time_sql = utils_jkh.form_date(date)
            summ_sq = str(summ).replace(',', '.')
            summ_sql = str(summ_sq).replace(' ', '')
            connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
            cursor = connection.cursor()
            try:
                new_pay = (num, date_time_sql, usl, card, summ_sql, 'fr', 'gz', pokaz)
                request_to_insert_data = ''' INSERT INTO pay (num, date, usl, card, summ, kf, kp, pokaz) VALUES (%s, %s, %s, %s, %s, %s, %s, %s); '''
                cursor.execute(request_to_insert_data, new_pay)
                connection.commit()
                print('Данные введены')
            except Exception as e:
                # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
                connection.rollback()
                print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")
            finally:
                # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
                cursor.close()
                connection.close()
            await msg.answer(chek, reply_markup=kb_jkh.opl_zkh_fr())
            await state.clear()
        else:
            print('Данные из чека не извлечены')
            await msg.answer(text_jkh.falling_chek, reply_markup=kb_jkh.opl_zkh_fr())
            await state.clear()    
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())
        await state.clear()

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text == 'Нет', Opl_gz_fr.preparation)
async def opl_gz_fr(msg: Message, state: FSMContext):        
    await state.update_data(preparetion=msg.text)
    async with ChatActionSender.typing(bot=b, chat_id=msg.chat.id):
        # Приостанавливается выполнение асинхронной функции на 2 секунды (как будто бот печатает сообщение)
        await asyncio.sleep(2)
        await msg.answer('Укажи сумму, которую собираешься оплатить.')
    await state.set_state(Opl_gz_fr.summ)

@router_jkh.message(F.from_user.id == settings.tg_user_id, F.text, Opl_gz_fr.summ)
async def opl_gz_fr(msg: Message, state: FSMContext):        
    await state.update_data(summ=msg.text)
    data_summ = await state.get_data()
    connection = con.connect(
              host=settings.con_sql[0],
              user=settings.con_sql[1],
              password=settings.con_sql[2],
              database=settings.con_sql[3]
            )
    cursor = connection.cursor()
    try:
        select = ''' SELECT inn, gaz, schet, bik, pokaz, price FROM flat_ls JOIN pokazania 
        ON flat_ls.kf = pokazania.kf JOIN postavshiki ON pokazania.kp = postavshiki.kp 
        WHERE flat_ls.kf = 'fr' AND postavshiki.kp = 'gz' '''
        cursor.execute(select)
        data = cursor.fetchall()
        inn = data[0][0]
        l_sch = data[0][1]
        schet = data[0][2]
        bik = data[0][3]
        pok = data[0][4]
        connection.commit()
        print('Данные получены')
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()
    await msg.answer(text_jkh.preparation_pay)
    input_value = driver_jkh.oplata_gz(inn=inn, l_sch=l_sch, schet=schet, bik=bik, pok=pok, summ=data_summ.get('summ'))
    if input_value[0] is True:
        await msg.answer(text_jkh.question_pay.format(input_value[1]), reply_markup=kb_jkh.yes_no_kb)
        await state.set_state(Opl_gz_fr.preparation)
    else:
        await msg.answer(text_jkh.falling_pay, reply_markup=kb_jkh.opl_zkh_fr())
