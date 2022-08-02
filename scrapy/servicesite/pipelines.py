import hashlib
import logging
from urllib.parse import urlparse
from datetime import datetime

from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.python import to_bytes
from twisted.internet.defer import DeferredList
from sqlalchemy.orm import sessionmaker

from servicesite.database import Pages, db_connect

from servicesite.items import BookMeta, Comment, MovieMeta, Subject
from servicesite.strategies.s3 import S3Strategy


class DatabasePipeline(object):
    def __init__(self) -> None:
        engine = db_connect()
        self.session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        _session = self.session()
        pages = Pages(**item) # pages model

        try:
            _session.add(pages)
            _session.commit()
        except Exception as e:
            _session.rollback()
            logging.warn(item)
            logging.error(e)
            raise
        finally:
            _session.close()

        return item


class S3Pipeline(object):
    """
    upload files to s3
    """
    def __init__(self, settings) -> None:
        url = settings['PIPELINE_S3_URL']
        o = urlparse(url)
        self.bucket_name = o.hostname
        self.object_key_template = o.path[1:]  # trail the first '/'

        self.strategy = S3Strategy(settings)
        if o.scheme != 's3':
            raise ValueError('PIPELINE_S3_URL must start with s3://')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler.stats)
    
    def process_item(self, item, spider):
        """
        Process single item. Add item to items and then upload to S3/GCS
        if size of items >= max_chunk_size.
        """
        self._timer_cancel()

        self.items.append(item)
        if len(self.items) >= self.max_chunk_size:
            self._upload_chunk()

        self._timer_start()

        return item

    def open_spider(self, spider):
        """
        Callback function when spider is open.
        """
        # Store timestamp to replace {time} in S3PIPELINE_URL
        self.ts = datetime.utcnow().replace(microsecond=0).isoformat().replace(':', '-')
        self._spider = spider
        self._timer = None

    def close_spider(self, spider):
        """
        Callback function when spider is closed.
        """
        # Upload remained items to S3.
        self._upload_chunk()
        self._timer_cancel()

    def _upload_chunk(self):
        """
        Do upload items to S3/GCS.
        """

        if not self.items:
            return  # Do nothing when items is empty.

        f = self._make_fileobj()

        # Build object key by replacing variables in object key template.
        object_key = self.object_key_template.format(**self._get_uri_params())

        try:
            self.strategy.upload_fileobj(f, self.bucket_name, object_key)
        except UploadError:
            self.stats.inc_value('pipeline/s3/fail')
            raise
        else:
            self.stats.inc_value('pipeline/s3/success')
        finally:
            # Prepare for the next chunk
            self.chunk_number += len(self.items)
            self.items = []

    def _get_uri_params(self):
        params = {}
        for key in dir(self._spider):
            params[key] = getattr(self._spider, key)

        params['chunk'] = self.chunk_number
        params['time'] = self.ts
        return params

    def _make_fileobj(self):
        """
        Build file object from items.
        """

        bio = BytesIO()
        f = gzip.GzipFile(mode='wb', fileobj=bio) if self.use_gzip else bio

        # Build file object using ItemExporter
        exporter = self.exporter_cls(f, encoding='utf-8')
        exporter.start_exporting()
        for item in self.items:
            exporter.export_item(item)
        exporter.finish_exporting()

        if f is not bio:
            f.close()  # Close the file if GzipFile

        # Seek to the top of file to be read later
        bio.seek(0)

        return bio

    def _timer_start(self):
        """
        Start the timer in s3pipeline
        """
        self._timer = Timer(self.max_wait_upload_time, self._upload_chunk)
        self._timer.start()

    def _timer_cancel(self):
        """
        Stop the timer in s3pipeline
        """
        if self._timer is not None:
            self._timer.cancel()


class CoverPipeline(ImagesPipeline):
    def process_item(self, item, spider):
        if "meta" not in spider.name:
            return item
        info = self.spiderinfo
        requests = arg_to_iter(self.get_media_requests(item, info))
        dlist = [self._process_request(r, info, item) for r in requests]
        dfd = DeferredList(dlist, consumeErrors=1)
        return dfd.addCallback(self.item_completed, item, info)

    def file_path(self, request, response=None, info=None, *, item=None):
        guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return "%s%s/%s%s/%s.jpg" % (guid[9], guid[19], guid[29], guid[39], guid)

    def get_media_requests(self, item, info):
        if item["cover"]:
            return Request(item["cover"])

    def item_completed(self, results, item, info):
        image_paths = [x["path"] for ok, x in results if ok]
        if image_paths:
            item["cover"] = image_paths[0]
        else:
            item["cover"] = ""
        return item
