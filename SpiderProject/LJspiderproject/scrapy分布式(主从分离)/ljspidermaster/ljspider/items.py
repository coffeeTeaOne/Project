
import scrapy


class LjspiderItem(scrapy.Item):
    collection = 'fang'
    id= scrapy.Field()
    img_src = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    house_model = scrapy.Field()
    acreage = scrapy.Field()
    towards = scrapy.Field()
    decorate = scrapy.Field()
    lift = scrapy.Field()
    # info = scrapy.Field()
    flood = scrapy.Field()
    all_money = scrapy.Field()
    single_money = scrapy.Field()

    tag = scrapy.Field()

    type = scrapy.Field()   # 新房/二手房

    city = scrapy.Field()   # 区域信息
    area = scrapy.Field()   # 区域信息


class MasterRedisItem(scrapy.Item):
    url = scrapy.Field()



