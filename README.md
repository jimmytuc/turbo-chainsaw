## Crawler

Python 3
Scrapy 2.6.2

### Docker
-------

scrapyd with Python 3.9 [python:3.9-slim-buster](https://pythonspeed.com/articles/base-image-python-docker-images/)


### SQL
------

The test database is located at docker/mysql/test.sql 。

### Usage
-------
    $ cd ./scrapy/docker
    $ sudo docker-compose up --build -d
    # 进入 douban_scrapyd 容器
    $ sudo docker exec -it douban_scrapyd bash
    # 进入 scrapy 目录
    $ cd /srv/ScrapyDouban/scrapy
    $ scrapy list
    # 抓取电影数据
    $ scrapy crawl movie_subject # 收集电影 Subject ID
    $ scrapy crawl movie_meta # 收集电影元数据
    $ scrapy crawl movie_comment # 收集电影评论
    # 抓取书籍数据
    $ scrapy crawl book_subject # 收集书籍 Subject ID
    $ scrapy crawl book_meta # 收集书籍元数据
    $ scrapy crawl book_comment # 收集书籍评论

If you want to easily modify the code during testing, you can mount the scrapy directory of the project path to the scrapyd container.

If you are used to working with scrapyd, you can deploy the project directly to the scrapyd container through scrapyd-client.
# turbo-chainsaw
