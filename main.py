import ipdb
import requests
from bs4 import BeautifulSoup
import time
import re


class crawler:
    def __init__(self):
        super(crawler, self).__init__()
        self.root_url = "https://www.ptt.cc"
        self.init_url = "https://www.ptt.cc/bbs/Beauty/index.html"
        self.header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q = 0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-ncoding': 'gzip,deflate,br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://www.ptt.cc/ask/over18?from=%2Fbbs%2FBeauty%2Findex3428.html',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user - agent': 'Mozilla/5.0 (X11; Linuxx86_64) AppleWebKit/537.36(KHTML,likeGecko) Chrome/85.0.4183.102Safari/537.36'
        }
        self.cur_url = self.init_url
        self.payload = {
            'from': self.cur_url,
            'yes': 'yes'
        }
        self.first_visit = True
        self.not_found = True
        self.all_articles = []
        self.all_popular = []
        self.tic = time.time()

    def find_first_page(self):
        """
        target of the function is to find out the starting page when the date is 2018/12/31
        as the starting point where we should start recording the articles
        :return:
            changing self.cur_url to the desired page
        :time required:
            76.79 (sec) for recursive method
            73.11 (sec) for iterative method
        """
        while (self.not_found):
            time.sleep(0.1)
            rs = requests.session()
            req = rs.post("https://www.ptt.cc/ask/over18", data=self.payload)
            req = rs.get(self.cur_url)
            req = req.text
            self.cur_soup = BeautifulSoup(req, 'html.parser')
            date = self.cur_soup.find("div", class_="date").text
            interval = 5
            if date == "12/31" and self.first_visit == True:
                self.end_url = self.cur_url
                self.prev_page(300)
                self.first_visit = False
                # self.find_first_page()
            elif date == "12/31" and self.first_visit == False:
                self.not_found = False
                # self.crawl_remain()
            else:
                if re.match(" 1/+[0-5]", date):
                    interval = 0
                self.prev_page(interval)
                # self.find_first_page()

    """def crawl_remain(self):
        self.toc = time.time()
        ipdb.set_trace()"""

    def prev_page(self, interval):
        btn_list = self.cur_soup.find_all("a", class_="btn wide")
        for btn in btn_list:
            if btn.get_text() == "‹ 上頁":
                prev_page = btn.get("href")
                prev_page = prev_page.split(".")
                index = prev_page[len(prev_page) - 2]
                index = index[17:]
                index = int(index) - interval
                url = "/bbs/Beauty/index" + str(index) + ".html"
                self.cur_url = self.root_url + url

    def next_page(self):
        btn_list = self.cur_soup.find_all("a", class_="btn wide")
        for btn in btn_list:
            if btn.get_text() == "下頁 ›":
                self.cur_url = self.root_url + btn.get("href")

    def crawl(self, phase):
        time.sleep(0.1)
        rs = requests.session()
        req = rs.post("https://www.ptt.cc/ask/over18", data=self.payload)
        req = rs.get(self.cur_url)
        req = req.text
        self.cur_soup = BeautifulSoup(req, 'html.parser')
        section = []
        if phase == "start":
            for presection in self.cur_soup.find_all('div', class_="r-ent"):
                if presection.find("div", class_="date").text == " 1/01":
                    section.append(presection)
        elif phase == "end":
            for presection in self.cur_soup.find_all('div', class_="r-ent"):
                if presection.find("div", class_="date").text == "12/31":
                    section.append(presection)
        else:
            section = self.cur_soup.find_all('div', class_="r-ent")
        for sec in section:
            title = sec.find("div", class_="title")
            title = title.find("a")
            if title:  # filter out the deleted posts
                date = sec.find("div", class_="date").text
                date = date.split("/")
                date = date[0] + date[1]
                popular = sec.find("div", class_="nrec")
                if popular.find("span"):
                    popular = popular.find("span").text
                    print(popular)
                else:
                    popular = "0"
                title_string = title.get_text()
                href = self.root_url+title.get("href")
                if title_string.find("[公告]") != -1:
                    print(title_string)
                else:
                    self.all_articles.append(date + "," + title_string + "," + href)
                    if popular == "爆":
                        self.all_popular.append(date + "," + title_string + "," + href)
        self.next_page()



if __name__ == '__main__':
    ### deal with input data parsing here
    c = crawler()
    c.find_first_page()
    toc_1 = time.time()
    c.crawl(phase="start")
    while c.cur_url != c.end_url:
        c.crawl(phase="normal")
    c.crawl(phase="end")
    toc_2 = time.time()
    ipdb.set_trace()
    outputfile = open("all_articles.txt", "w")
    for item in c.all_articles:
        outputfile.write(item + "\n")
    outputfile.close()
    outputfile = open("all_popular.txt", "w")
    for item in c.all_popular:
        outputfile.write(item + "\n")
    outputfile.close()
