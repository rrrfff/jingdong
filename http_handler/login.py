import requests
import auth
import json
import log_ex as logger
import urllib


class Login:
    def __init__(self, name, pwd, uuid, user_agent):
        self.name = name
        self.pwd = pwd
        self.uuid = uuid
        self.user_agent = user_agent

    def get_cookie(self):
        logger.debug('get-cookie[get_req_data]:%s %s %s' % (self.name, self.pwd, self.uuid))
        url = 'http://wlogin.m.jd.com/applogin_v2'
        headers = {'User-Agent': 'Android WJLoginSDK 1.4.2'}
        data = auth.get_req_data(self.name, self.pwd, self.uuid)
        logger.debug('POST %s\n%s\n%s' % (url, data, json.dumps(headers)))
        resp = requests.post(url, data=data, headers=headers)
        resp_text = resp.text
        logger.debug('resp: %s' % (resp_text))

        try:
            cookie = auth.get_cookie(resp_text)
            return cookie
        except Exception, e:
            raise Exception('cookie parse error', e)

    def get_h5_cookie(self, cookie):
        body = {"action": "to", "to": 'https%3A%2F%2Ftrain.m.jd.com'}
        sign = auth.sign('genToken', self.uuid, json.dumps(body))
        url = 'http://api.m.jd.com/client.action?functionId=genToken&clientVersion=5.3.0&build=36639&client=android&d_brand=ZTE&d_model=SCH-I779&osVersion=4.4.2&screen=1280*720&partner=tencent&uuid=%s&area=1_2802_0_0&networkType=wifi&st=%s&sign=%s&sv=122' % (
            self.uuid, sign[1], sign[0])
        print url

        headers = {
            'Charset': 'UTF-8',
            'Connection': 'close',
            'Cookie': cookie,
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

        resp = requests.post(url, data='body=' + urllib.quote(json.dumps(body)) + '&', headers=headers)
        print resp.text

        resp_body = resp.json()
        # {"code":"0","tokenKey":"AAEAMKMEfWAYh1fRAvE0siwbJrEjuCmaht3Of-dkAaMMpGzemdi7WsCeMn3EaUdejhCZvQ0","url":"http://un.m.jd.com/cgi-bin/app/appjmp"}

        url = 'http://un.m.jd.com/cgi-bin/app/appjmp?tokenKey=' + resp_body[
            'tokenKey'] + '&to=https%3A%2F%2Ftrain.m.jd.com&lbs='
        session = requests.session()
        resp = session.get(url, headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': self.user_agent})

        return session.cookies.get_dict()
