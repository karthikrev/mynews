# mynews

          My personal news site aggregatore written in python + sqlite and AngularJS
            a. Reads list of rss feed url from "links.conf" 
            b. Reads the news feed and content. Content is clutter-removed using readability.com API
            c. Stored in sqlite3
            d. Using flask web server the content is displayed and rendered using AngularJS. PFA Screenshot



Pre reqs
========
easy_install feedparser
easy_install flask


Run 
===
python update.py # To update the news each time
python service.py  # your news site will be available on  http://localhost:5000


Configure
=========
configure your rss feed links in links.conf
