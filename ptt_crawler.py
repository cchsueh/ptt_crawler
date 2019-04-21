import requests
import time
import json
from bs4 import BeautifulSoup


PTT_URL = 'https://www.ptt.cc'


def get_web_page(url):
    resp = requests.get(
        url=url
        # cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html5lib')

    # 取得上一頁的連結
    paging_div = soup.find('div', 'btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']

    # 儲存取得的文章資料
    articles = []
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        if d.find('div', 'date').text.strip() == date:
            # 取得文章連結及標題
            if d.find('a'):    # 有超連結，表示文章存在，未被刪除
                href = d.find('a')['href']
                title = d.find('a').text
                author = d.find('div', 'author').text if d.find('div', 'author') else ''
                articles.append({
                    'title': title,
                    'href': href,
                    'author': author
                })

    return articles, prev_url


def search_articles(articles, query):
    search_list = []
    for article in articles:
        if query in article['title']:
            search_list.append(article)
    return search_list


if __name__ == '__main__':
    current_page = get_web_page(PTT_URL + '/bbs/Baseball/index.html')
    if current_page:
        articles = []  # 全部的今日文章
        today = time.strftime("%m/%d").lstrip('0')  # 今天日期, 去掉開頭的 '0' 以符合 PTT 網站格式
        current_articles, prev_url = get_articles(current_page, today)  # 目前頁面的今日文章
        while current_articles:  # 若目前頁面有今日文章則加入 articles，並回到上一頁繼續尋找是否有今日文章
            articles += current_articles
            current_page = get_web_page(PTT_URL + prev_url)
            current_articles, prev_url = get_articles(current_page, today)

        # 儲存或處理文章資訊
        print('今天有', len(articles), '篇文章')
        for a in articles:
            print(a)
        with open('baseball.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, sort_keys=True, ensure_ascii=False)

        print('--------------------------------------------------------')
        query = input('請輸入要搜尋的關鍵字: ')
        search_list = search_articles(articles, query)
        print('今天共有', len(search_list), '筆有關', query, '的文章')
        print(search_list)