import requests
from bs4 import BeautifulSoup
from src.NovelWeb import NovelWeb
from src.util.RedisUtil import RedisUtil
from src.util.MongoUtil import MongoUtil
from src.model.NovelModel import NovelModel
from lxml import etree
from src.Constant import Constant
import time
from multiprocessing import Pool

redis_util = RedisUtil()
mongo_util = MongoUtil()
novelModel = NovelModel()
novel_web = NovelWeb()


# 获取每个分类的首页网址
def parse_index_list(class_name, url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    a_last = soup.find('a', 'last')
    host = a_last['href']
    last_page = a_last.contents[0]
    if last_page and host:
        host = host[0: host.index(last_page)] + "{}.html"
        generate_class_index(class_name, host, int(last_page))


# 保存分类的网址到redis
def generate_class_index(class_name, host, last):
    if last <= 0:
        return

    key = 'qbw_{}'.format(class_name)
    url_list = []
    for i in range(1, last + 1):
        url = host.format(i)
        url_list.append(url)
    redis_util.save_index_url(key, url_list)
    # print(url_list)


# 解析每本小说到地址
def parse_novel_url(index_url):
    repeat = 0
    while repeat < 3:
        content = requests.get(index_url).content
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            dls = soup.find('div', 'sitebox').find_all('dl')
            books = []
            for dl in dls:
                a = dl.find('dd').find('a')
                # print(novelModel.get_simple_info(a.contents[0], a['href']))
                books.append(novelModel.get_simple_info(a.contents[0], a['href']))
            return books
        else:
            print('爬取网站{}出错'.format(index_url))
            repeat += 1


# 保存小说地址到mongo
def save_novel_url():
    bqw = novel_web.get_bqw()
    # for i in bqw:
    #     parse_index_list(i['class_name'], i['href'])

    for i in bqw:
        urls = redis_util.get_index_urls('qbw_{}'.format(i['class_name']))
        print('爬取{}类共{}条'.format(i['class_name'], len(urls)))
        if urls:
            sleep_page = 0
            total_page = 0
            books = []
            print(len(urls))
            for url in urls:
                if len(books) >= 100:
                    mongo_util.novel_add_many(books)
                    books.clear()
                    break

                # if sleep_page >= 10:
                #     time.sleep(1)
                #     sleep_page = 0

                books.extend(parse_novel_url(url))
                sleep_page += 1
                total_page += 1
                print(total_page)
            # if books:
            #     mongo_util.novel_add_many(books)


# 解析小说信息
def parse_novel_info(url):
    tree = etree.HTML(requests.get(url).content, etree.HTMLParser())
    img = xpath(tree, Constant.XPATH_IMG)
    title = xpath(img, Constant.XPATH_TITLE)
    cover_url = novel_web.get_bqw_host() + '{}'.format(xpath(img, Constant.XPATH_COVER))
    cover_width = xpath(img, Constant.XPATH_COVER_WIDTH)
    cover_height = xpath(img, Constant.XPATH_COVER_HEIGHT)
    author = xpath(tree, Constant.XPATH_AUTHOR)
    desc = xpath(tree, Constant.XPATH_DESCRIPTION)
    classify = xpath(tree, Constant.XPATH_CLASSIFY)
    classify = classify[0: -2]
    chapters = xpath(tree, Constant.XPATH_CHAPTERS)

    chapter_names = chapters.xpath(Constant.XPATH_CHAPTER_NAME)
    chapter_hrefs = chapters.xpath(Constant.XPATH_CHAPTER_HREF)
    chapter_thread_list = []
    start = time.time()
    if len(chapter_names) == len(chapter_hrefs) and len(chapter_names) <= 1000:
        for i in range(0, len(chapter_names)):
            chapter_hrefs[i] = url + chapter_hrefs[i]
            chapter_thread_list.append({'name': chapter_names[i],
                                        'href': chapter_hrefs[i]})
    else:
        print('《{}》超过1000章跳过'.format(title))
        return
    print('爬取《{}》。。。'.format(title))
    pool = Pool(5)
    chapters_list = pool.map(get_novel_content, chapter_thread_list)
    if chapters_list and len(chapters_list) == len(chapter_names):
        novel = novelModel.get_novel_info(name=title, classify=classify, cover=cover_url, cover_width=cover_width,
                                          cover_height=cover_height, author=author, desc=desc,
                                          chapters=chapters_list)
    else:
        print('章节数对不上')
    print('完成{}-------花费{}s'.format(title, (time.time() - start)))
    if novel:
        mongo_util.novel_add_one(novel)
    pool.close()
    # return novel


def xpath(src, path):
    return src.xpath(path)[0]

def get_novel_content(novel):
    content = etree.HTML(requests.get(novel['href']).content, etree.HTMLParser()) \
        .xpath(Constant.XPATH_CHAPTER_CONTENT)
    return novelModel.get_chapter(novel['name'], novel['href'], content)


# 保存小说到mongo
def save_novel_info():
    urls = list(mongo_util.novel_find_all_from_temp())
    for i in range(0, len(urls)):
        if i >= 780:
            # parse_novel_info(urls[i]['href'])
            try:
                parse_novel_info(urls[i]['href'])
            except Exception as e:
                print('下载出错')
                time.sleep(5)


# if __name__ == '__main__':
#     save_novel_info()
