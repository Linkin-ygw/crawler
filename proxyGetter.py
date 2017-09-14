import requests
from bs4 import BeautifulSoup
import pymongo

headers = {
'User-Agent':
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

class ProxyGetter:
    def __init__(self):
        client = pymongo.MongoClient(host="localhost", port=27017)
        self.db = client['proxyPool']

    def get5UFreeProxy(self):
        '''
        获取无忧代理
        '''
        urllist = ['http://www.data5u.com/',
                    'http://www.data5u.com/free/',
                    'http://www.data5u.com/free/gngn/index.shtml',
                    'http://www.data5u.com/free/gnpt/index.shtml']
        proxys = []
        for url in urllist:
            try:
                r = requests.get(url, headers = headers)
                soup = BeautifulSoup(r.content)
            except requests.ConnectionError as e:
                print(e)

            #print(soup.find_all('div',class_='wlist')[1])
            wlist = soup.find_all('div',{'class':'wlist'})[1].find_all('ul',{'class':'l2'})
            #print(wlist)

            for w in wlist:
                proxy = w.find_all('span')
                proxys.append({'proxy':proxy[0].text +':'+ proxy[1].text})
            print(proxys)
        return proxys

    def write_to_database(self):
        proxys = self.get5UFreeProxy()
        collection = self.db.Pool
        collection.insert(proxys)

if __name__ == '__main__':
    proxyGetter = ProxyGetter()
    #print(proxyGetter.get5UFreeProxy())
    proxyGetter.write_to_database()
