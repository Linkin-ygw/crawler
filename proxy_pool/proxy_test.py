import pymongo
import requests

headers = {
'User-Agent':
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

class ProxyTest:
    def __init__(self):
        self.proxys = []
        client = pymongo.MongoClient(host="localhost", port=27017)
        db = client['proxyPool']
        for item in db.Pool.find():
            self.proxys.append(item)

    def proxy_test(self):
        test_url = 'https://www.baidu.com/'
        for proxy in self.proxys:
            proxies = {"https": "https://{proxy}".format(proxy=proxy['proxy'])}
            try:
                r = requests.get(test_url, headers=headers, proxies=proxies, timeout=10, verify=False)
                if r.status_code == 200:
                    print(proxy['proxy'] + 'is ok')
            except Exception as e:
                print(proxy['proxy'] + 'fail')
                print(e)
                continue

if __name__ == '__main__':
    test = ProxyTest()
    test.proxy_test()
