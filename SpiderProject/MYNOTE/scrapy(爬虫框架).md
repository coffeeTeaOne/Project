#### scrapy(爬虫框架)

##### 1,安装

~~~
pip install pywin32(安装完成后才能安装scrapy)
pip install Scrapy

在安装过程是有可能会提示:Twisted是安装失败的,这就要在官网下载源文件,安装,
pip install Twisted-18.4.0-cp36-cp36m-win32.whl
在安装scrapy

下载的安装包安装方式(进入相应文件夹下面):
python setup.py install
或者
pip install Scrapy
~~~

##### 2,项目创建

~~~
scrapy startproject name
~~~

##### 3,项目运行

~~~
文件结构组成:
scrapy.cfg:项目的配置信息，主要为Scrapy命令行工具提供一个基础的配置信息。（真正爬虫相关的配置信息在settings.py文件中）
items.py:设置数据存储模板，用于结构化数据，如：Django的Model
pipelines:数据处理行为，如：一般结构化的数据持久化
settings.py:配置文件，如：递归的层数、并发数，延迟下载等
spiders:爬虫目录，如：创建文件，编写爬虫规则。
在spiders文件中创建爬虫的时候，一般以爬取的网站的域名为爬虫的名称
~~~



~~~python
整个项目运行结构:
	1.1,首先在settings里面,找到运行的项目和user_agent等用作项目运行时的准备条件;
	BOT_NAME = 'weibospider'
	SPIDER_MODULES = ['weibospider.spiders']
	NEWSPIDER_MODULE = 'weibospider.spiders'
	USER_AGENT
	1.2,item.py,相当于Django的模型;
	1.3,进入到自定义的页面weibo,qidian,douban等,这里面创建爬虫,将数据从页面或是api接口上获取出来,存入到一个字典中,这里的字典一般处理为
	user_item = UserItem()(这里是在items创建的模型对象),
	1.4,如果我们获取的不止一个页面或是api接口,这里的处理方式有很多种	
~~~

##### 多页面获取方式

~~~python
页面处理方式:
		1.4.1,如果页面采用如下方式:
		"https://movie.douban.com/top250?start=" + num_str + "&filter="
		num_str可以循环自加处理,并把每一次得到的url存入到start_urls列表中,后面再页面解析获取数据时,它会自动去获取每一个页面的数据,并存储;
		1.4.2,主页面url='https://movie.douban.com/top250'
		  子页面:
				第二页:"?start=25&amp;filter="
				第三页:"?start=50"
				第四页:"?start=75"
		这种url在点击访问时,会自动拼接主页面的url,所以我们在处理这种情况时,可以采用自动匹配模式;
		方法:
		导入相关模块
			from scrapy.linkextractors import LinkExtractor
			from scrapy.spider import Rule,CrawlSpider
			from scrapy.selector import Selector
			class DoubanSpider(CrawlSpider):
			name = "douban"
			start_urls = {'https://movie.douban.com/top250',}
			# 这里的parse_item连接的是下面数据处理的函数,一般是parse(重写这个函数),但这里由于调用层级问题,不能使用这个名字
			rules = {Rule(LinkExtractor(allow=r'https://movie.douban.com/top250.*'),callback='parse_item'),}
~~~

#### 多个api接口处理

~~~python
1.4.3,api接口数据处理模式
		多接口数据处理模式:
			寻找api接口url的不同点和无效数据;
			https://m.weibo.cn/api/container/getIndex?uid=1730077315&containerid=1005051730077315
			有用数据两条:uid和containerid
			不同点:uid值变化,containerid的后几位是有uid组成,所以也会发生变化(前面6位表示个人用户,微博,主页等)

			代码结构:
			name = "gaoyy2"	    
		    user_url= 'https://m.weibo.cn/api/container/getIndex?uid={uid}&containerid=100505{uid}'
		    start_user_uids = ['1730077315','1840274303','1644461042']
		    
		    def start_requests(self):
		        for uid in self.start_user_uids:
		            yield Request(self.user_url.format(uid=uid), callback=self.parse)

		    用户url,这里的{uid}与format格式化用法需注意,def下面生成器使用原理
~~~

#####利用生成器返回

~~~python
通过parse_user我们生成了博主的部分信息,这些信息存储到user_item字典里面(后面利用该字典存储到mongodb数据库中),这里的parse_user函数返回3个对象:

1,第一个返回user的用户信息,用于数据持久化;
yield user_item

2,第二个,用来解析博主关注的人(类似一对多处理,拿博主id);
# 这里的Request(url,callback,meta),url:继续访问的地址; callback:执行的函数; meta:response里面带的参数(下面有所需要的)
yield Request(self.follow_url.format(uid=user_item.get('id'),
page=1),callback=self.parse_follows,meta={'page': 1, 'uid': user_item.get('id')})

3,第三个,利用博主的id来解析他的fans,和第二个原理一样;
yield Request(self.fans_url.format(uid=user_item.get('id'),
since_id=1),callback=self.parse_fans,meta={'since_id': 1, 'uid': user_item.get('id')})

总结:
这里需注意Request(url,callback,meta)的用法:
1,利用博主的部分信息(id,用于格式化fans和关注的人的api接口url),解析相关的api接口信息;

