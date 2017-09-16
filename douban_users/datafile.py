import pymongo

class DataFile:
    def __init__(self, dbname='douban_users_1'):
        self.dbname = dbname
        self.db = self.get_db()

    def get_db(self):
        client = pymongo.MongoClient(host="localhost", port=27017)
        db = client[self.dbname]
        return db

    def get_collection(self, name='informations'):
        coll = self.db[name]
        return coll

    def insert_one_doc(self, doc):
        coll = self.get_collection()
        information_id = coll.insert(doc)
        return information_id

    def insert_one_invalid_url(self, url):
        coll = self.db['invalidUrl']
        information_id = coll.insert(url)
        return information_id

    def get_invalid_url(self):
        urls = []
        for item in self.db['invalidUrl'].find():
            urls.append(item['url'])
        return urls

    def insert_multi_docs(self, docs):
        coll = self.get_collection()
        information_id = coll.insert(docs)
        return information_id

    def load_crawed_list(self):
        crawled_list = []
        coll = self.get_collection()
        for item in coll.find():
            crawled_list.append(item['url'])
        return crawled_list

    def load_uncrawled_user_list(self, crawled_set):
        un_crawled_user_list = []
        invalid_url = set(self.get_invalid_url())
        coll = self.get_collection()
        for item in coll.find():
            for url in item['rev']:
                if url not in crawled_set and url not in invalid_url:
                    un_crawled_user_list.append(url)
        for item in coll.find():
            for url in item['friend']:
                if url not in crawled_set and url not in invalid_url:
                    un_crawled_user_list.append(url)
        if len(un_crawled_user_list) == 0:
            un_crawled_user_list.append('https://www.douban.com/people/63439633/')
        return un_crawled_user_list
