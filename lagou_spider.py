import requests
from bs4 import BeautifulSoup
import pymongo
import csv
import time
from concurrent import futures

BASE_URL = 'https://www.lagou.com/zhaopin/'
DEFAULT_KEYWORD = 'Python'
count = 0

headers = {
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch, br',
'Accept-Language':'zh-CN,zh;q=0.8',
'Connection':'keep-alive',
'Cookie':'user_trace_token=20170907141546-fc86daef-9393-11e7-9123-5254005c3644; LGUID=20170907141546-fc86ddcf-9393-11e7-9123-5254005c3644; JSESSIONID=ABAAABAACEBACDG92BBE3ABBFFB0CAEB34FB11A4C79516D; index_location_city=%E5%85%A8%E5%9B%BD; X_HTTP_TOKEN=d2a0d87fdaafd93d8eb97d4fe8eba9a1; TG-TRACK-CODE=index_navigation; _gat=1; SEARCH_ID=44a5babf2216464f955af56b3a4be7ac; _gid=GA1.2.2140782754.1504764946; _ga=GA1.2.856745722.1504764946; LGSID=20170909082939-f736058a-94f5-11e7-8d02-525400f775ce; LGRID=20170909092513-ba4797f1-94fd-11e7-915c-5254005c3644; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1504764947; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1504920313',
'Upgrade-Insecure-Requests':'1',
'Host':'www.lagou.com',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}
def get_db():
    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client['lagou']
    #db['Python'].remove()
    return db

def insert_one_doc(db, doc):
    coll = db['positions']
    information_id = coll.insert_one(doc)
    print (information_id)

def insert_multi_docs(db, docs):
    coll = db['positions']
    information_id = coll.insert(docs)
    print (information_id)

def download_one_page(session, url):
    try:
        print(url)
        r = session.get(url, headers=headers)
    except requests.ConnectionError as e:
        print(e)
        return None
    return r.content

def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    #print(soup)
    my_position_list = []
    position_list = soup.find('div', {'class':'s_position_list'}).find('ul',{'class':'item_con_list'})
    if position_list == None:
        return None

    for position in position_list.find_all('li'):
        my_position = {}
        my_position['position_id'] = position['data-positionid']
        my_position['position_name'] = position['data-positionname']
        my_position['salary'] = position['data-salary']
        my_position['positon_label'] = position.find('div',{'class':'list_item_bot'}).find('div',{'class':'li_b_l'}).text.strip()
        my_position['company'] = position['data-company']
        my_position['company_id'] = position['data-companyid']
        my_position['company_industry'] = position.find('div',{'class':'company'}).find('div',{'class':'industry'}).text.strip()
        my_position['company_label'] = position.find('div',{'class':'list_item_bot'}).find('div', {'class':'li_b_r'}).text.strip()
        my_position['area'] = position.find('div',{'class':'position'}).find('span',{'class':'add'}).text.strip()
        my_position['link'] = position.find('a',{'class':'position_link'})['href']
        my_position_list.append(my_position)
    return my_position_list

def parse_job_detail(url):
    print(url)
    db = get_db()
    try:
        r = requests.get(url, headers = headers)
        soup = BeautifulSoup(r.content, 'lxml')
    except requests.ConnectionError as e:
        print(e)

    job_detail = {}
    job_detail['职位名称'] = soup.find('div',{'class':'job-name'}).find('span',{'class':'name'}).text
    job_request = soup.find('dd',{'class':'job_request'}).find_all('span')
    job_detail['薪水'] = job_request[0].text
    job_detail['城市'] = job_request[1].text
    job_detail['经验'] = job_request[2].text
    job_detail['学历'] = job_request[3].text
    job_detail['性质'] = job_request[4].text
    job_detail['职位诱惑'] = soup.find('dd',{'class':'job-advantage'}).p.text
    job_description = soup.find('dd',{'class':'job_bt'}).div.text
    job_detail['职位描述'] = job_description
    company = soup.find('dl',{'class':'job_company'})
    job_detail['公司名称'] = company.find('h2',{'class':'fl'}).text
    feature = company.find('ul',{'class':'c_feature'}).find_all('li')
    job_detail['公司领域'] = feature[0].text
    job_detail['发展阶段'] = feature[1].text
    job_detail['公司规模'] = feature[2].text
    insert_one_doc(db, job_detail)
    time.sleep(2)
    #print(job_detail)

def get_position_detail(position_list):
    links = [position['link'] for position in position_list]
    with futures.ThreadPoolExecutor(4) as executor:
        executor.map(parse_job_detail, links)

def get_catogry_urls():
    categorys = {}
    url = 'https://www.lagou.com/'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    category_list = soup.find_all('div',{'class':'menu_box'})
    for category in category_list:
        category_name = category.find('div',{'class':'category-list'}).h2.text.strip()
        for sub in category.find_all('dl'):
            sub_name = sub.dt.text
            sub_list = []
            for u in sub.find_all('a'):
                sub_list.append({u.text:u['href']})
            sub_category[sub_name] = sub_list
        categorys[category_name] = sub_category
    return categorys


def get_pages(url):
    r = requests.get(url, headers = headers)
    soup = BeautifulSoup(r.content, 'lxml')
    try:
        pages = int(soup.find('div',{'class':'pager_container'}).find_all('a')[-2].text)
    except:
        pages = 0
    return pages

def get_all_crawled_positions(db):
    coll = db['positions']
    positons = []
    for item in coll.find():
        positons.append(item['position_id'])
    return positons

def crawl_one_category(category):
    for key, value in category.items():

def main():
    db = get_db()

    for url in urls:
        pages = get_pages(url)
        print(pages)
        with requests.session() as session:
            for page in range(pages):
                position_list = parse(download_one_page(session, url + str(page+1) + '/?filterOption=3'))
                if position_list != None:
                    #print(position_list)
                    insert_multi_docs(db,  position_list)
                    #get_position_detail(position_list)
                time.sleep(2)

def delete_repeat_data(db):
    coll = db['positions']
    print(coll.count())
    for pid in coll.distinct('position_id'):
        num = coll.count({'position_id':pid})
        if num > 1:
            print(num)
            for i in range(num-1):
                coll.delete_one({'position_id':pid})
    print(coll.count())

if __name__ == '__main__':
    #get_all_type_urls()
    #main()
    db = get_db()
    delete_repeat_data(db)
