import pymssql
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time


class KaolaScrapy():
    def __init__(self):
        self.chrome_options1 = webdriver.ChromeOptions()
        self.chrome_options1.add_argument('--headless')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options1)
        self.wait = WebDriverWait(self.browser, 10)
        self.browser.implicitly_wait(10)
        self.db = pymssql.connect(host='localhost', user='sa', password='654321', port='1433',
                             database='A2_Milk_Powder1', charset='utf8')
        self.cursor = self.db.cursor()


    def varnity(self):
        self.data = zip()
        self.isLase = True

    def turn_page(self):
        self.isLase=False

    def parse_page(self):
        try:
            url = self.wait.until(EC.presence_of_all_elements_located \
                    ((By.XPATH, '//li[@class="goods"]/div/a')))
            url = [item.get_attribute('href') for item in url]
            curents_price = self.wait.until(EC.presence_of_all_elements_located \
                    ((By.XPATH, "//li[@class='goods']/div/div/p[1]/span[1]")))
            curents_price = [item.text.replace("预定价¥", "").replace("¥", "") for item in curents_price]
            memberprice = self.wait.until(EC.presence_of_all_elements_located \
                ((By.XPATH, "//p[@class='price']/span[2]")))
            memberprice = [item.text.replace("考拉价¥", "").replace("会员价 ¥", "").replace("¥", "") for item in memberprice]
            title = self.wait.until(EC.presence_of_all_elements_located \
                ((By.XPATH, "//li[@class='goods']/div/div/div/a")))
            title = [item.get_attribute('title') for item in title]
            comment_num = self.wait.until(EC.presence_of_all_elements_located \
                ((By.XPATH, "//li[@class='goods']/div/div/p[3]/a")))
            comment_num = [item.text for item in comment_num]
            address = self.wait.until(EC.presence_of_all_elements_located \
                ((By.XPATH, "//li[@class='goods']/div/div/p[3]/span")))
            address = [item.text for item in address]
            sale_shop = self.wait.until(EC.presence_of_all_elements_located \
                ((By.XPATH, "//li[@class='goods']/div/div/p[4]/span")))
            sale_shop = [item.text for item in sale_shop]
            self.data = zip(url, curents_price, memberprice, title, comment_num, address, sale_shop)
            # for i in list(self.data):
            #     print(str(i))


        except selenium.common.exceptions.TimeoutException:
            print('parse_page: TimeoutException')
            self.parse_page()
        except selenium.common.exceptions.StaleElementReferenceException:
            print('parse_page: StaleElementReferenceException')
            self.browser.refresh()

    def save_database_outter(self):
        print("入库开始")
        sql = 'insert into [dbo].[KLData_outter1]\
                    (url, curents_price, memberprice, title, comment_num, address, sale_shop) values(%s,%s,%s,%s,%s,%s,%s)'
        for it in list(self.data):
            print(it[0], it[1], it[2], it[3], it[4], it[5], it[6])
            try:
            # for it in list(self.data):
                self.cursor.execute(sql, (it[0], it[1], int(it[2]), it[3], int(it[4]), it[5], it[6]))
                self.db.commit()
            except:
                print("插入失败")
                self.db.rollback()
        self.db.close
        print("入库成功")

    def request_database_outter(self):
        self.varnity()
        sql = 'select id,url from KLData_outter1 where id between 1 and 44'
        try:
            self.cursor.execute(sql)
            self.result = self.cursor.fetchall()
        except:
            print("数据读取出问题")

    def save_database_inner(self, id, product_details, goodPercent, commWithImg, tax, activuty, offer):
        self.request_database_outter()
        sql = 'insert into KLData_inner1(id, product_details, goodPercent, commWithImg, tax, activuty, offer) values(%s,%s,%s,%s,%s,%s,%s)'
        print(id, product_details, goodPercent, commWithImg, tax, activuty, offer)
        try:
            self.cursor.execute(sql, (int(id), str(product_details), str(goodPercent), str(commWithImg), str(tax), str(activuty), str(offer)))
            self.db.commit()
            print("入库成功")
        except Exception as e:
            print(e)
            self.db.rollback()

    def is_element(self, identify, c):
        try:
            if identify == "id":
                self.browser.find_element_by_id(c)
            elif identify == "xpath":
                self.browser.find_element_by_xpath(c)
            elif identify == "class":
                self.browser.find_element_by_class_name(c)
            elif identify == "link text":
                self.browser.find_element_by_link_text(c)
            elif identify == "partial link text":
                self.browser.find_element_by_partial_link_text(c)
            elif identify == "name":
                self.browser.find_element_by_name(c)
            elif identify == "tag name":
                self.browser.find_element_by_tag_name(c)
            elif identify == "css selector":
                self.browser.find_element_by_css_selector(c)
            return self.wait.until(EC.presence_of_all_elements_located( \
                (By.XPATH, c)))
        except Exception as e:
            return ""


    def parse_inner_page(self):
        self.request_database_outter()
        for i in self.result:
            id = i[0]
            url = i[1]
            self.browser.get(url)
            time.sleep(1)

            product_details = self.is_element("xpath", "//ul[@class='goods_parameter']")
            product_details = [item.text.replace("\n", ";") for item in product_details]
            goodPercent = self.is_element("xpath", "//span[@class='goodPercent']")
            goodPercent = [item.text for item in goodPercent]
            commWithImg = self.is_element("xpath", "//span[contains(@class,'commWithImg')]/a")
            commWithImg = [item.text for item in commWithImg]
            tax = self.is_element("xpath", "//div[contains(@class,'taxmsg')]/b")
            tax = [item.text for item in tax]
            activuty = self.is_element("xpath", "//div[contains(@class,'promotionwrap')]")
            activuty = [item.text for item in activuty]
            offer = self.is_element("xpath", "//span[@class='vtxt']/i")
            offer = [item.text for item in offer]
            # self.data = zip(product_details, goodPercent, commWithImg, tax, activuty, offer)
            print(url)
            self.save_database_inner(id, product_details, goodPercent, commWithImg, tax, activuty, offer)

    def close_browser(self):
        self.browser.quit()

    def crawl(self):
        self.varnity()
        print("开始爬虫")
        self.url = 'https://search.kaola.com/search.html?zn=top&key=a2%25E5%25A5%25B6%25E7%25B2%2589&searchRefer=searchbutton&oldQuery=a2%25E5%25A5%25B6%25E7%25B2%2589&timestamp=1559612082872&hcAntiCheatSwitch=0&anstipamActiCheatSwitch=1&anstipamActiCheatToken=ee7b2ce7910f4e04ac89bbdae1871d04&anstipamActiCheatValidate=anstipam_acti_default_validate'
        html = self.browser.get(self.url)
        time.sleep(1)
        for num in range(1000, 10000, 100):
            js = "var q=document.documentElement.scrollTop="+str(num)
            self.browser.execute_script(js)
        time.sleep(4)
        count = 0
        while self.isLase:
            count += 1
            print("所在页数:" + str(count) + "页")
            self.parse_page()
            self.save_database_outter()
            self.turn_page()
        print("爬虫结束")
        self.close_browser()


if __name__ == '__main__':
    ks = KaolaScrapy()
    # ks.crawl()
    ks.parse_inner_page()