import os
import time
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
import requests

from datafile import DataFile
from login import Login
from crawler import Crawler

task_queue = Queue()

response_queue = Queue()

data = DataFile()

thread_numbers = 3

class MasterThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        crawled_list = data.load_crawed_list()
        self.crawled_set = set(crawled_list)
        un_crawled_user_list = data.load_uncrawled_user_list(self.crawled_set)
        self.task_set = set()
        for user_url in un_crawled_user_list:
            task_queue.put(user_url)
            self.task_set.add(user_url)
        self.temp_user_infos = []

        print(len(crawled_list))
        print(len(un_crawled_user_list))

    def run(self):
        while len(self.crawled_set) < 1000000:
            if response_queue.empty() == True:
                print('response_queue empty')
                time.sleep(50)
                continue

            #print('master thread work')
            info = response_queue.get()
            #print(info)

            if info['url'] in self.task_set:
                self.task_set.remove(info['url'])

            if info.get('invalid') != None:
                data.insert_one_invalid_url({'url':info['url']})
            else:
                for url in info['friend']:
                    if url not in self.crawled_set and url not in self.task_set:
                        task_queue.put(url)
                        self.task_set.add(url)

                for url in info['rev']:
                    if url not in self.crawled_set and url not in self.task_set:
                        task_queue.put(url)
                        self.task_set.add(url)
                if info['name'] != None:
                    #data.insert_one_doc(info)
                    self.temp_user_infos.append(info)
                    #print(len(self.temp_user_infos))
                    if len(self.temp_user_infos) > 100:
                        print(data.insert_multi_docs(self.temp_user_infos))
                        self.temp_user_infos.clear()
                else:
                    self.crawled_set.add(info['url'])

        print('master thread exit!!')


class WorkerThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            if task_queue.empty() == True:
                print('task_queue empty')
                time.sleep(2)
                continue
            url = task_queue.get()
            #print('worker: ' + url)
            info = crawler.crawler(url)
            if info != None:
                response_queue.put(info)
            time.sleep(4)
        print('worker thread exit!')

if __name__ == '__main__':
    login = Login()
    login.login()
    crawler = Crawler(login.session)
    #crawler = Crawler(None)

    master = MasterThread()
    worker = []
    for i in range(thread_numbers):
        worker.append(WorkerThread())

    for i in range(thread_numbers):
        worker[i].start()
    master.start()

    master.join()
    for i in range(thread_numbers):
        worker[i].join()
