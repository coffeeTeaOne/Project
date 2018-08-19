
import pymongo
import redis
from scrapy.conf import settings

from guazispider.items import RrcSpider, CarMsgSpider


class GuazispiderPipeline(object):
    def process_item(self, item, spider):
        return item


class RrcPymongoPipeline(object):
    def __init__(self):
        # 连接数据库(mongodb)
        conn = pymongo.MongoClient(host=settings['MONGODB_HOST'],port=settings['MONGODB_PORT'])
        db = conn[settings['MONGODB_DB']]
        self.collection = db[RrcSpider.collection]

    def process_item(self, item, spider):
        # 车辆基本信息
        if isinstance(item, RrcSpider):
            self.collection.update({'car_id':item['car_id']},{'$set': item}, True)

        # 车辆详细信息
        if isinstance(item, CarMsgSpider):
            self.collection.update(
                {'car_id': item['car_id']},
                {'$addToSet': {
                    'car_data': {'$each': item['car_data']}
                }},
                True
                )
        return item


class RedisRrcPipeline(object):
    def __init__(self):
        self.r = redis.Redis(host=settings['REDIS_HOST'],
                             port=settings['REDIS_PORT'])

    def process_item(self, item, spider):
        self.r.lpush('guazi:start_urls', item['url'])
        return item



