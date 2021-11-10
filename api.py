from requests import get, post
from bs4 import BeautifulSoup
import json
from config import *


class Bitrix24:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.cookies = {}
        self.sessid = ''
        self.auth()
    
    def get_sessid(self):
        r = get(BASE_HOST, cookies=self.cookies)
        soup = BeautifulSoup(r.text, 'html.parser')
        self.sessid = soup.find('input', {'name': 'sessid'}).get('value')

    def auth(self):
        r = get(BASE_HOST)
        if 'Новости' in r.text:
            return True
        form = {'AUTH_FORM': 'Y', 'TYPE': 'AUTH', 'USER_LOGIN': self.login, 'USER_PASSWORD': self.password}
        r = post(BASE_HOST + '/login', data=form)
        if 'Новости' in r.text:
            self.cookies = r.cookies
            self.get_sessid()
            return True
        return False

    def json(self, r):
        return json.loads(r.text.replace("'", '"'))

    def get_state(self):
        r = get(BASE_HOST + '/bitrix/tools/timeman.php', params={'action': 'update', 'site_id': 's1', 'sessid': self.sessid}, cookies=self.cookies)
        state = self.json(r)['STATE']
        meta = self.json(r)
        return state, meta
    
    def open(self):
        r = post(BASE_HOST + '/bitrix/tools/timeman.php', params={'action': 'open', 'site_id': 's1', 'sessid': self.sessid}, cookies=self.cookies)
        if r.status_code == 200:
            return True
        return False
    
    def close(self, report):
        r = post(BASE_HOST + '/bitrix/tools/timeman.php', params={'action': 'close', 'site_id': 's1', 'sessid': self.sessid}, data={'REPORT': report, 'ready': 'Y', 'device': 'browser'}, cookies=self.cookies)
        if r.status_code == 200:
            return True
        return False
