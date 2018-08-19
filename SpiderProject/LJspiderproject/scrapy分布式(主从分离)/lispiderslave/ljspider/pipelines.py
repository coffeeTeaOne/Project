
import pymongo
from scrapy.conf import settings

from ljspider.items import LjspiderItem


class LjspiderPipeline(object):

    def process_item(self, item, spider):
        return item

class LjPymongoPipeline(object):
    def __init__(self):
        conn = pymongo.MongoClient(host=settings['MONGODB_HOST'], port=settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[LjspiderItem.collection]

    def process_item(self,item,spider):
        if isinstance(item, LjspiderItem):
            self.collection.update({'id': item['id']}, {'$set': item}, True)
            return item


