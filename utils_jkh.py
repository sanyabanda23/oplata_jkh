from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display
import time
import PyPDF2
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import mysql.connector as con

import config_jkh


# Инициализирует и возвращает экземпляр Chrome WebDriver.
def initialize_driver(headless: bool = False) -> Optional[webdriver.Chrome]:
    """
    Инициализирует и возвращает экземпляр Chrome WebDriver.

    Args:
        headless (bool): Запускать ли браузер в headless-режиме (без GUI).

    Returns:
        Optional[webdriver.Chrome]: Экземпляр WebDriver или None в случае ошибки.
    """
    try:
        # Запустить Xvfb, запускает виртуальный дисплей необходимый в ВМ
        display = Display(visible=0, size=(1920, 1080))  
        display.start()
        #
        options = Options()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu') 
            options.add_argument('--window-size=1920x1080')# Часто необходимо для headless

        # Используем webdriver-manager для автоматической загрузки и управления драйвером
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(5) # Неявное ожидание элементов
        print("WebDriver успешно инициализирован.")
        return driver
    except Exception as e:
        print(f"Ошибка инициализации WebDriver: {e}")
        return None

# Открывает указанный URL в браузере.    
def open_website(driver: webdriver.Chrome, url: str) -> bool:
    """
    Открывает указанный URL в браузере.

    Args:
        driver (webdriver.Chrome): Экземпляр WebDriver.
        url (str): URL сайта для открытия.

    Returns:
        bool: True, если сайт успешно открыт, иначе False.
    """
    try:
        driver.get(url)
        print(f"Сайт {url} успешно открыт.")
        return True
    except Exception as e:
        print(f"Ошибка при открытии сайта {url}: {e}")
        return False

# Открывает указанный URL в браузере в новой вкладке.
def open_tab(driver: webdriver.Chrome, url: str, name: str) -> bool:
    try:
        driver.execute_script(f"window.open('{url}', '{name}');")
        driver.switch_to.window(name)
        print(f"Вкладка {url} успешно открыт.")
        return True
    except Exception as e:
        print(f"Ошибка при открытии вкладки {url}: {e}")
        return False
     
# Находит элемент на странице по заданному локатору.
def find_element(driver: webdriver.Chrome, by: By, value: str) -> Optional[WebElement]:
    """
    Находит элемент на странице по заданному локатору.

    Args:
        driver (webdriver.Chrome): Экземпляр WebDriver.
        by (By): Стратегия поиска (By.ID, By.NAME, etc.).
        value (str): Значение локатора.

    Returns:
        Optional[WebElement]: Найденный веб-элемент или None.
    """
    try:
        element = driver.find_element(by, value)
        print = ('Элемент найден')
        return element
    except Exception as e:
        print(f"Ошибка при поиске элемента {by}={value}: {e}")
        return None

# Вводит текст в указанный веб-элемент.
def input_text(element: Optional[WebElement], text: str) -> bool:
    """
    Вводит текст в указанный веб-элемент.

    Args:
        element (Optional[WebElement]): Веб-элемент (поле ввода).
        text (str): Текст для ввода.

    Returns:
        bool: True, если ввод успешен, иначе False.
    """
    if element:
        try:
            element.clear() # Очищаем поле перед вводом
            element.send_keys(text)
            print(f"Текст '{text[:5]}...' успешно введен.")
            return True
        except Exception as e:
            print(f"Ошибка ввода текста: {e}")
            return False
    return False

# Выполняет клик по указанному веб-элементу.
def click_element(element: Optional[WebElement]) -> bool:
    """
    Выполняет клик по указанному веб-элементу.

    Args:
        element (Optional[WebElement]): Веб-элемент для клика.

    Returns:
        bool: True, если клик успешен, иначе False.
    """
    if element:
        try:
            element.click()
            print("Элемент успешно кликнут.")
            return True
        except Exception as e:
            print(f"Ошибка клика по элементу: {e}")
            return False
    return False

