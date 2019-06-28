from requests_html import HTMLSession
# import sqlite3
import psycopg2
import multiprocessing

session = HTMLSession()
base_url = 'https://tw.appledaily.com'
# 分頁的連接列表
page_url_lists = ['/new/realtime/1']
# 貼文網址
post_url = []
# 貼文內容
# post_detail = {}

def get_page(url, page_url_lists):
    # 讀取分頁url, 插入分頁page_url_lists
    r = session.get(url)
    get_url = r.html.find('.lisw a')

    if get_url and get_url[-1].attrs['href'] not in page_url_lists:
        for i in get_url:
            if i.attrs['href'] not in page_url_lists:
                page_url_lists.append(i.attrs['href'])
    else:
        return page_url_lists

def get_post_url(page_url):
    # 輸入分頁url，讀取個文章連接
    r = session.get(base_url+page_url)
    full_html_sets = r.html.find('.rtddt')
    for i in full_html_sets:
        post_url.append(list(i.links)[0])
    return post_url

def get_post_detail(per_page_url):
    # 讀取貼文詳細資訊
    r = session.get(per_page_url)
    try:
        title = r.html.find('h1')[0].text
    except:
        title=''
    try:
        view = int(r.html.find('.ndArticle_view')[0].text)
    except:
        view = ''
    try:
        time = r.html.find('.ndArticle_creat')[0].text.replace("出版時間：","")
    except:
        time=''
    try:
        content = r.html.find('.ndArticle_content p')[0].text
    except:
        content=''
    detail={'title':title, 'view':view, 'time':time, 'content':content, 'url':per_page_url}
    return detail

if __name__=="__main__":
    # 讀每頁，這邊也應該用多進程多線程的
    for i in page_url_lists:
        get_post_url(i)
        # 如果跑到下10頁，讀接下來十頁的頁連接
        if i == page_url_lists[-1]:
            my_url = base_url+i
            get_page(my_url, page_url_lists)
        else:
            continue
    # 多進程原本沒用多進程，跑一次要半小時，現在好多了，雖然還是慢
    pool = multiprocessing.Pool(processes=10)
    pool_outputs = pool.map(get_post_detail, post_url)
    pool.close()
    pool.join()

    # conn = sqlite3.connect('apple.db') 上方註解是跑sqlite的
    # 實際是跑postgresql
    conn = psycopg2.connect(database="", user="", password="", host="", port="")
    c = conn.cursor()
    # 看資料庫有無表單，沒有就加
    # add_sql = 'CREATE TABLE if not exists "apple_news" ("title" text, "content" text, "time" text, "view" integer, "url" text NOT NULL, PRIMARY KEY ("url"));'
    add_sql = 'create table if not exists apple_news("title" varchar(255) COLLATE "pg_catalog"."default", "content" text COLLATE "pg_catalog"."default", "time" varchar(20) COLLATE "pg_catalog"."default", "view" int8, "url" varchar(100) COLLATE "pg_catalog"."default" NOT NULL, CONSTRAINT "news_pkey" PRIMARY KEY ("url"));'
    c.execute(add_sql)
    # 如果資料庫沒有就新增，有就更新
    # sql = "REPLACE INTO apple_news (title, content, time, view, url) VALUES (:title, :content, :time, :view, :url);"
    sql = """INSERT INTO apple_news VALUES (%(title)s, %(content)s, %(time)s, %(view)s, %(url)s) ON CONFLICT(url) DO UPDATE SET title=excluded.title, content=excluded.content, view=excluded.view, time=excluded.time;"""
    c.executemany(sql, pool_outputs)
    conn.commit()
    conn.close()
