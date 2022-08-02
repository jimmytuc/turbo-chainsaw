import os
import json

from servicesite.util import get_domain_from_url, clean_tag
# from servicesite.items import Comment
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ClonetSiteSpider(CrawlSpider):
    name = 'clone_site_spider'
    allowed_domains = [
        get_domain_from_url(os.getenv('SITE_URL'))
    ]
    start_urls = [os.getenv('SITE_URL')]
    rules = (
        Rule(LinkExtractor(canonicalize=True, unique=True), callback='download_site', follow=True),
    )

    def download_site(self, response):
        filename = response.url.split('/')[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

    """
    extract meta data from site
    """
    def parse_item(self, response):
        title = response.xpath('//title/text()').extract()
