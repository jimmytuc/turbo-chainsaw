import os
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from servicesite.util import get_domain_from_url, clean_tag
from servicesite.items import Metadata


class CloneSiteSpider(CrawlSpider):
    name = 'clone_spider'
    allowed_domains = [
        get_domain_from_url(os.getenv('SITE_URL'))
    ]

    def start_requests(self):
        urls = [
            os.getenv('SITE_URL')
        ]
        for url in urls:
            yield Request(url=url, callback=self.download_site)

    def download_site(self, response):
        filename = response.url.split('/')[-2] + '.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

    """
    extract meta data from site
    """
    def parse_item(self, response):
        title = response.xpath('//title/text()').extract_first()

        keywords = response.xpath('//meta[@name=\'keywords\']/@content').extract_first()
        description = response.xpath('//meta[@name=\'description\']/@content').extract_first()

        og_title = response.xpath('//meta[@property=\'og:title\']/@content').extract_first()
        og_description = response.xpath('//meta[@property=\'og:description\']/@content').extract_first()
        og_type = response.xpath('//meta[@property=\'og:type\']/@content').extract_first()
        og_image = response.xpath('//meta[@property=\'og:image\']/@content').extract_first()

        # yield Metadata(title, keywords, description)
