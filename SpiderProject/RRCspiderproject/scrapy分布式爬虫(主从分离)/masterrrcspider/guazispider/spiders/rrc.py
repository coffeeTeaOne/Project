from scrapy import Selector, Request
from scrapy.spiders import Spider
from guazispider.items import RrcSpider, CarMsgSpider, MasterRedisItem


class GuaZiSpider(Spider):
    name = 'rrc'
    #
    start_urls = ['https://www.renrenche.com/cd/',]  # 按成都筛选
    main_url = 'https://www.renrenche.com/cd/{brand}/p{page}/'  # 基本url

    # 车型选型
    def parse(self, response):
        ca = Selector(response)
        a_list = ca.xpath('//*[@id="brand_more_content"]/div/p/span/a')
        if a_list:
            try:
                for a in a_list:
                    car_href = a.xpath('./@href').extract()[0].split('/')[-2]
                    # 将生成的url,返回到redis缓存
                    car_url = self.main_url.format(brand=car_href, page=1)
                    # 函数回调,生成新的url

                    yield Request(car_url, callback=self.parse_page, meta={'car_href': car_href, 'page': 1})
            except:
                pass
        else:
            pass

    def parse_page(self, response):
        pa = Selector(response)
        page = int(response.meta.get('page')) + 1

        car_href = response.meta.get('car_href')
        lis = pa.xpath('//ul[@class="row-fluid list-row js-car-list"]/li')
        # 判断lis是否为空,如果为空就超过了最大页
        if lis:
            item = MasterRedisItem()
            url = self.main_url.format(brand=car_href, page=page)
            item['url'] = url
            yield item
            # 获取所有分页,函数回调
            yield Request(url=url, callback=self.parse_page, meta={'car_href': car_href, 'page': page})

        else:
            pass



