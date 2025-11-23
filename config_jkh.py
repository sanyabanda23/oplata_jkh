import mysql.connector as con

# установка соединения с бд MYSQL
connection = con.connect(
      host='127.0.0.1',
      user='sanyabanda23',
      password='Mashenka1!',
      database='pay_jkh'
)

BOT_TOKEN = '8452662654:AAFwF6mapAm0wQY148pPFCpvMcJfqtE3K8A'
REDIS_URL = 'redis://127.0.0.1:6379/0'
tg_user_id = 5180149646

URL_payments = "https://web1.online.sberbank.ru/payments/detailspay"
URL_payments_2 = "https://si1.online.sberbank.ru/payments/detailspay"
URL_payments_yki = 'https://si2.online.sberbank.ru/payments/provider?psh=p&did=1760979417033000379&serviceId=1098838455848&pid=bb572305-b0e3-11f0-99bd-1d1e5ec9d69e'
URL_payments_yki_2 = 'https://web1.online.sberbank.ru/payments/provider?psh=p&did=1760979417033000379&serviceId=1098838455848&pid=28dde8ed-b0eb-11f0-933d-a32aa9affa12'
URL_vhod = "https://online.sberbank.ru/CSAFront/index.do"
login_telefon = "9515273806"
bank_card = '2202200226525598'
pasword_text = 'Mashenka2@'
