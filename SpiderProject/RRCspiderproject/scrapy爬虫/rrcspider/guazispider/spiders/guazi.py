from scrapy import Selector, Request
from scrapy.spiders import Spider
import re

from guazispider.items import RrcSpider, CarMsgSpider


class GuaZiSpider(Spider):
    name = 'guazi'
    # start_urls = []


    base_url = 'https://www.renrenche.com'

    # start_url = 'https://www.renrenche.com'     # 按全国所有城市筛选

    # main_url = 'https://www.renrenche.com/{city}/{brand}/p{page}/'   # 基本url

    start_url = 'https://www.renrenche.com/cd/'   # 按成都筛选

    main_url = 'https://www.renrenche.com/cd/{brand}/p{page}/'         # 基本url



    # 起始
    def start_requests(self):
        yield Request(self.start_url, callback=self.parse_info)

    # 车型
    def parse_info(self, response):
        ca = Selector(response)
        a_list = ca.xpath('//*[@id="brand_more_content"]/div/p/span/a')
        # 判断是否有a标签
        if a_list:
            try:
                for a in a_list:
                    # 类型
                    car_name = a.xpath('./text()').extract()[0]
                    car_href = a.xpath('./@href').extract()[0].split('/')[-2]
                    # 选定车型后的url
                    car_url = self.main_url.format(brand=car_href,page=1)

                    # 完成车型选型,获取车的基本信息
                    yield Request(car_url, callback=self.parse_msg, meta={'car_name': car_name,
                                                                          'car_href': car_href,
                                                                          'page': 1})

            except:
                pass
        else:
            pass

    # 获取车的基本数据信息
    def parse_msg(self, response):
        res = Selector(response)
        lis = res.xpath('//*[@id="search_list_wrapper"]/div/div/div[1]/ul/li')

        # 判断li标签存在,页数没有超过最大页,超过了最大页数静默处理
        if lis:
            item = RrcSpider()
            for li in lis:

                    #  车的编号
                    if li.xpath('./a/@data-car-id'):
                        item['car_id'] = li.xpath('./a/@data-car-id').extract()[0]

                    #  标题
                    if li.xpath('./a/h3/text()'):
                        item['title'] = li.xpath('./a/h3/text()').extract()[0]

                    #  首页图片
                    if li.xpath('./a/div[1]/img/@src'):
                        item['img'] = li.xpath('./a/div[1]/img/@src').extract()[0]

                    if li.xpath('./a/div[2]/span/text()'):
                        t = li.xpath('./a/div[2]/span/text()').extract()
                        #  上线时间
                        item['create_time'] = t[0]
                        #  里程
                        item['all_trip'] = t[1]

                    #  总价
                    if li.xpath('./a/div[4]/div/text()'):
                        price = li.xpath('./a/div[4]/div/text()').extract()[0]
                        rep = price.replace('\n', '')
                        item['all_price'] = rep.replace(' ', '')

                    #  首付
                    if li.xpath('./a/div[4]/div/div/div/text()'):
                        item['first_pay'] = li.xpath('./a/div[4]/div/div/div/text()').extract()[0]

                    #  类型
                    item['car_name'] = response.meta.get('car_name')


                    # 车的基本信息
                    yield item

                    # 处理分页,函数回调
                    page = response.meta.get('page') + 1
                    url = self.main_url.format(brand=response.meta.get('car_href'), page=page)
                    yield Request(url, callback=self.parse_msg, meta={'car_href': response.meta.get('car_href'),
                                                                      'car_name': response.meta.get('car_name'),
                                                                      'page': page})

                    # 获取车的超链接
                    if li.xpath('./a/@href'):
                        child_href = self.base_url + li.xpath('./a/@href').extract()[0]
                        # 获取车的详细信息
                        yield Request(child_href, callback=self.parse_child, meta={'car_id': item['car_id'],
                                                                                   'car_title': item['title']})
        else:
            pass

    # 车的详细信息获取
    def parse_child(self, response):
        ch = Selector(response)
        car_data = {}
        item = CarMsgSpider()
        try:
            # 月供
            if ch.xpath('//*[@id="basic"]/div[2]/div[2]/div[1]/div[3]/div[2]/p[5]/text()'):
                car_data['month_pay'] = ch.xpath('//*[@id="basic"]/div[2]/div[2]/div[1]/div[3]/div[2]/p[5]/text()').extract()[0]
            # 手续费
            if ch.xpath('//*[@id="js-service-wrapper"]/div[1]/p[2]/strong/text()'):
                car_data['poundage'] = ch.xpath('//*[@id="js-service-wrapper"]/div[1]/p[2]/strong/text()').extract()[0]
            # 车辆介绍信息
            if ch.xpath('//*[@id="gallery"]/div[1]/div[1]/div[2]/div/p/text()'):
                car_data['car_msg'] = ch.xpath('//*[@id="gallery"]/div[1]/div[1]/div[2]/div/p/text()').extract()[0]
            # 车辆详情图片
            if ch.xpath('//*[@id="gallery"]/div[1]/div[@class="detail-car-appearance"]/div[2]/div/img/@data-src'):
                car_data['car_imgs'] = ch.xpath('//*[@id="gallery"]/div[1]/div[@class="detail-car-appearance"]/div[2]/div/img/@data-src').extract()

            item['car_id'] = response.meta.get('car_id')
            item['car_data'] = car_data
        except:
            pass

        yield item



