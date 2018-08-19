
import pymongo
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
            # 保存更新车辆的详细信息
            self.collection.update(
                {'car_id': item['car_id']},
                {'$set': {
                    'car_data': dict(item['car_data'])}
                },
                True
                )
        return item



