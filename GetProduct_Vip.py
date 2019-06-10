import csv

import pymssql
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time


class VipScript():
    def __init__(self):
        self.chrome_options1 = webdriver.ChromeOptions()
        self.chrome_options1.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options1)
        self.wait = WebDriverWait(self.browser, 10)
        self.find_key = 'A2奶粉'
        self.browser.implicitly_wait(10)

    def chrome_start(self):
        self.data = zip()
        self.isLast = True

    def parse_page(self):
        try:
            url = self.wait.until(EC.presence_of_all_elements_located \
                        ((By.XPATH,'//div[@class="goods-image"]/a')))
            url = [i.get_attribute('href') for i in url]
            sale_name = self.wait.until(EC.presence_of_all_elements_located \
                        ((By.XPATH,'//h4[contains(@class,"goods-info")]/a')))
            sale_name = [i.get_attribute('title') for i in sale_name]
            promotions_price = self.wait.until(EC.presence_of_all_elements_located \
                         ((By.XPATH,'//div[@class="goods-vipshop-discount"]/span[2]/del')))
            promotions_price = [i.text.replace("¥", "") for i in promotions_price]
            promotions_discount = self.wait.until(EC.presence_of_all_elements_located \
                         ((By.XPATH,'//div[@class="goods-vipshop-discount"]/span[2]')))
            promotions_discount = [i.text.replace("折","")[-3:] for i in promotions_discount]
            inner_exclusive_price = self.wait.until(EC.presence_of_all_elements_located \
                          ((By.XPATH,'//span[@class="inner-exclusive "]/span')))
            inner_exclusive_price = [i.text for i in inner_exclusive_price]
            sells_price = self.wait.until(EC.presence_of_all_elements_located \
                          ((By.XPATH,'//em[@class="goods-sells-price "]/span[@class="price"]')))
            sells_price = [i.text for i in sells_price]
            small_price = self.wait.until(EC.presence_of_all_elements_located \
                            ((By.XPATH,'//div[contains(@class,"goods-inner")]/div[3]/del')))
            small_price = [i.text.replace("¥", "") for i in small_price]
            vip_discount = self.wait.until(EC.presence_of_all_elements_located \
                          ((By.XPATH,'//div[contains(@class,"goods-inner")]/div[3]/span')))
            vip_discount = [i.text.replace("折", "") for i in vip_discount]
            vip_price = self.wait.until(EC.presence_of_all_elements_located \
                        ((By.XPATH, "//div[@class='goods-vipshop-discount']/span[1]")))
            vip_price = [i.text for i in vip_price]
            self.data = zip(url, sale_name, promotions_price, promotions_discount, inner_exclusive_price, sells_price, small_price, vip_discount, vip_price)
        except selenium.common.exceptions.TimeoutException:
            print('parse_page: TimeoutException')
            self.parse_page()
        except selenium.common.exceptions.StaleElementReferenceException:
            print('parase_page: StaleElementReferenceException')
            self.browser.refresh()

    def turn_page(self):
        self.isLast = False
        pass

    def close_browser(self):
        self.browser.quit()

    def write_to_file(self):
        self.fd = open('Vip.csv', 'w', encoding='utf-8', newline='')
        writer = csv.writer(self.fd)
        for item in self.data:
            writer.writerow(item)

    def save_datahub(self):
        print("入库开始")
        dbs = pymssql.connect(host='127.0.0.1', user='sa', password='654321', port='1433', database='A2_Milk_Powder1', charset="utf8")
        cursor = dbs.cursor()
        for item in list(self.data):
            sql = 'insert into [dbo].[VipData_outter2]\
                            (url, sale_name, promotions_price, promotions_discount, inner_exclusive_price, sells_price, small_price,\
                            vip_discount,vip_price) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            print(item)
            try:
                # data = str(item[0]), str(item[1]), str(item[2]), str(item[3]), str(item[4]), str(item[5]),str(item[6]),str(item[7]), str(item[8])
                cursor.execute(sql, (str(item[0]), str(item[1]), str(item[2]), str(item[3]), str(item[4]), str(item[5]) ,str(item[6]), str(item[7]), str(item[8])))
                dbs.commit()
            except:
                dbs.rollback()

        dbs.close()
        print("数据库入库成功")

    def crawl(self):
        self.chrome_start()
        print('开始爬取')
        self.url = 'https://category.vip.com/suggest.php?keyword='+str(self.find_key)+'&ff=235|12|1|1'
        html = self.browser.get(self.url)
        time.sleep(1)
        js = "var q=document.documentElement.scrollTop=10000"
        self.browser.execute_script(js)  # 把页面滑动到最下方
        time.sleep(2)
        count = 0
        while self.isLast:
            count += 1
            print('所在页数:' + str(count) +'页')
            self.parse_page()
            self.save_datahub()
            # print(self.browser.page_source)
            self.turn_page()
        print('爬虫结束')
        # print(self.data))
        self.close_browser()
        # self.write_to_file()

        # 循环获取数据库id以及url

    def get_url_data(self):
        print("取库读信息开始")
        db = pymssql.connect(host='localhost', user='sa', password='654321', port='1433',
                             database='A2_Milk_Powder1', charset='utf8')
        cursor = db.cursor()
        sql = 'select id,url from VipData_outter2 '
        try:
            cursor.execute(sql)
            self.result = cursor.fetchall()
        except:
            print("数据库读取问题")

    # 根据url获取跳转页的详情块
    def get_inner_data(self):
        self.get_url_data()
        self.chrome_start()
        for item in self.result:
            id = item[0]
            url = item[1]
            print(url, id)
            self.browser.get(url)
            # print(self.browser.page_source)
            time.sleep(1)
            comment_num = self.wait.until(EC.presence_of_all_elements_located( \
                (By.XPATH, '//i[@class="J-detail-commentCnt-count"]')))
            comment_num = [item.text for item in comment_num]
            second_data = self.wait.until(EC.presence_of_all_elements_located( \
                (By.XPATH, '//table[contains(@class,"dc-table")]')))
            second_data = [item.text for item in second_data]
            promote_activity = self.wait.until(EC.presence_of_all_elements_located( \
                (By.XPATH, '//div[contains(@class,"pmsContent")]')))
            promote_activity = [item.text for item in promote_activity]
            print(comment_num,second_data, promote_activity)

            # 将查询到的对应商品的详细信息存入数据库根据id
            db = pymssql.connect(host='localhost', user='sa', password='654321', port='1433',
                                 database='A2_Milk_Powder1', charset='utf8')
            cursor = db.cursor()
            sql = 'insert into   VipData_inner2(id,comment_num, second_data, promote_activity)  values(%s,%s,%s,%s)'
            try:
                cursor.execute(sql, (int(id), str(comment_num[0]), str(second_data[0]), str(promote_activity[0])))
                db.commit()
            except:
                print("详细信息插入失败")
                db.rollback()
        db.close()
        print("存储完成")
        self.close_browser()


if __name__ == '__main__':
    tvs = VipScript()
    tvs.crawl()
    # tvs.get_inner_data()
