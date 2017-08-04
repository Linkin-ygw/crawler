import requests
from bs4 import BeautifulSoup
import urllib
import time
import pymongo
import urllib
from lxml import etree
import re

headers = {
'User-Agent':
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

class crawler:
    def __init__(self, dbname, collection_name, url):
        self.urls = []
        self.dbname = dbname
        self.url = url
        self.collection_name = collection_name
        self.db = self.get_db()

    def get_db(self):
        client = pymongo.MongoClient(host="localhost", port=27017)
        db = client[self.dbname]
        return db

    def get_collection(self, conllection_name):
        coll = self.db[conllection_name]
        return coll

    def insert_one_doc(self, collection_name, doc):
        coll = self.db[collection_name]
        information_id = coll.insert(doc)
        print (information_id)

    def clear_all_datas(self, collection_name):
        db[collection_name].remove()

    def getPeopleUrls(self):
        try:
            r = requests.get(self.url, headers=headers)
        except requests.ConnectionError as e:
            print(e)
            time.sleep(10)

        soup = BeautifulSoup(r.content, 'lxml')
        ss = soup.find('div', {'class':'main-content'})
        for s in ss.findAll('div', {'class':'para'}, recursive=False):
            for t in s.findAll('a'):
                try:
                    link = t['href']
                    self.urls.append(link)
                except:
                    continue

    def getPeopleInfo(self):
        for u in self.urls:
            try:
                url = 'https://baike.baidu.com' + u
                r = requests.get(url, headers = headers)
                print(url)
            except requests.ConnectionError as e:
                print(e)

            soup = BeautifulSoup(r.content, 'lxml')

            peopleinfo = {}
            itemname = []
            itemvalue = []
            basicinfo = soup.find('div', {'class':'basic-info cmn-clearfix'})
            for name in basicinfo.find_all('dt', {'class':'basicInfo-item name'}):
                print(name.string.strip())
                itemname.append(name.string.strip())
            for value in basicinfo.find_all(re.compile('^dd')):
                print(value)
                itemvalue.append(value.string.strip())
            time.sleep(10000)

            print(itemname)
            print(itemvalue)
            for name, value in zip(itemname, itemvalue):
                peopleinfo.setdefault(name, "")
                peopleinfo[name] = value
            print(peopleinfo)
            self.insert_one_doc(peopleinfo)

crawler = crawler('yuanshi','information', 'https://baike.baidu.com/item/%E4%B8%AD%E5%9B%BD%E7%A7%91%E5%AD%A6%E9%99%A2%E9%99%A2%E5%A3%AB')
crawler.getPeopleUrls()
crawler.getPeopleInfo()
