from sqlalchemy import create_engine, Table, Column, Integer, String, Text, DateTime, MetaData, delete, update
from telebot import TeleBot
from werkzeug.security import generate_password_hash


engine = create_engine('sqlite:///data.db?check_same_thread=False')
conn = engine.connect()
metadata = MetaData()

bot = TeleBot('2011837329:AAGml7u90VPIuBEzXYHMJ-fNNFEewfkjm68') # You can set parse_mode by default. HTML or MARKDOWN

users = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('username', String(80), unique=True),
    Column('password', String(120), unique=True),
    Column('started_at', DateTime())
    )


class Db:
    @staticmethod
    def get_user(id):
        s = users.select().where(users.c.id==id)
        return conn.execute(s).first()

    @staticmethod
    def check_user_exists(id):
        res = Db.get_user(id)
        return res is not None


@bot.message_handler(commands=['start'])
def start_message(message):
    if Db.check_user_exists(message.chat.id):
        s = delete(users).where(users.c.id == message.chat.id)
        conn.execute(s)
    s = users.insert().values(id=message.chat.id)
    conn.execute(s)
    bot.send_message(message.chat.id, 'Бот будет автоматически открывать ваш рабочий день утром, спрашивать у вас содержание ежедневного отчёта и закрывать рабочий день. День открывается в период 8:30-9:30 в случайным образом выбранное время, закрывается - после написания отчета, который бот предложит написать, но не раньше, чем через 7 часов 30 минут с момента начала рабочего времени. Бот предлагает написать отчет в промежутке 17:30-18:30.\n\nДля начала работы необходим ваш логин и пароль от системы Битрикс24. Не волнуйтесь: данные хранятся на защищённом сервере и нерасшифровываемы для автора бота.\n\nВведите ваш логин:')

@bot.message_handler()
def all(msg):
    s = users.select().where(users.c.id==msg.chat.id)
    user = conn.execute(s).first()
    if user[1] is None:
        s = users.update().where(users.c.id==msg.chat.id).values(username=msg.text)
        res = conn.execute(s)
        bot.send_message('Теперь ваш пароль:')
    elif user[2] is None:
            password = generate_password_hash(msg.text, 'sha256')
            s = users.update().where(users.c.id==msg.chat.id).values(password=password)
            res = conn.execute(s)
            bot.send_message('Отлично. Сканирую данные о рабочем дне...')


metadata.create_all(engine)
bot.infinity_polling()