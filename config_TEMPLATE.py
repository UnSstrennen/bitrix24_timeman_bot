from os import environ as env


BASE_HOST = env.get('BASE_HOST', 'https://bitrix.keklol.ru/')

TOKEN = env.get('TOKEN', '')

DAY_MIN_LENGTH = int(env.get('DAY_MIN_LENGTH', 27000))
DAY_MAX_LENGTH = int(env.get('DAY_MAX_LENGTH', 32400))

RU_STATES = {'OPENED': 'открыт', 'EXPIRED': 'вы не закрыли предыдущий рабочий день', 'CLOSED': 'закрыт', 'PAUSED': 'приостановлен'}
