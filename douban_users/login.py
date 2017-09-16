import os
import urllib
from bs4 import BeautifulSoup
import requests
from configparser import ConfigParser

headers = {
    "Host":"www.douban.com",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
    "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding":"gzip, deflate",
    "Connection":"keep-alive"
}

class Login:
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.cookies = None
        self.session = requests.Session()
        self.session.headers.update(headers)
        #self.s = requests.session()

    def read_account_from_file(self):
        cf = ConfigParser()
        if os.path.exists(self.config_file) and os.path.isfile(self.config_file):
            cf.read(self.config_file)
            email = cf.get('info', 'email')
            password = cf.get('info', 'password')
            return (email, password)
        else:
            print('配置文件不存在！！！')
            return(None, None)

    def build_form_data(self):
        email, password = self.read_account_from_file()
        if email == None or password == None:
            print('请输入用户名和密码\n用户名：')
            email = input()
            print('密码：')
            password = input()
        form_data = {
            'source':'index_nav',
            'form_email':email,
            'form_password':password,
            'remember':'on',
            'login':'登录',
            'redir': 'https://www.douban.com/people/153329708/'
            }

        return form_data

    def getcaptcha(self, soup):
        cap = soup.find('img',{'id':'captcha_image'})
        if cap != None:
            urllib.request.urlretrieve(cap['src'],'captcha.png')
            print('请输入验证码:')
            captcha_solution = input()
            captcha_id = soup.find('input',{'name':'captcha-id'})['value']
        else:
            captcha_solution = None
            captcha_id = None
        return captcha_solution, captcha_id

    def getContent(self, req):
        soup = BeautifulSoup(req.content)
        loginfo = soup.find('div', {'id':'content'}).h1

        if loginfo != None and loginfo.text == u'登录豆瓣':
            print('登录失败！！请重新登录')
            self.login()
        else:
            print('登录成功!!')

    def login(self):
        form_data = self.build_form_data()
        url = 'https://www.douban.com/accounts/login'
        r = self.session.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')

        captcha_solution, captcha_id = self.getcaptcha(soup)
        if captcha_solution != None:
            form_data['captcha-solution'] = captcha_solution
            form_data['captcha-id'] = captcha_id

        r = self.session.post(url, data=form_data, headers=headers)
        self.getContent(r)
        self.cookies = self.session.cookies

#if __name__ == '__main__':
#    login = Login()
#    login.login()
