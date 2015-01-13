
import sqlite3
import json
import feedparser
import urllib2
import time
import re


def to_readable(url):
    try:
        print ">>>" + url
        response = urllib2.urlopen("https://www.readability.com/api/content/v1/parser?url="+url+"&token=17a156baecad6bad220569ec1be2392b4f8b5d41")
    except Exception as e:
        print "Readabilty failed: " + str(e)
        return "", "", ""
    readable_news = json.load(response)
    content = re.sub("\"", '\'', readable_news['content'])
    content = re.sub("\\n|\\t", '', content)
    return readable_news['title'] or "-", readable_news['lead_image_url'] or "-", content or "-"


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("data/news.db")
        self.connection.row_factory = self.dict_factory
        with self.connection:
            self.cur = self.connection.cursor()
            self.cur.execute('create table if not exists News(title text, lead_image_url text, content text, news_link text, time timestamp, read int, feedname text, UNIQUE(news_link))')
            self.connection.commit()

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def insert(self, row_data):
        self.cur.execute("insert into News values (?, ?, ?, ?, ?, ?, ?)", row_data)
        self.connection.commit()

    def set_read(self, read_url):
        query = "update News set read = 1 where news_link = \"" + read_url + "\""
        print query
        self.cur.execute(query)
        self.connection.commit()

    def readall(self):
        return self.cur.execute("select * from News").fetchall()

    def read_feednames(self):
        return self.cur.execute("select feedname from news group by feedname")

    def read_by_feedname(self, feedname):
        return self.cur.execute("select * from News where feedname = \"" + feedname + "\" order by time DESC limit 12").fetchall()


class Feedmanager:
    def __init__(self):
        self.DB = Database()
        self.links_to_be_readable = []

    def updatefeeds(self):
        f = open('links.conf', 'r')
        for U in f.readlines():
            flink, fname = U.split(',')
            fname = fname.strip()
            self.links_to_be_readable += [(entry['link'], fname) for entry in feedparser.parse(flink).entries if entry['link'] not in self.read_all_links()][:12]
        now = int(time.time())
        for news_link, feed_name in self.links_to_be_readable:
            title, img, content = to_readable(news_link)
            print "News: " + title
            self.DB.insert((title, img, content, news_link, now, 0, feed_name)) if title else None

    def read_all_links(self):
        all_rows = self.DB.readall()
        return [row['news_link'] for row in all_rows]

    def read_all_news(self):
        all_news = {}
        for feed_name_dict in self.DB.read_feednames():
            fname = feed_name_dict['feedname']
            db = Database()
            all_news[fname] = db.read_by_feedname(fname)
        return json.dumps(all_news)


from flask import Flask, request
app = Flask(__name__, static_url_path='')


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/fetchnews')
def fetch_to_web():
    return F.read_all_news()


@app.route('/markread')
def mark_as_read():
    DB = Database()
    DB.set_read(request.args.get('feedurl'))
    return "marked read"


@app.route('/updatenews')
def updatenews():
    F.updatefeeds()
    return "ok"


if __name__ == "__main__":
    F = Feedmanager()
    app.run()

