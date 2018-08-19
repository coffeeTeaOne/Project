import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# 设置驱动位置
chromdriver = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'

# 模拟哪个浏览器行为
browser = webdriver.Chrome(chromdriver)

# 打开url地址
browser.get('https://www.guazi.com/cd/buy/o6/')

# 拿去a标签的集合(非页面,属于a标签对象集合)
lis = browser.find_elements_by_xpath('/html/body/div[4]/ul/li')

# 这里的lis是以个对象集合,可以拿去这个对象里面的任何东西
# 1,拿值:i.text
# 2,拿属性的值:get_attribute('任意属性名')

for i in lis:
    title = i.find_element_by_css_selector('a').text
    img = i.find_element_by_css_selector('a img').get_attribute('src')
    trip = i.find_element_by_class_name('t-i').text
    price  =i.find_element_by_css_selector('.t-price p').text
    print(title,img,trip,price)

# 关闭
browser.close()