2,这里的format用法:
url的处理(花括号):url='https://m.weibo.cn/api/container/getIndex?uid={uid}&containerid=100505{uid}
url的格式化:new_url = url.format(uid=user_item.get('id'))
    
3,callback参数:这个参数是用于处理访问url接口信息(response)的处理,主要是有效数据的获取(数据采集),这里是调用一个数据处理的函数,调用方式:
   callback=self.parse_follows
(这里的函数名是parse_follows,class里面调用需加self)

4,meta参数的插入:用于接口数据处理后,需要进行递归处理时,将再次使用这些参数(这里主要指uid和page,这两个参数都会用于改变api接口的url),在parse_follows后面处理这两个参数时,需根据api接口的url改变的一定规律来进行变化,再将这些值传入url中,然后Request--->数据处理等递归操作;
    
5,yield的使用:
 这里不能使用return来返回数据对象,return只能返回一个数据对象且程序会终止,yield可以在函数内或是程序中的任意位置返回任意数据对象(scrapy框架里面会自动处理yield返回数据进行持久化处理,完成后再返回到这个程序中,返回到程序这个过程是自动处理的所以这个没有send或next的操作),程序不会终止,继续进行下一步操作,所遇到的yield都是如上操作.这里的逻辑顺序相当于就是:先拿去博主及相关数据信息-->该信息数据持久化(数据库存储)-->返回程序中-->进行下一步操作(获取关注的人)(获取fans),这里需注意的一点是:关注的人和fans是并发执行的,可以说没有先后顺序;
~~~

##### weibo.py

~~~python
这个文件里需要注意的点:
1,格式:
class WeiBoSpider(Spider):
    name = "hello"  
    user_url= '/'
    follow_url ='/'
    fans_url = '/'
    
    def parse_user(self):
    	yield user_item
    	yield Request(self.follow_url.format(uid=user_item.get('id'),
    	 page=1),callback=self.parse_follows,meta={'page': 1, 'uid': user_item.get('id')})
        yield Request(self.fans_url.format(uid=user_item.get('id'),
        since_id=1),callback=self.parse_fans,meta={'since_id': 1, 'uid': user_item.get('id')})
        
    def parse_follows(self, response):
        yield user_relation_item
        yield
    
    def parse_fans(self, response):
    	yield user_fans_item
        yield
    
2,在api接口取数据的时候,最好使用res.get('data'),不要使用res['data'],如果是data是空值,这样的方式容易报错,爬虫不能继续,get不会报错;
3,接口数据转换为自己爬取数据(部分数据)方式;
 user_params = {'id': 'id','screen_name': 'screen_name'}
 for k, v in user_params.items():
     user_item[k] = user_info[v]
 这里的user_info是接口数据的json对象下面的一个字典;
4,format格式应用;
5,response响应,response.text是json字符集响应对象;
6,from scrapy import Request,Request(url,callback,meta)的用法;
7,采集数据序列化
 user_relation_item = UserRelationItem()
 follower_list = [{'id': follower.get('user').get('id'), 'name':  follower.get('user').get('screen_name')} for follower in followers]
            user_relation_item['id'] = uid
            user_relation_item['follower'] = follower_list
 yield user_relation_item
8,调用meta里面的参数:uid = response.meta.get('uid')
~~~

##### settings配置

~~~
BOT_NAME = 'weibospider'

SPIDER_MODULES = ['weibospider.spiders']
NEWSPIDER_MODULE = 'weibospider.spiders'
USER_AGENT = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36'
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'weibospider.pipelines.UserCreateTimePipeline': 300,
    # 'weibospider.pipelines.WeibospiderPipeline': 301,
    'weibospider.pipelines.WeiboPymongoPipeline': 302,
}

MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_DB = 'weibo'
# MONGODB_COLLECTION = 'gaoyy'
~~~

##### pipelines.py

~~~
数据持久化(保存数据库)
格式:
class WeiboPymongoPipeline(object):
       # 数据连接通道,和数据存储数据库
    def __init__(self):
        self.MONGODB_HOST = settings['MONGODB_HOST']
        self.MONGODB_PORT = settings['MONGODB_PORT']
        self.MONGODB_DB = settings['MONGODB_DB']
        conn = pymongo.MongoClient(host=self.MONGODB_HOST, port=self.MONGODB_PORT)
        db = conn[self.MONGODB_DB]
        self.collections = db[UserItem.collections]
        # 数据保存
	def process_item(self, item, spider):
		self.collections.update({'id': item['id']},{'$set':item}, True)
		self.collections.insert(dict(item))
	   # 数据库里子库创建,$addToSet,$each固定用法
	    self.collections.update(
               {'id': item['id']},
               {'$addToSet': {
                   'follower': {'$each': item['follower']}
               }},
               True
           )
~~~

items.py

~~~
这里相当于django中的模型
class UserItem(scrapy.Item):
    # 这里的collections的值是在数据库里命名的表名,在piplines会调用,
    # 数据库的表名也可以在settings里面生成,生成方式比较灵活.
    collections = 'myusers'
    # 结构化数据
    id = scrapy.Field()
    screen_name = scrapy.Field()
    profile_image_url = scrapy.Field()

~~~
