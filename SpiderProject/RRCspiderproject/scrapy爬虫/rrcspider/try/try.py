from urllib.request import Request,urlopen

from bs4 import BeautifulSoup


def get_data(url):

    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/65.0.3325.181 Safari/537.36'}

    req = Request(url=url,headers=header)
    re = urlopen(req)
    # res = re.read().decode('utf-8')

    soup = BeautifulSoup(re.text, 'lxml')

if __name__ == '__main__':
    url = 'https://www.guazi.com/cd/buy/o6/'
    get_data(url)





