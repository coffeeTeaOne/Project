from json import loads

from scrapy import Request
from scrapy.selector import Selector
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider


from ljspider.items import LjspiderItem


class LjSpider(RedisSpider):
    name = 'lian'

    redis_key = 'lian:start_urls'


    def parse(self, response):
        res = Selector(response)
        #  这里获取的是li对象的集合,注意后面不能加.extract()
        lis = res.xpath('/html/body/div[4]/div[1]/ul/li[@class="clear"]')
        item = LjspiderItem()
        # extract()[0]存储是直接存数据,不加[0],存的是一个目录,然后下面才是数据
        for li in lis:
            try:
                # 获取属性方式:@data-housecode
                item['id'] = li.xpath('./a/@data-housecode').extract()[0]
                item['img_src'] = li.xpath('./a/img/@data-original').extract()[0]
                # 获取文本方式text()
                item['title'] = li.xpath('./div/div/a/text()').extract()[0]
                item['address'] = li.xpath('./div/div[2]/div/a/text()').extract()[0]
                info = li.xpath('./div/div[2]/div/text()').extract()[0]
                msgs = self.slit_house_info(info)
                item['house_model'] = msgs[0]
                item['acreage'] = msgs[1]
                item['towards'] = msgs[2]
                item['decorate'] = msgs[3]
                item['lift'] = msgs[4]

                item['flood'] = li.xpath('./div/div[3]/div/text()').extract()
                # 获取class="priceInfo"属性的div,这里注意加[]
                item['all_money'] = li.xpath('./div/div[@class="priceInfo"]/div/span/text()').extract()
                item['single_money'] = li.xpath('./div/div[@class="priceInfo"]/div[2]/span/text()').extract()
                item['flood'] = li.xpath('./div/div[3]/div/text()').extract()
                item['tag'] = li.xpath('.//div[@class="tag"]/span/text()').extract()
                item['type'] = '二手房'
                item['city'] = '成都'
                item['area'] = response.meta.get('area_name')
            except:
                pass
            finally:
                # 每一次只能生成一组item,并返回,数据持久化,所以这里只能使用yield,return只能返回一次
                yield item

    def slit_house_info(self,info):
        return [i.strip() for i in info.split('|')[1:]]


