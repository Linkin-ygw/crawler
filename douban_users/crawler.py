import os
import urllib
import random
import string
from bs4 import BeautifulSoup
import requests
import time
from configparser import ConfigParser
headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
    "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
}
class Crawler:
    def __init__(self, session):
        self.session = session
        self.gen_bid()

    def gen_bid(self):
        headers["Cookie"] = "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))

    def get_friend_links(self, url):
        url = url + 'contacts'

        #print(url)
        contact_links = []
        try:
            r = self.session.get(url)
            soup = BeautifulSoup(r.content, 'lxml')
        except requests.ConnectionError as e:
            print(e)
            return contact_links


        for item in soup.findAll('dl', {'class':'obu'}):
            contact_links.append(item.dt.a['href'])
        #print(contact_links)
        return contact_links

    def get_rev_links(self, url):
        url = url + 'rev_contacts'
        #print(url)
        contact_links = []
        try:
            r = self.session.get(url)
            soup = BeautifulSoup(r.content, 'lxml')
        except requests.ConnectionError as e:
            print(e)
            return contact_links

        for item in soup.findAll('dl', {'class':'obu'}):
            contact_links.append(item.dt.a['href'])
        #print(contact_links)
        return contact_links

    def crawler(self, url):
        try:
            r = self.session.get(url)
            #r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.content, 'lxml')
        except requests.ConnectionError as e:
            print(e)
            return None

        print('crawl ' + url)
        try:
            text = str(soup.find('div',{'class':'article'}).text).strip()
            if text.find('用户管理细则') != -1 or text.find('注销时间') != -1:
                info = {'url':url, 'invalid':True}
                return info
        except Exception as e:
            print(e)

        user_info = soup.find('div',{'class':'user-info'})
        try:
            location = user_info.find('a').text
        except:
            location = None
        try:
            name_time = user_info.find('div').text
            name = name_time.split()[0]
            time = name_time.split()[1][:-2]
        except:
            name = None
            time = None
        try:
            friend_num = int(soup.find('div',{'id':'friend'}).find('a').text[2:])
            rev_num = soup.find('p',{'class':'rev-link'}).a.text
            rev_num = int(rev_num[rev_num.find('被')+1:-3])
        except:
            friend_num = 0
            rev_num = 0
        friend_links = []
        rev_links = []
        #if friend_num > 0:
        #    friend_links = self.get_friend_links(url)

        #if rev_num > 0:
        #    rev_links = self.get_rev_links(url)

        if name == None:
            info = None
        else:
            info = {'name':name, 'location':location, 'time':time, 'friend_num':friend_num,
        'rev_num':rev_num, 'url':url, 'friend':friend_links, 'rev':rev_links}

        return info

    def check(self, url, soup):
        import urllib
        cap = soup.find('img',{'alt':'captcha'})
        if cap != None:
            urllib.request.urlretrieve(cap['src'],'captcha.png')
            print('请输入验证码:')
            captcha = input()
            captcha_id = soup.find('input',{'name':'captcha-id'})['value']
            form_data={
            'ck':'PndI',
            'captcha-solution':captcha,
            'captcha-id':captcha_id,
            'original-url':url
            }
            r = self.session.post('https://www.douban.com/misc/sorry', data=form_data)
        else:
            return
