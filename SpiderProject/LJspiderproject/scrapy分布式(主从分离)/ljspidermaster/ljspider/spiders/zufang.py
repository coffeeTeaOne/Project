from json import loads

from scrapy import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider


from ljspider.items import LjspiderItem, MasterRedisItem


class LjSpider(Spider):
    name = 'lian'
    # allowed_domains = [] # 允许访问哪个域名下的连接
    start_urls = ['https://cd.lianjia.com/ershoufang',]
    main_url = 'https://cd.lianjia.com'

    def parse(self, response):
        sl = Selector(response)
        areas = sl.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div/a')
        for i in areas:
            area_name = i.xpath('./text()').extract()[0]
            area_url = i.xpath('./@href').extract()[0]
            yield Request(self.main_url + area_url,
                          callback=self.parse_info,
                          meta={'area_url':area_url,'area_name':area_name})

    def parse_info(self,response):
        sa = Selector(response)
        pa = sa.xpath('/html/body/div[4]/div[1]/div[8]/div[2]/div')
        page_data = pa.xpath('./@page-data').extract()[0]
        page_data_dict = loads(page_data)
        total_page = page_data_dict.get('totalPage')
        item = MasterRedisItem()
        for i in range(1,total_page+1):
            item['url'] = self.main_url + response.meta.get('area_url') + 'pg' + str(i)
            yield item





