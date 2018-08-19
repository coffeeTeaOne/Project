from scrapy import Selector, Request
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider


from guazispider.items import RrcSpider, CarMsgSpider


class GuaZiSpider(RedisSpider):
    name = 'guazi'
    redis_key = 'guazi:start_urls'

    base_url = 'https://www.renrenche.com'
    start_url = 'https://www.renrenche.com/cd/'  # 按成都筛选
    main_url = 'https://www.renrenche.com/cd/{brand}/p{page}/'  # 基本url

    # 获取车的基本数据信息
    def parse(self, response):
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
                    title = li.xpath('./a/h3/text()').extract()[0]
                    item['title'] = title
                    # 类型
                    item['car_name'] = title.split(' ')[0]

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

                # 车的基本信息
                yield item

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
                car_data['month_pay'] = \
                ch.xpath('//*[@id="basic"]/div[2]/div[2]/div[1]/div[3]/div[2]/p[5]/text()').extract()[0]
            # 手续费
            if ch.xpath('//*[@id="js-service-wrapper"]/div[1]/p[2]/strong/text()'):
                car_data['poundage'] = ch.xpath('//*[@id="js-service-wrapper"]/div[1]/p[2]/strong/text()').extract()[0]
            # 车辆介绍信息
            if ch.xpath('//*[@id="gallery"]/div[1]/div[1]/div[2]/div/p/text()'):
                car_data['car_msg'] = ch.xpath('//*[@id="gallery"]/div[1]/div[1]/div[2]/div/p/text()').extract()[0]
            # 车辆详情图片
            if ch.xpath('//*[@id="gallery"]/div[1]/div[@class="detail-car-appearance"]/div[2]/div/img/@data-src'):
                car_data['car_imgs'] = ch.xpath(
                    '//*[@id="gallery"]/div[1]/div[@class="detail-car-appearance"]/div[2]/div/img/@data-src').extract()

            item['car_id'] = response.meta.get('car_id')
            item['car_data'] = car_data
        except:
            pass

        yield item




