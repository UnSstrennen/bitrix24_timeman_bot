from datetime import datetime as dt
from random import randint
from requests import get, post
from app import Db, bot
from api import Bitrix24
from config import *


def generate_times():
        now = dt.now()
        hour = randint(9,10)
        minute = randint(0, 59) if hour == 9 else randint(0, 30)
        start = dt(now.year, now.month, now.day, hour, minute, randint(0, 59))
        end = dt.fromtimestamp(start.timestamp() + randint(DAY_MIN_LENGTH, DAY_MAX_LENGTH))
        return start, end


if 8 <= dt.now().hour <= 12:
    users = Db.get_all_users()
    for user in users:
        if user[3] >= dt.now():
            bitrix = Bitrix24(user[1], user[2])
            state, meta = bitrix.get_state()
            if state == 'CLOSED':
                bitrix.open()
                bot.send_message(user[0], f'Ваш рабочий день открыт. Окончание рабочего дня запланировано на {user[4]} при условии своевременного написания отчёта.')
            else:
                bot.send_message(user[0], 'Ошибка: кажется, предыдущий рабочий день не закрыт или вы \
                    поставили рабочий день на паузу. Исправьте и бот снова заработает.')

elif 3 <= dt.now().hour <= 5:
    users = Db.get_all_users()
    for user in users:
        if user[3] is None and user[4] is None:
            start, stop = generate_times()
            Db.set_times(user[0], start, stop)

elif dt.now().hour >= 17:
    users = Db.get_all_users()
    for user in users:
        if user[5] is None and not user[6]:
            bot.send_message(user[0], 'Напишите отчёт о рабочем дне. Прям сюда! Рабочий день пока не будет закрыт.')
            Db.waiting_report(user[0])
        elif user[4] >= dt.now() and user[5] is not None:
            bitrix = Bitrix24(user[1], user[2])
            state, meta = bitrix.get_state()
            if state == 'OPENED':
                bitrix.close(user[5])
                Db.clear_user(user[0])
                bot.send_message(user[0], 'Ваш рабочий день был закрыт, отчёт - передан.')
            elif state in ['EXPIRED', 'PAUSED']:
                bot.send_message(user[0], 'Ошибка: кажется, предыдущий рабочий день не закрыт или вы \
                    поставили рабочий день на паузу. Исправьте и бот снова заработает.')