# Проверяет успешность входа ожиданием появления элемента-индикатора.
def check_login_success(driver: webdriver.Chrome, success_indicator_locator: tuple[By, str], timeout: int = 10) -> bool:
    """
    Проверяет успешность входа ожиданием появления элемента-индикатора.

    Args:
        driver (webdriver.Chrome): Экземпляр WebDriver.
        success_indicator_locator (tuple[By, str]): Кортеж (локатор, значение) для элемента, 
                                                    подтверждающего успешный вход.
        timeout (int): Максимальное время ожидания элемента (в секундах).

    Returns:
        bool: True, если вход успешен (элемент найден), иначе False.
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(success_indicator_locator)
        )
        print("Вход успешно выполнен (индикатор найден).")
        return True
    except Exception as e:
        print(f"Ошибка проверки входа или вход не выполнен: {e}")
        return False

# Выполлняет прокрутку до элемента и click, используя JavaScript
def click_element_with_js(driver: webdriver.Chrome, by: By, value: str) -> None:
    """Clicks on an element using JavaScript.

    Args:
        driver: The Selenium WebDriver instance.
        element_locator: A tuple containing the By strategy and the locator value.
    """
    element = driver.find_element(by, value)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

# Изменение размера экрана и click 
def resize_window_and_click(driver: webdriver.Chrome, width: int, height: int, element_locator: tuple[By, str]) -> None:
    """Resizes the browser window and then clicks on an element.

    Args:
        driver: The Selenium WebDriver instance.
        width: The desired width of the window.
        height: The desired height of the window.
        element_locator: A tuple containing the By strategy and the locator value.
    """
    driver.set_window_size(width, height)
    element = driver.find_element(*element_locator)
    element.click()

# Ожидание и click
def wait_and_click(driver: webdriver.Chrome, element_locator: tuple[By, str], timeout: int = 10) -> None:
    """Waits for an element to be clickable and then clicks on it.

    Args:
        driver: The Selenium WebDriver instance.
        element_locator: A tuple containing the By strategy and the locator value.
        timeout: The maximum time to wait for the element to be clickable (in seconds).
    """
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(element_locator)
    )
    element.click()

# Вход в СБОЛ
def vhod_tel_parol(driver: webdriver.Chrome):
    button_vhod_tel_parol = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div/div[1]/div[2]/button[2]')
    if click_element(button_vhod_tel_parol):
        success_locator = (By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[1]/div/input') 
        is_logged_in = check_login_success(driver, success_locator)
        if is_logged_in:
            print("Перешел на страницу")
            login_input = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[1]/div/input')
            if login_input:
                for i in config_jkh.login_telefon:
                    login_input.send_keys(i)
            pasword_input = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[2]/div/input')
            if pasword_input:
                input_text(pasword_input, config_jkh.pasword_text)
            button_poluch_sms = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[4]/button')
            if click_element(button_poluch_sms):
                success_locator = (By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[1]') 
                is_logged_in = check_login_success(driver, success_locator)
                if is_logged_in:
                    print("Перешел на страницу")
                    time.sleep(10)
                    return True
    else:
        return False
def vhod_po_bank_card(driver: webdriver.Chrome):
    button_vhod_bank_card = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div/div[1]/div[1]/button[1]')
    if click_element(button_vhod_bank_card):
        success_locator = (By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[1]/div[1]/input') 
        is_logged_in = check_login_success(driver, success_locator)
        if is_logged_in:
            print("Перешел на страницу")
            login_input = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[1]/div[1]/input')                                                
            if login_input:
                for i in config_jkh.bank_card:
                    login_input.send_keys(i)
            button_poluch_sms = find_element(driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[2]/button')
            if click_element(button_poluch_sms):
                success_locator = (By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[1]') 
                is_logged_in = check_login_success(driver, success_locator)
                if is_logged_in:
                    print("Перешел на страницу")
                    time.sleep(10)
                    return True
    else:
        return False

def vhod_v_sbol(driver: webdriver.Chrome) -> bool:
        if  driver:
            open_website(driver, config_jkh.URL_vhod)
            if vhod_tel_parol(driver):
                print('Переход для получения СМС выполнен')
                return True
            else:
                print('Вход в Сбербанк Онлайн не  выполнен')
                return False

# формирование даты и времени в нужный вид для внесения в СУБД
def form_date(date: str) -> str:
    month = {'января':'01', 'февраля':'02', 'марта':'03', 'апреля':'04', 'мая':'05', 'июня':'06',
             'июля':'07', 'августа':'08', 'сентября':'09', 'октября':'10', 'ноября':'11', 'декабря':'12'}
    list_date = date.split(' ')
    for k, v in month.items():
        if list_date[1] in k:
            list_date[1] = v
    if len(list_date[0]) == 1:
        list_date[0].zfill(2)
    date_sql = '-'.join([list_date[2], list_date[1], list_date[0]])
    date_time_sql = date_sql + ' ' + list_date[3]
    return date_time_sql
# получение информации из чек об оплате в виде списка необходмых реквизитов
def get_info_from_chek() -> list:
    ### функция находит последний загруженный файл PDF в папке загрузки
    path = '/home/sanyabanda23/Downloads/'
    pdf = list(filter(lambda x: x.endswith('.pdf'), os.listdir(path))) # формирует список названий файлов PDF 
    files = [os.path.join(path, file) for file in pdf] # присваивает файлам PDF их путь
    last_file = max(files, key=os.path.getctime) # возвращает последдний созданный файл
    pdfReader = PyPDF2.PdfReader(open(last_file, 'rb'))    
    text = pdfReader.pages[0].extract_text().split('\n')
    for i in text:
        if 'Чек по операции ' in i:
            d = i.lstrip('Чек по операции ')
            date = d.rstrip(' мск')
        if '(СУИП)' in i:
            nom = i.lstrip('(СУИП)')
        if 'Услуга' in i:
            usl = i.lstrip('Услуга ')
        if 'Показания' in i:
            pok = i
        else:
            pok = 0
        if 'Способ оплаты ' in i:
            kar = i.lstrip('Способ оплаты ')
        if 'Сумма платежа ' in i:
            s = i.lstrip('Сумма платежа ')
            summ = s.rstrip(' ₽')
    rekviz = [nom, date, usl, kar, summ, pok]
    return rekviz

# формирование отчетов
def select_from_postav():
    try:
        connection = con.connect(
              host=config_jkh.con_sql[0],
              user=config_jkh.con_sql[1],
              password=config_jkh.con_sql[2],
              database=config_jkh.con_sql[3]
            )
        cursor = connection.cursor()
        # sql запрос
        select = ''' SELECT name, inn, schet, bik FROM pay_jkh.postavshiki; '''
        #метод объекта курсора, который выполняет SQL-запрос
        cursor.execute(select)
        # метод в Python, который извлекает все строки результата запроса и возвращает их в виде списка кортежей.
        data = cursor.fetchall()
        # метод commit сохраняет все изменения, внесённые в рамках транзакции, и делает их постоянными
        connection.commit()
        print('Данные выведены')
        # Приведенеие списка из БД в формат DataFrame, с указанием индексов столбцов в виде названий
        df = pd.DataFrame(data, columns=['Наиименование', 'ИНН', 'Счет организации', 'БИК'])
        # plt.subplots создаёт фигуру с подграфиками, размер которых — 12×4 дюйма
        fig, ax =plt.subplots(figsize=(12,4)) #fig — фигура с подграфиками. ax — индекс подграфиков, на который можно ссылаться для редактирования каждого из них.
        ax.axis('tight') # Настроить оси плотно вокруг точек данных 
        ax.axis('off') # отключает все визуальные компоненты осей (x- и y-осей) только для последнего подзаголовка
        the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center') # создаёт таблицу на основе данных из DataFrame

        #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
        pp = PdfPages("postavshiki.pdf") # создание объекта класса PdfPages
        pp.savefig(fig, bbox_inches='tight') # сохранить график в формате PDF с учётом параметра bbox_inches='tight', который убирает ненужные поля при сохранении графика
        pp.close()
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()

def select_from_lsch():
    try:
        connection = con.connect(
              host=config_jkh.con_sql[0],
              user=config_jkh.con_sql[1],
              password=config_jkh.con_sql[2],
              database=config_jkh.con_sql[3]
            )
        cursor = connection.cursor()
        # sql запрос
        select = ''' SELECT name, gaz, water, light, yk, garbage, kap_rem, warm FROM pay_jkh.flat_ls; '''
        #метод объекта курсора, который выполняет SQL-запрос
        cursor.execute(select)
        # метод в Python, который извлекает все строки результата запроса и возвращает их в виде списка кортежей.
        data = cursor.fetchall()
        # метод commit сохраняет все изменения, внесённые в рамках транзакции, и делает их постоянными
        connection.commit()
        print('Данные выведены')
        # Приведенеие списка из БД в формат DataFrame, с указанием индексов столбцов в виде названий
        df = pd.DataFrame(data, columns=['Наиименование', 'Газпром', 'Водоканал', 'ТНС Энерго', 'УК', 'Экотранс', 'ФКР', 'Теплоэнерго'])
        # plt.subplots создаёт фигуру с подграфиками, размер которых — 12×4 дюйма
        fig, ax =plt.subplots(figsize=(12,4)) #fig — фигура с подграфиками. ax — индекс подграфиков, на который можно ссылаться для редактирования каждого из них.
        ax.axis('tight') # Настроить оси плотно вокруг точек данных 
        ax.axis('off') # отключает все визуальные компоненты осей (x- и y-осей) только для последнего подзаголовка
        the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center') # создаёт таблицу на основе данных из DataFrame

        #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
        pp = PdfPages("l_sch.pdf") # создание объекта класса PdfPages
        pp.savefig(fig, bbox_inches='tight') # сохранить график в формате PDF с учётом параметра bbox_inches='tight', который убирает ненужные поля при сохранении графика
        pp.close()
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()

def select_from_pay_month(month):
    try:
        connection = con.connect(
              host=config_jkh.con_sql[0],
              user=config_jkh.con_sql[1],
              password=config_jkh.con_sql[2],
              database=config_jkh.con_sql[3]
            )
        cursor = connection.cursor()
        # sql запрос
        select = f''' SELECT name, num, date, usl, summ, pokaz FROM pay JOIN flat_ls ON flat_ls.kf = pay.kf
        WHERE MONTH(date)={month} '''
        #метод объекта курсора, который выполняет SQL-запрос
        cursor.execute(select)
        # метод в Python, который извлекает все строки результата запроса и возвращает их в виде списка кортежей.
        data_1 = cursor.fetchall()
        select = f''' SELECT SUM(summ) FROM pay
        WHERE MONTH(date)={month} '''
        #метод объекта курсора, который выполняет SQL-запрос
        cursor.execute(select)
        # метод в Python, который извлекает все строки результата запроса и возвращает их в виде списка кортежей.
        data_2 = cursor.fetchall()
        # метод commit сохраняет все изменения, внесённые в рамках транзакции, и делает их постоянными
        connection.commit()
        print('Данные выведены')
        # Приведенеие списка из БД в формат DataFrame, с указанием индексов столбцов в виде названий
        df = pd.DataFrame(data_1, columns=['Наименование', '№', 'Дата', 'Услуга', 'Сумма', 'Показания'])
        # plt.subplots создаёт фигуру с подграфиками, размер которых — 12×4 дюйма
        fig, ax =plt.subplots(figsize=(8,12)) #fig — фигура с подграфиками. ax — индекс подграфиков, на который можно ссылаться для редактирования каждого из них.
        ax.axis('tight') # Настроить оси плотно вокруг точек данных 
        ax.axis('off') # отключает все визуальные компоненты осей (x- и y-осей) только для последнего подзаголовка
        the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center') # создаёт таблицу на основе данных из DataFrame

        #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
        pp = PdfPages("month_pay.pdf") # создание объекта класса PdfPages
        pp.savefig(fig, bbox_inches='tight') # сохранить график в формате PDF с учётом параметра bbox_inches='tight', который убирает ненужные поля при сохранении графика
        pp.close()
        return data_2[0][0]
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()

def select_from_pay_year(kf, kp, year):
    try:
        connection = con.connect(
              host=config_jkh.con_sql[0],
              user=config_jkh.con_sql[1],
              password=config_jkh.con_sql[2],
              database=config_jkh.con_sql[3]
            )
        cursor = connection.cursor()
        # sql запрос
        select = f''' SELECT name, num, date, usl, summ, pokaz 
        FROM pay JOIN flat_ls ON flat_ls.kf = pay.kf
        WHERE YEAR(date)={year} AND pay.kf='{kf}' AND pay.kp='{kp}' '''
        #метод объекта курсора, который выполняет SQL-запрос
        cursor.execute(select)
        # метод в Python, который извлекает все строки результата запроса и возвращает их в виде списка кортежей.
        data = cursor.fetchall()
        # метод commit сохраняет все изменения, внесённые в рамках транзакции, и делает их постоянными
        connection.commit()
        print('Данные выведены')
        # Приведенеие списка из БД в формат DataFrame, с указанием индексов столбцов в виде названий
        df = pd.DataFrame(data, columns=['Наименование', '№', 'Дата', 'Услуга', 'Сумма', 'Показания'])
        # plt.subplots создаёт фигуру с подграфиками, размер которых — 12×4 дюйма
        fig, ax =plt.subplots(figsize=(8,12)) #fig — фигура с подграфиками. ax — индекс подграфиков, на который можно ссылаться для редактирования каждого из них.
        ax.axis('tight') # Настроить оси плотно вокруг точек данных 
        ax.axis('off') # отключает все визуальные компоненты осей (x- и y-осей) только для последнего подзаголовка
        the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center') # создаёт таблицу на основе данных из DataFrame

        #https://stackoverflow.com/questions/4042192/reduce-left-and-right-margins-in-matplotlib-plot
        pp = PdfPages("year_pay.pdf") # создание объекта класса PdfPages
        pp.savefig(fig, bbox_inches='tight') # сохранить график в формате PDF с учётом параметра bbox_inches='tight', который убирает ненужные поля при сохранении графика
        pp.close()
    except Exception as e:
        # метод rollback, который отменяет все изменения, внесённые в текущей транзакции, возвращая базу данных в предыдущее состояние.
        connection.rollback()
        print(f"Произошла ошибка: {str(e)} Транзакция откатывается.")

    finally:
        # Когда вы завершаете работу с курсором, например, после выполнения всех операций, важно закрыть как курсор, так и соединение
        cursor.close()
        connection.close()


# класс для выполения операций на СБОЛ 
class SBOL:
    def __init__(self):
        pass

    def initialize_driver(self, headless: bool = True) -> Optional[webdriver.Chrome]:
        """
        Инициализирует и возвращает экземпляр Chrome WebDriver.

        Args:
            headless (bool): Запускать ли браузер в headless-режиме (без GUI).

        Returns:
            Optional[webdriver.Chrome]: Экземпляр WebDriver или None в случае ошибки.
        """
        try:
            options = Options()
            if headless:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu') # Часто необходимо для headless
                options.add_experimental_option("detach", True)

            # Используем webdriver-manager для автоматической загрузки и управления драйвером
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(5) # Неявное ожидание элементов
            
            return "WebDriver успешно инициализирован."
        except Exception as e:
            return f"Ошибка инициализации WebDriver: {e}"
        
    def open_website(self, url: str) -> bool:
        """
        Открывает указанный URL в браузере.

        Args:
            driver (webdriver.Chrome): Экземпляр WebDriver.
            url (str): URL сайта для открытия.

        Returns:
            bool: True, если сайт успешно открыт, иначе False.
        """
        try:
            self.driver.get(url)
            print(f"Сайт {url} успешно открыт.")
            return True
        except Exception as e:
            print(f"Ошибка при открытии сайта {url}: {e}")
            return False

    def vhod_tel_parol(self) -> bool:
        button_vhod_tel_parol = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/div/div[1]/div[2]/button[2]')
        button_cookie = find_element(self.driver, By.XPATH, '//*[@id="app"]/div/div[1]/div/div[2]/button')
        click_element(button_cookie)
        if click_element(button_vhod_tel_parol):
            success_locator = (By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[1]/div/input') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Перешел на страницу")
                login_input = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[1]/div/input')
                if login_input:
                    for i in config_jkh.login_telefon:
                        login_input.send_keys(i)
                pasword_input = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[2]/div/input')
                if pasword_input:
                    input_text(pasword_input, config_jkh.pasword_text)
                button_poluch_sms = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/div[2]/form/div[4]/button')
                if click_element(button_poluch_sms):
                    success_locator = (By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[1]') 
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Перешел на страницу")
                        time.sleep(10)
                        return True
        else:
            self.driver.close()
            print('на кнопку не нажал')

    def close_driver(self):
        self.driver.close()

    def quit_driver(self):
        self.driver.quit()

    def vvod_is_sms(self, kod: str) -> bool:
        okno_1 = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[1]')
        okno_2 = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[2]')
        okno_3 = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[3]')
        okno_4 = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[4]')
        okno_5 = find_element(self.driver, By.XPATH, '//*[@id="layout-content"]/form/div[1]/div/div/input[5]')
        input_text(okno_1, kod[0])
        input_text(okno_2, kod[1])
        input_text(okno_3, kod[2])
        input_text(okno_4, kod[3])
        self.driver.save_screenshot("screenshot_tutorialspoint.png")
        if input_text(okno_5, kod[-1]):
            success_locator = (By.XPATH, '//*[@id="main"]/div/div/section[1]/div[3]/div[2]/div/div[2]/div/div/div/div[1]/a') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Вход в сбербанк онлайн выполнен")
                return True
            else:
                print("Не удалось перейти на страниицу")
                return False
        else:
            print("Не удалось перейти на страниицу")
            return False

########    
    def oplata_kr(self, inn: str, l_sch: str, summ: str):
        if 'oplata_kr' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_kr')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_kr')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_kr' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_kr')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_kr')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a') 
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a')
                        if click_element(button_next): # переход по ссылке
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по ссылке кап ремонта")
                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                if l_sch_input:
                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                    if click_element(button_next): # кнопка далее
                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input') 
                                        is_logged_in = check_login_success(self.driver, success_locator)
                                        if is_logged_in:
                                            print("Ввел лицевой счет")
                                            summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input')
                                            if summ_input:
                                                input_text(summ_input, f'0{summ}')
                                                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                if click_element(button_next): # кнопка далее
                                                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button') 
                                                    is_logged_in = check_login_success(self.driver, success_locator)
                                                    if is_logged_in:
                                                        print("Ввел сумму оплаты")
                                                        input_element = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                                        input_value = input_element.get_attribute("value")
                                                        return [True, input_value]
                                                else:
                                                    print("Сумма не введена")
                                                    return [False]
                                    else:
                                        print("Не ввел лицевой счет")
                                        return [False]
                        else:
                            print("Не перешел по ссылке")
                            return [False]
                    else:
                        print("Не нашел ИНН")
                        return [False]
            else:
                print('Не клинул элемент')
                return [False]
            
    def oplata_kr_yes(self):
        self.driver.switch_to.window('oplata_kr')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/button')
        click_element(button_vibor_scheta) # выбрал счет
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
        if click_element(button_next): # кнопка далее
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    return True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False

##########
    def oplata_gb(self, inn: str, l_sch: str, summ: str):
        if 'oplata_gb' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_gb')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_gb')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_gb' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_gb')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_gb')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div/div[2]/div/div')
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div/div[2]/div/div')
                        if click_element(button_next): # переход по ссылке
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по ссылке Вывоз ТКО")
                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                if l_sch_input:
                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                    if click_element(button_next): # кнопка далее
                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input') 
                                        is_logged_in = check_login_success(self.driver, success_locator)
                                        if is_logged_in:
                                            print("Ввел лицевой счет")
                                            summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input')
                                            if summ_input:
                                                input_text(summ_input, f'0{summ}')
                                                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div[1]/button')
                                                if click_element(button_next): # кнопка далее
                                                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div[1]/button') 
                                                    is_logged_in = check_login_success(self.driver, success_locator) 
                                                    if is_logged_in:
                                                        print("Ввел сумму оплаты")
                                                        input_element = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div/input')
                                                        input_value = input_element.get_attribute("value")
                                                        return [True, input_value]
                                                else:
                                                    print("Сумма не введена")
                                                    return [False]
                                    else:
                                        print("Не ввел лицевой счет")
                                        return [False]
                        else:
                            print("Не перешел по ссылке")
                            return [False]
                    else:
                        print("Не нашел ИНН")
                        return [False]
            else:
                print('Не клинул элемент')
                return [False]

    def oplata_gb_yes(self):
        self.driver.switch_to.window('oplata_gb')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/button')
        click_element(button_vibor_scheta) # выбрал счет  
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div[1]/button')
        if click_element(button_next): # кнопка далее 
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False                  

########
    def oplata_yk_dm(self, inn: str, l_sch: str, schet: str, bik: str, summ: str):
        if 'oplata_yk' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_yk')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_yk')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_yk' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_yk')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_yk')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[1]/button')
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_find_schet_bik = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[1]/button')
                        if click_element(button_find_schet_bik): # переход поиск по счету и бик
                            success_locator = (By.XPATH, '//*[@id="text-field-3"]')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по для поиска по счету и бик")
                                schet_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-3"]')
                                input_text(schet_input, schet) # ввел номер счета
                                bik_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-4"]')
                                input_text(bik_input, bik) # ввел бик
                                button_next_vibor_uk = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
                                if click_element(button_next_vibor_uk): # переход выбор ук
                                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                                    is_logged_in = check_login_success(self.driver, success_locator)
                                    if is_logged_in:
                                        button_uk = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                                        if click_element(button_uk): # переход по ссылке
                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                            is_logged_in = check_login_success(self.driver, success_locator)
                                            if is_logged_in:
                                                print("Перешел по ссылке Вывоз ТКО")
                                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                                if l_sch_input:
                                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                                    if click_element(button_next): # кнопка далее     
                                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input') 
                                                        is_logged_in = check_login_success(self.driver, success_locator)
                                                        if is_logged_in:
                                                            print("Ввел лицевой счет")
                                                            summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input')
                                                            if summ_input:
                                                                input_text(summ_input, f'0{summ}')
                                                                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                                if click_element(button_next): # кнопка далее
                                                                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
                                                                    is_logged_in = check_login_success(self.driver, success_locator)
                                                                    if is_logged_in:
                                                                        print("Ввел сумму оплаты")
                                                                        input_element = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                                                        input_value = input_element.get_attribute("value")
                                                                        return [True, input_value]
                                                                    else:
                                                                        print("Сумма не введена")
                                                                        return [False]
                                                        else:
                                                            print("Не ввел лицевой счет")
                                                            return [False]
                                        else:
                                            print("Не перешел по ссылке")
                                            return [False]
                            else:
                                print('Не перешел по для поиска по счету и бик')
                                [False]
                    else:
                        print("Не нашел ИНН")
                        return [False]
            else:
                print('Не клинул элемент')
                return [False]

    def oplata_yk_dm_yes(self):
        self.driver.switch_to.window('oplata_yk')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/button')
        click_element(button_vibor_scheta) # выбрал счет
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир      
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
        if click_element(button_next): # кнопка далее
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False

########
    def oplata_yk_in(self, l_sch: str, summ: str):
        if 'oplata_yk' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_yk')
            open_website(config_jkh.URL_payments_yki)
        else: 
            open_tab(self.driver, config_jkh.URL_payments_yki, 'oplata_yk')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
        else:
            if 'oplata_yk' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_yk')
                open_website(config_jkh.URL_payments_yki_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_yki_2, 'oplata_yk')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
        if l_sch_input:
            input_text(l_sch_input, l_sch) # ввод лицевого счета
            button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
            if click_element(button_next): # кнопка далее   
                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div/input') 
                is_logged_in = check_login_success(self.driver, success_locator) 
                if is_logged_in:
                    print("Ввел лицевой счет")
                    summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div/input')
                    if summ_input:
                        input_text(summ_input, f'0{summ}')
                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                        if click_element(button_next): # кнопка далее
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Ввел сумму оплаты")
                                input_element = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                input_value = input_element.get_attribute("value")
                                return [True, input_value]
                            else:
                                print("Сумма не введена")
                                return [False]
                else:
                    print("Лицевой счет не введен")
                    return [False]

    def oplata_yk_in_yes(self):
        self.driver.switch_to.window('oplata_yk')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/button')
        click_element(button_vibor_scheta) # выбрал счет
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
        if click_element(button_next): # кнопка далее
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False
        
########
    def oplata_yk_fr(self, inn: str, l_sch: str, schet: str, bik: str, pok_lt: str, pok_cwt: str, pok_hwt: str, summ: str):
        if 'oplata_yk' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_yk')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_yk')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_yk' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_yk')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_yk')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[1]/button')
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_find_schet_bik = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[1]/button')
                        if click_element(button_find_schet_bik): # переход поиск по счету и бик
                            success_locator = (By.XPATH, '//*[@id="text-field-3"]')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по для поиска по счету и бик")
                                schet_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-3"]')
                                input_text(schet_input, schet) # ввел номер счета
                                bik_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-4"]')
                                input_text(bik_input, bik) # ввел бик
                                button_next_vibor_uk = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
                                if click_element(button_next_vibor_uk): # переход выбор ук
                                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                                    is_logged_in = check_login_success(self.driver, success_locator)
                                    if is_logged_in:
                                        button_uk = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                                        if click_element(button_uk): # переход по ссылке
                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                            is_logged_in = check_login_success(self.driver, success_locator)
                                            if is_logged_in:
                                                print("Перешел по ссылке Вывоз ТКО")
                                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                                if l_sch_input:
                                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                                    if click_element(button_next): # кнопка далее     
                                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/div/input') 
                                                        is_logged_in = check_login_success(self.driver, success_locator)
                                                        if is_logged_in:
                                                            print("Ввел лицевой счет")
                                                            summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/div/input')
                                                            pok_lt_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/input')
                                                            pok_cwt_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/input')
                                                            pok_hwt_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/input')
                                                            if pok_lt_input:
                                                                input_text(pok_lt_input, pok_lt)
                                                                input_text(pok_cwt_input, pok_cwt)
                                                                input_text(pok_hwt_input, pok_hwt)
                                                                input_value = summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', '')
                                                                if input_value.isdigit() is False:
                                                                    input_value = 0
                                                                else:
                                                                    input_value = float(summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', ''))
                                                                print(f'INPUT_VALUE = {input_value}')
                                                                print(f'Тип данных summ - {summ} - {type(summ)}')
                                                                if summ == '1.0':
                                                                    if input_value > 0:
                                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div[1]/button')
                                                                    else:
                                                                        input_text(summ_input, f'0{summ}')
                                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div[1]/button')
                                                                        print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ INPUT_VALUE')
                                                                else:
                                                                    input_text(summ_input, f'0{summ}')
                                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div[1]/button')
                                                                    print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ SUMM')
                                                                if click_element(button_next): # кнопка далее
                                                                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[15]/div/div[1]/button')
                                                                    is_logged_in = check_login_success(self.driver, success_locator)
                                                                    if is_logged_in:
                                                                        print("Ввел сумму оплаты")
                                                                        input_element_summ = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[12]/div/div/input')
                                                                        input_element_lt = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div/textarea')
                                                                        input_element_cwt = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div/textarea')
                                                                        input_element_hwt = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div/textarea')
                                                                        input_value_summ = input_element_summ.get_attribute("value")
                                                                        input_value_lt = input_element_lt.get_attribute("value")
                                                                        input_value_cwt = input_element_cwt.get_attribute("value")
                                                                        input_value_hwt = input_element_hwt.get_attribute("value")
                                                                        return [True, input_value_summ, input_value_lt, input_value_cwt, input_value_hwt]
                                                                    else:
                                                                        print("Сумма не введена")
                                                                        return [False]
                                                        else:
                                                            print("Не ввел лицевой счет")
                                                            return [False]
                                            else:
                                                print("Не перешел по ссылке")
                                                return [False]
                            else:
                                print('Не перешел по для поиска по счету и бик')
                    else:
                        print("Не нашел ИНН")
                        return [False]
                else:
                    print('Не клинул элемент')
                    return [False]
                
    def oplata_yk_fr_yes(self):
        self.driver.switch_to.window('oplata_yk')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[14]/div/button')
        click_element(button_vibor_scheta) # выбрал счет
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[15]/div/div[1]/button')
        if click_element(button_next): # кнопка далее
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False

########
    def oplata_wm(self, inn: str, l_sch: str, summ: str):
        if 'oplata_wm' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_wm')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_wm')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_wm' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_wm')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_wm')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                        if click_element(button_next): # переход по ссылке
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по ссылке Теплоэнерго")
                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                if l_sch_input:
                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                    if click_element(button_next): # кнопка далее
                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div/input') 
                                        is_logged_in = check_login_success(self.driver, success_locator)
                                        if is_logged_in:
                                            print("Ввел лицевой счет")
                                            summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div/input')
                                            input_value = summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', '')
                                            if input_value.isdigit() is False:
                                                input_value = 0
                                            else:
                                                input_value = float(summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', ''))
                                            print(f'INPUT_VALUE = {input_value}')
                                            print(f'Тип данных summ - {summ} - {type(summ)}')
                                            if summ == '1.0':
                                                if input_value > 0:
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                else:
                                                    input_text(summ_input, f'0{summ}')
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                    print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ INPUT_VALUE')
                                            else:
                                                input_text(summ_input, f'0{summ}')
                                                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ SUMM')
                                            if click_element(button_next): # кнопка далее
                                                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                                is_logged_in = check_login_success(self.driver, success_locator)
                                                if is_logged_in:
                                                    print("Ввел сумму оплаты")
                                                    input_element_summ = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                                    input_value_summ = input_element_summ.get_attribute("value")
                                                    return [True, input_value_summ]
                                                else:
                                                    print("Сумма не введена")
                                                    return [False]
                                        else:
                                            print('Не ввел лицевой счет')
                                            return [False]
                            else:
                                print("Не перешел по ссылкке Теплоэнерго")
                                return [False]
                    else:
                        print("Не ввел ИНН")
                        return [False]    

    def oplata_wm_yes(self):
        self.driver.switch_to.window('oplata_wm')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/button')
        click_element(button_vibor_scheta) # выбрал счет
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
        if click_element(button_next): # кнопка далее
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    return True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False

########    
    def oplata_wt(self, inn: str, l_sch: str, pok: str, summ: str):
        if 'oplata_wt' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_wt')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_wt')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_wt' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_wt')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_wt')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                        if click_element(button_next): # переход по ссылке
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по ссылке Водоканал")
                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                if l_sch_input:
                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                    if click_element(button_next): # кнопка далее
                                        print(f'Значение pok = {pok} {type(pok)}')
                                        if pok == 0:
                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input') 
                                            is_logged_in = check_login_success(self.driver, success_locator)
                                            if is_logged_in:
                                                print("Ввел лицевой счет")
                                                summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input')
                                                if summ_input:
                                                    input_text(summ_input, f'0{summ}')
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                    if click_element(button_next): # кнопка далее
                                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div/input') 
                                                        is_logged_in = check_login_success(self.driver, success_locator)
                                                        if is_logged_in:
                                                            print("Ввел сумму оплаты")
                                                            input_element = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div/input')
                                                            input_value = input_element.get_attribute("value")
                                                            return [True, input_value]
                                                        else:
                                                            print("Сумма не введена")
                                                            return [False]
                                            else:
                                                print("Не ввел лицевой счет")
                                                return [False]
                                        else:
                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div[1]/input') 
                                            is_logged_in = check_login_success(self.driver, success_locator)
                                            if is_logged_in:
                                                print("Ввел лицевой счет")
                                                summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div[1]/input')
                                                pok_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/input')
                                                input_text(pok_input, pok)
                                                input_value = float(summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', ''))
                                                print(f'INPUT_VALUE = {input_value}')
                                                print(f'Тип данных summ - {summ} - {type(summ)}')
                                                if summ == '1.0':
                                                    if input_value > 0:
                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button')
                                                    else:
                                                        input_text(summ_input, f'0{summ}')
                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button')
                                                        print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ INPUT_VALUE')
                                                else:
                                                    input_text(summ_input, f'0{summ}')
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button')
                                                    print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ SUMM')
                                                if click_element(button_next): # кнопка далее
                                                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div/input')
                                                    is_logged_in = check_login_success(self.driver, success_locator)
                                                    if is_logged_in:
                                                        print("Ввел сумму оплаты")
                                                        input_element_summ = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div/input')
                                                        input_element_pok = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div/input')
                                                        input_value_summ = input_element_summ.get_attribute("value")
                                                        input_value_pok = input_element_pok.get_attribute("value")
                                                        return [True, input_value_summ, input_value_pok]
                                                    else:
                                                            print("Сумма не введена")
                                                            return [False]
                                            else:
                                                print("Не ввел лицевой счет")
                                                return [False] 

                        else:
                            print("Не перешел по ссылке")
                            return [False]
                    else:
                        print("Не нашел ИНН")
                        return [False]
            else:
                print('Не клинул элемент')
                return [False]
            
    def oplata_wt_yes(self):
        self.driver.switch_to.window('oplata_wt')
        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/div[1]/button') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/button')
            click_element(button_vibor_scheta) # выбрал счет
            button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
            click_element(button_mir) # выбрал карты мир
            button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/div[1]/button')
            if click_element(button_next): # кнопка далее
                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
        else:
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[12]/div/div[1]/button') 
            is_logged_in = check_login_success(self.driver, success_locator) 
            if is_logged_in:
                button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/button')
                click_element(button_vibor_scheta) # выбрал счет
                button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
                click_element(button_mir) # выбрал карты мир 
                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[12]/div/div[1]/button')
                if click_element(button_next): # кнопка далее 
                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
            else:
                print('Кнопка далее не нажата')
                return False
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            print("Провел оплату")
            button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
            if click_element(button_save_chek):
                time.sleep(5)
                print('Чек сохранен')
                return True
            else:
                print("Чек не сохранен")
                return True
        else:
            print("Оплата не прошла")
            return False

########    
    def oplata_lt(self, inn: str, l_sch: str, pok: str, summ: str):
        if 'oplata_lt' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_lt')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_lt')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_lt' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_lt')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_lt')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[7]/a/div')
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[7]/a/div')
                        if click_element(button_next): # переход по ссылке 
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по ссылке ТНС Энерго")
                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[1]/div/div[1]/input')
                                if l_sch_input:
                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/button')
                                    if click_element(button_next): # кнопка далее
                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div/input') 
                                        is_logged_in = check_login_success(self.driver, success_locator)
                                        if is_logged_in:
                                            print("Ввел лицевой счет")
                                            summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div/input')
                                            pok_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/input')
                                            input_text(pok_input, pok)
                                            input_value = summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', '')
                                            if input_value.isdigit() is False:
                                                input_value = 0
                                            else:
                                                input_value = float(summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', ''))
                                            print(f'INPUT_VALUE = {input_value}')
                                            print(f'Тип данных summ - {summ} - {type(summ)}')
                                            if summ == '1.0':
                                                if input_value > 0:
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                else:
                                                    input_text(summ_input, f'0{summ}')
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                    print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ INPUT_VALUE')
                                            else:
                                                input_text(summ_input, f'0{summ}')
                                                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ SUMM')
                                            if click_element(button_next): # кнопка далее
                                                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div/input')
                                                is_logged_in = check_login_success(self.driver, success_locator)
                                                if is_logged_in:
                                                    print("Ввел сумму оплаты")
                                                    input_element_summ = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div/input')
                                                    input_element_pok = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[3]/div/div/input')
                                                    input_value_summ = input_element_summ.get_attribute("value")
                                                    input_value_pok = input_element_pok.get_attribute("value")
                                                    return [True, input_value_summ, input_value_pok]
                                                else:
                                                    print("Сумма не введена")
                                                    return [False]
                                        else:
                                            print("Не ввел лицевой счет")
                                            return [False]
                            else:
                                print("Не перешел по ссылке")
                                return [False]
                    else:
                        print("Не нашел ИНН")
                        return [False]

    def oplata_lt_yes(self):
        self.driver.switch_to.window('oplata_lt')
        button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/button')
        click_element(button_vibor_scheta) # выбрал счет
        button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
        click_element(button_mir) # выбрал карты мир
        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div[1]/button')
        if click_element(button_next): # кнопка далее
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                print("Провел оплату")
                button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
                if click_element(button_save_chek):
                    time.sleep(5)
                    print('Чек сохранен')
                    return True
                else:
                    print("Чек не сохранен")
                    return True
            else:
                print("Оплата не прошла")
                return False
        else:
            print('Кнопка далее не нажата')
            return False

########
    def oplata_gz(self, inn: str, l_sch: str, schet: str, bik: str, pok: str, summ: str):
        if 'oplata_gz' in self.driver.window_handles:
            self.driver.switch_to.window('oplata_gz')
            open_website(config_jkh.URL_payments)
        else: 
            open_tab(self.driver, config_jkh.URL_payments, 'oplata_gz')
        self.driver.set_window_size(1920, 1080)
        success_locator = (By.XPATH, '//*[@id="text-field-1"]')
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        else:
            if 'oplata_gz' in self.driver.window_handles:
                self.driver.switch_to.window('oplata_gz')
                open_website(config_jkh.URL_payments_2)
            else: 
                open_tab(self.driver, config_jkh.URL_payments_2, 'oplata_gz')
                self.driver.set_window_size(1920, 1080)
                success_locator = (By.XPATH, '//*[@id="text-field-1"]') 
                is_logged_in = check_login_success(self.driver, success_locator)
                if is_logged_in:
                    inn_input = find_element(self.driver, By.XPATH, '//*[@id="text-field-1"]')
        if inn_input:
            input_text(inn_input, inn) # ввод инн
            button_next = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
            if button_next:
                self.driver.save_screenshot("screenshot_tutorialspoint.png")
                if click_element(button_next): # кнопка далее
                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[1]/button') 
                    is_logged_in = check_login_success(self.driver, success_locator)
                    if is_logged_in:
                        print("Ввел инн")
                        button_find_schet_bik = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[1]/button')
                        if click_element(button_find_schet_bik): # переход поиск по счету и бик
                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/div/div/div[2]/ul/li[2]/div/div[2]/div[1]/div[1]/input') 
                            is_logged_in = check_login_success(self.driver, success_locator)
                            if is_logged_in:
                                print("Перешел по для поиска по счету и бик")
                                schet_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/div/div/div[2]/ul/li[2]/div/div[2]/div[1]/div[1]/input') 
                                input_text(schet_input, schet) # ввел номер счета
                                bik_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/div/div/div[2]/ul/li[2]/div/div[3]/div[1]/div[1]/input')
                                input_text(bik_input, bik) # ввел бик
                                button_next_vibor_uk = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/ul/li[4]/div/button')
                                if click_element(button_next_vibor_uk): # переход выбор ук
                                    success_locator = (By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                                    is_logged_in = check_login_success(self.driver, success_locator)
                                    if is_logged_in:
                                        button_uk = find_element(self.driver, By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/ul/li[2]/a/div')
                                        if click_element(button_uk): # переход по ссылке
                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/input')
                                            is_logged_in = check_login_success(self.driver, success_locator)
                                            if is_logged_in:
                                                print("Перешел по ссылке Газпром")
                                                l_sch_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[2]/div/div[1]/input')
                                                if l_sch_input:
                                                    input_text(l_sch_input, l_sch) # ввод лицевого счета
                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[3]/div/div[1]/button')
                                                    if click_element(button_next): # кнопка далее     
                                                        print(f'Значение pok = {pok} {type(pok)}')
                                                        if pok == 0:
                                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input') 
                                                            is_logged_in = check_login_success(self.driver, success_locator)
                                                            if is_logged_in:
                                                                print("Ввел лицевой счет")
                                                                summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[4]/div/div[1]/input')
                                                                if summ_input:
                                                                    input_text(summ_input, f'0{summ}')
                                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/button')
                                                                    if click_element(button_next): # кнопка далее
                                                                        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input') 
                                                                        is_logged_in = check_login_success(self.driver, success_locator)
                                                                        if is_logged_in:
                                                                            print("Ввел сумму оплаты")
                                                                            input_element = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                                                            input_value = input_element.get_attribute("value")
                                                                            return [True, input_value]
                                                                        else:
                                                                            print("Сумма не введена")
                                                                            return [False]
                                                            else:
                                                                print("Не ввел лицевой счет")
                                                                return [False]
                                                        else:
                                                            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button') 
                                                            is_logged_in = check_login_success(self.driver, success_locator)
                                                            if is_logged_in:
                                                                print("Ввел лицевой счет")
                                                                summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div[1]/input')
                                                                pok_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[5]/div/div[1]/input')
                                                                input_text(pok_input, pok)
                                                                input_value = summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', '')
                                                                if input_value.isdigit() is False:
                                                                    input_value = 0
                                                                else:
                                                                    input_value = float(summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', ''))
                                                                print(f'INPUT_VALUE = {input_value}')
                                                                print(f'Тип данных summ - {summ} - {type(summ)}')
                                                                if summ == '1.0':
                                                                    if input_value > 0:
                                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button')
                                                                    else:
                                                                        input_text(summ_input, f'0{summ}')
                                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button')
                                                                        print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ INPUT_VALUE')
                                                                else:
                                                                    input_text(summ_input, f'0{summ}')
                                                                    button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/button')
                                                                    print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ SUMM')
                                                            else:
                                                                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div[1]/button') 
                                                                is_logged_in = check_login_success(self.driver, success_locator)
                                                                if is_logged_in:
                                                                    print("Ввел лицевой счет")
                                                                    summ_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[7]/div/div[1]/input')
                                                                    pok_input = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div[1]/input')
                                                                    input_text(pok_input, pok)
                                                                    input_value = summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', '')
                                                                    if input_value.isdigit() is False:
                                                                        input_value = 0
                                                                    else:
                                                                        input_value = float(summ_input.get_attribute("value").rstrip(' ₽').replace(',', '.').replace(' ', ''))
                                                                    print(f'INPUT_VALUE = {input_value}')
                                                                    print(f'Тип данных summ - {summ} - {type(summ)}')
                                                                    if summ == '1.0':
                                                                        if input_value > 0:
                                                                            button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div[1]/button')
                                                                        else:
                                                                            input_text(summ_input, f'0{summ}')
                                                                            button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div[1]/button')
                                                                            print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ INPUT_VALUE')
                                                                    else:
                                                                        input_text(summ_input, f'0{summ}')
                                                                        button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div[1]/button')
                                                                        print('ВВОЖУ ПОСЛЕ ПРОВЕРКИ SUMM')
                                                                else:
                                                                    print("Не ввел лицевой счет")
                                                                    return [False]
                                                            if click_element(button_next): # кнопка далее
                                                                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/button')
                                                                is_logged_in = check_login_success(self.driver, success_locator)
                                                                if is_logged_in:
                                                                    print("Ввел сумму оплаты")
                                                                    input_element_summ = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/div/input')
                                                                    input_element_pok = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[6]/div/div/input')
                                                                    input_value_summ = input_element_summ.get_attribute("value")
                                                                    input_value_pok = input_element_pok.get_attribute("value")
                                                                    return [True, input_value_summ, input_value_pok]
                                                                else:
                                                                    print("Сумма не введена")
                                                                    return [False]
                                            else:
                                                print("Не перешел по ссылке")
                                                return [False]
                            else:
                                print("Не перешел по для поиска по счету и бик")
                                return [False]
                    else:
                        print("Не нашел ИНН")
                        return [False]
            else:
                print('Не клинул элемент')
                return [False]

    def oplata_gz_yes(self):
        self.driver.switch_to.window('oplata_gz')
        success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/button') 
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[10]/div/button')
            click_element(button_vibor_scheta) # выбрал счет
            button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                    
            click_element(button_mir) # выбрал карты мир
            button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[11]/div/div[1]/button')
            if click_element(button_next): # кнопка далее
                success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button') 
        else:
            success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/button') 
            is_logged_in = check_login_success(self.driver, success_locator)
            if is_logged_in:
                button_vibor_scheta = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[8]/div/button')
                click_element(button_vibor_scheta) # выбрал счет
                button_mir = find_element(self.driver, By.XPATH, '/html/body/div[6]/ul/li[1]/button')                                                     
                click_element(button_mir) # выбрал карты мир 
                button_next = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/section/div[9]/div/div[1]/button')
                if click_element(button_next): # кнопка далее 
                    success_locator = (By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
            else:
                print('Кнопка далее не нажата')
                return False
        is_logged_in = check_login_success(self.driver, success_locator)
        if is_logged_in:
            print("Провел оплату")
            button_save_chek = find_element(self.driver, By.XPATH, '/html/body/div[1]/div/main/div[5]/form/div[2]/div/div[2]/button')
            if click_element(button_save_chek):
                time.sleep(5)
                print('Чек сохранен')
                return True
            else:
                print("Чек не сохранен")
                return True
        else:
            print("Оплата не прошла")
            return False
