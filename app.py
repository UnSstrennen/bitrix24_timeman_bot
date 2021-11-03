from sqlalchemy import create_engine, Table, Column, Integer, String, Text, DateTime, MetaData, delete, Boolean
from telebot import TeleBot
from datetime import datetime as dt
from random import randint
from api import Bitrix24
from config import *


engine = create_engine('sqlite:///data.db?check_same_thread=False')
conn = engine.connect()
metadata = MetaData()

bot = TeleBot(TOKEN)

users = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('username', String(80), unique=True),
    Column('password', String(120), unique=True),
    Column('start', DateTime()),
    Column('stop', DateTime()),
    Column('report', Text()),
    Column('waiting_report', Boolean(), default=False),
    Column('report_required', Boolean())
    )


class Db:
    @staticmethod
    def get_all_users():
        s = users.select()
        return conn.execute(s).all()

    @staticmethod
    def get_user(id):
        s = users.select().where(users.c.id==id)
        return conn.execute(s).first()

    @staticmethod
    def check_user_exists(id):
        res = Db.get_user(id)
        return res is not None

    @staticmethod
    def add_user(id):
        s = users.insert().values(id=id)
        conn.execute(s)

    @staticmethod
    def delete_user(id):
        s = users.delete().where(users.c.id==id)
        return conn.execute(s)
    
    @staticmethod
    def waiting_report(id):
        s = users.update().where(users.c.id==id).values(waiting_report = True)
        conn.execute(s)

    @staticmethod
    def set_times(id, start, stop):
        user = Db.get_user(id)
        if user[3] is None:
            s = users.update().where(users.c.id==id).values(start=start, stop=stop)
            res = conn.execute(s)
            return start, stop
        return user[3], user[4]
    
    @staticmethod
    def set_report_requirement(id, req):
        s = users.update().where(users.c.id==id).values(report_required = req)
        conn.execute(s)
    
    @staticmethod
    def set_report(id, report):
        s = users.update().where(users.c.id==id).values(report = report, waiting_report = False)
        conn.execute(s)
    
    @staticmethod
    def clear_user(id):
        s = users.update().where(users.c.id==id).values(report=None, waiting_report=False, start=None, stop=None)
        conn.execute(s)


@bot.message_handler(commands=['start', 'restart'])
def start_message(message):
    if Db.check_user_exists(message.chat.id):
        Db.delete_user(message.chat.id)
    Db.add_user(message.chat.id)
    bot.send_message(message.chat.id, 'Бот будет автоматически открывать ваш рабочий день утром, спрашивать у вас содержание ежедневного отчёта и закрывать рабочий день. День открывается в период 9:00-10:30 в случайным образом выбранное время, закрывается - после написания отчета, который бот предложит написать, но не раньше, чем через 7 часов 30 минут с момента начала рабочего времени. Бот предлагает написать отчет в промежутке 17:30-18:30.\n\nДля начала работы необходим ваш логин и пароль от системы Битрикс24. Не волнуйтесь: данные хранятся на защищённом сервере и нерасшифровываемы для автора бота. Если вы хотите остановить работу бота - используйте команду /stop. Если что-то пошло не так - используйте /restart.\n\nВведите ваш логин:')


@bot.message_handler(commands=['stop'])
def start_message(message):
    if Db.check_user_exists(message.chat.id):
        Db.delete_user(message.chat.id)
    bot.send_message(message.chat.id, 'Бот больше не будет вести за вас Битрикс24 и беспокоить вас.\n\nДля повторного запуска бота - используйте команду /start')

def scan_user(user, id):
    additional = ''
    bot.send_message(id, 'Отлично. Сканирую данные о пользователе...')
    bitrix = Bitrix24(user[1], user[2])
    state, meta = bitrix.get_state()
    report_required = True if meta['REPORT_REQ'] == 'Y' else False
    Db.set_report_requirement(id, report_required)
    report_required = 'есть' if report_required else 'нет'
    if state == 'OPENED':
        timestamp = int(meta['INFO']['DATE_START'])
        datetime_start = dt.fromtimestamp(timestamp)
        datetime_stop = dt.fromtimestamp(timestamp + randint(DAY_MIN_LENGTH, DAY_MAX_LENGTH))
        start, stop = Db.set_times(id, datetime_start, datetime_stop)
        additional = f'\nРабочий день начат {start}\nСегодня день будет окончен не раньше {stop}'
    elif state == 'CLOSED':
        additional = '\nЗавтра будет новый день и бот начнёт свою работу.'
    else:
        additional = '\nС таким статусом бот не может продолжить работу. Продолжите рабочий день или запросите изменение рабочего дня, чтобы продолжить.'
    bot.send_message(id, f'Ваш рабочий день {RU_STATES[state]}.' + f'\nНеобходимость писать ежедневный отчёт: {report_required}' + additional)


@bot.message_handler()
def all(msg):
    s = users.select().where(users.c.id==msg.chat.id)
    user = conn.execute(s).first()
    if user[1] is None:
        s = users.update().where(users.c.id==msg.chat.id).values(username=msg.text)
        conn.execute(s)
        bot.send_message(msg.chat.id, 'Теперь ваш пароль:')
    elif user[2] is None:
        password = msg.text
        s = users.update().where(users.c.id==msg.chat.id).values(password=password)
        conn.execute(s)
        user = Db.get_user(msg.chat.id)
        scan_user(user, msg.chat.id)
    elif user[6]:
        Db.set_report(msg.chat.id, msg.text)
        bot.send_message(msg.chat.id, f'Отчёт сохранён. Рабочий день будет закрыт не раньше {user[4]}.')
    else:
        scan_user(user, msg.chat.id)


if __name__ == '__main__':
    metadata.create_all(engine)
    bot.infinity_polling()