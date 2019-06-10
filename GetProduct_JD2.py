import pymssql
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.common.exceptions
import json
import csv
import time


class JdSpider():
    # 选择接下来数据存储的方式
    def open_file(self):
        self.fm = input('请输入文件保存格式（txt、json、csv）：')
        while self.fm != 'txt' and self.fm != 'json' and self.fm != 'csv':
            self.fm = input('输入错误，请重新输入文件保存格式（txt、json、csv）：')
        if self.fm == 'txt':
            self.fd = open('Jd.txt', 'w', encoding='utf-8')
        elif self.fm == 'json':
            self.fd = open('Jd.json', 'w', encoding='utf-8')
        elif self.fm == 'csv':
            self.fd = open('Jd.csv', 'w', encoding='utf-8', newline='')

    # 初事化所用浏览器规则
    def open_browser(self):
        self.chrome_options1 = webdriver.ChromeOptions()
        self.chrome_options1.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options1)
        self.browser.implicitly_wait(10)
        self.wait = WebDriverWait(self.browser,10)

    # 初始化变量，数据变量，判断标识
    def init_variable(self):
        self.data = zip()
        self.isLast = False

    # 对于获取的某页面的解析
    def parse_page(self):
        try:
            skus = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//li[@class="gl-item"]')))
            skus = [item.get_attribute('data-sku') for item in skus]
            links = ['https://item.jd.com/{sku}.html'.format(sku=item) for item in skus]
            prices = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="gl-i-wrap"]/div[2]/strong/i')))
            prices = [item.text for item in prices]
            names = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="gl-i-wrap"]/div[3]/a/em')))
            names = [item.text for item in names]
            comments = self.wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@class="gl-i-wrap"]/div[4]/strong')))
            comments = [item.text for item in comments]
            shop_name = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="gl-i-wrap"]/div[5]/span/a')))
            shop_name = [item.text for item in shop_name]
            self.data = zip(skus,links, prices, names, comments, shop_name)
        except selenium.common.exceptions.TimeoutException:
            print('parse_page: TimeoutException')
            self.parse_page()
        except selenium.common.exceptions.StaleElementReferenceException:
            print('parse_page: StaleElementReferenceException')
            self.browser.refresh()
        print(str(self.data))

    # 对于页面翻页操作
    def turn_page(self):
        try:
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@class="pn-next"]'))).click()
            time.sleep(1)
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2)
        except selenium.common.exceptions.NoSuchElementException:
            self.isLast = True
        except selenium.common.exceptions.TimeoutException:
            print('turn_page: TimeoutException')
            self.turn_page()
        except selenium.common.exceptions.StaleElementReferenceException:
            print('turn_page: StaleElementReferenceException')
            self.browser.refresh()

    # 将数据写入对应文件类型。操作
    def write_to_file(self):
        if self.fm == 'txt':
            for item in self.data:
                self.fd.write('----------------------------------------\n')
                self.fd.write('link：' + str(item[0]) + '\n')
                self.fd.write('price：' + str(item[1]) + '\n')
                self.fd.write('name：' + str(item[2]) + '\n')
                self.fd.write('comment：' + str(item[3]) + '\n')
        if self.fm == 'json':
            temp = ('link', 'price', 'name', 'comment')
            for item in self.data:
                json.dump(dict(zip(temp, item)), self.fd, ensure_ascii=False)
        if self.fm == 'csv':
            writer = csv.writer(self.fd)
            for item in self.data:
                writer.writerow(item)

    # 关闭
    def close_file(self):
        self.fd.close()

    # 关闭浏览器对应属性
    def close_browser(self):
        self.browser.quit()

    # 数据存储入库
    def save_datahub(self):
        print("入库开始")
        dbs = pymssql.connect(host='127.0.0.1', user='sa', password='654321', port='1433', database='A2_Milk_Powder1', charset="utf8")
        cursor = dbs.cursor()
        for item in list(self.data):
            sql = 'insert into [dbo].[JDData_outter1]\
                            (skus,links, prices, names, comments, shop_name) values(%s,%s,%s,%s,%s,%s)'
            print(item)
            try:
                # data = str(item[0]), str(item[1]), str(item[2]), str(item[3]), str(item[4]), str(item[5]),str(item[6]),str(item[7]), str(item[8])
                cursor.execute(sql, (str(item[0]), str(item[1]), str(item[2]), str(item[3]), str(item[4]), str(item[5])))
                dbs.commit()
            except:
                dbs.rollback()

        dbs.close()
        print("数据库入库成功")

    # 结合上功能模块实现爬虫及分析入库
    def crawl(self):
        # self.open_file()
        self.open_browser()
        self.init_variable()
        print('开始爬取')
        self.browser.get('https://search.jd.com/Search?keyword=a2奶粉&enc=utf-8')
        time.sleep(1)
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        count = 0
        while not self.isLast:
            count += 1
            print('正在爬取第 ' + str(count) + ' 页......')
            self.parse_page()
            self.save_datahub()
            # self.write_to_file()
            self.turn_page()
        self.close_file()
        self.close_browser()
        print('结束爬取')

    # 循环获取数据库id以及url
    def get_url_data(self):
        print("取库读信息开始")
        db = pymssql.connect(host='localhost', user='sa', password='654321', port='1433', database='A2_Milk_Powder1', charset='utf8')
        cursor = db.cursor()
        sql = 'select id,links from JDData_outter1'
        try:
            cursor.execute(sql)
            self.result = cursor.fetchall()
        except:
            print("数据库读取问题")

    # 根据url获取跳转页的详情块
    def get_inner_data(self):
        self.get_url_data()
        self.open_browser()
        self.init_variable()
        for item in self.result:
            id = item[0]
            url = item[1]
            print(url, id)
            self.browser.get(url)
            # print(self.browser.page_source)
            time.sleep(1)
            second_data = self.wait.until(EC.presence_of_all_elements_located(\
                (By.XPATH,

                 '//ul[contains(@class,"parameter2")]')))
            second_data = [item.text.replace("\n", "；") for item in second_data]
            print(second_data[0])

            # 将查询到的对应商品的详细信息存入数据库根据id
            db = pymssql.connect(host='localhost', user='sa', password='654321', port='1433',
                                 database='A2_Milk_Powder1', charset='utf8')
            cursor = db.cursor()
            sql = 'insert into   JDData_innert1(id,innert_details)  values(%s,%s)  '

            try:
                cursor.execute(sql, (int(id), str(second_data[0])))
                time.sleep(1)
                db.commit()
            except:
                print("详细信息插入失败")
                db.rollback()
        db.close()
        print("存储完成")


if __name__ == '__main__':
    spider = JdSpider()
    # 1.解析商品列表网页信息
    # spider.crawl()
    # 2.解析商品详情页面信息
    spider.get_inner_data()
