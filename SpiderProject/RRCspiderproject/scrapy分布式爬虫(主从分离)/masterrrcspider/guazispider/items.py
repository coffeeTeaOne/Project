# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GuazispiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 车辆基本信息
class RrcSpider(scrapy.Item):
    collection = 'rrc'
    car_id = scrapy.Field()
    href = scrapy.Field()
    city_name = scrapy.Field()
    car_name = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    create_time = scrapy.Field()
    all_trip = scrapy.Field()
    all_price = scrapy.Field()
    first_pay = scrapy.Field()


# 车辆详细信息
class CarMsgSpider(scrapy.Item):
    collection = 'rrc'
    car_id = scrapy.Field()
    car_data = scrapy.Field()


class MasterRedisItem(scrapy.Item):
    url = scrapy.Field()


