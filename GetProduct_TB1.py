import time
import pymssql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class taobao_Scrapy:
    def __init__(self):
        self.url = 'https://login.taobao.com/member/login.jhtml'
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # 不加载图片
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  #切为开发者模式
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.db = pymssql.connect(host='127.0.0.1', user='sa', password='654321', port='1433', database='A2_Milk_Powder1', charset="utf8")
        self.cursor = self.db.cursor()
        self.weibo_username = "582473541@qq.com"  # 你的微博账号
        self.weibo_password = "lin19950902"  # 你的微博密码
        self.key = 'a2奶粉'

    def login(self):
        self.driver.get(self.url)
        # 等待 密码登录选项 出现
        password_login = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
        password_login.click()
        # 等待 微博登录选项 出现
        weibo_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
        weibo_login.click()
        # 等待 微博账号 出现
        weibo_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.username > .W_input')))
        weibo_user.send_keys(self.weibo_username)
        # 等待 微博密码 出现
        weibo_pwd = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.password > .W_input')))
        weibo_pwd.send_keys(self.weibo_password)
        # 等待 登录按钮 出现
        submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_tip > a > span')))
        submit.click()
        # 直到获取到淘宝会员昵称才能确定是登录成功
        taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
            '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
        # 输出淘宝昵称
        print(taobao_name.text)

    def send_key(self):
        self.driver.find_element_by_xpath('//*[@id="q"]').click()
        self.driver.find_element_by_xpath('//*[@id="q"]').send_keys(self.key)
        self.driver.find_element_by_xpath('//*[@id="J_TSearchForm"]/div[1]/button').click()

    def get_products(self):
        sale_num = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, '//div[@class="deal-cnt"]')))
        sale_num = [items.text.replace("人付款", "") for items in sale_num]
        price = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, "//div[contains(@class,'row-1')]/div[1]/strong")))
        price = [items.text for items in price]
        product_name = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, "//div[contains(@class,'row-2')]/a")))
        product_name = [items.text for items in product_name]
        trace_price = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, "//div[contains(@class,'ctx-box')]/div[2]/a")))
        trace_price = [items.get_attribute('trace-price') for items in trace_price]
        product_url = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, "//div[contains(@class,'ctx-box')]/div[2]/a")))
        product_url = [items.get_attribute('href') for items in product_url]
        shop_url = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, '//a[contains(@class,"shopname")]')))
        shop_url = [items.get_attribute('href') for items in shop_url]
        shop_name = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, '//a[contains(@class,"shopname")]/span[2]')))
        shop_name = [items.text for items in shop_name]
        shop_address = self.wait.until(EC.presence_of_all_elements_located(\
            (By.XPATH, '//div[@class="location"]')))
        shop_address = [items.text for items in shop_address]
        self.product = zip(sale_num, price, product_name, trace_price, product_url, shop_url, shop_name, shop_address)
        # for i in list(self.product):
        #     print(i)

    def turn_page(self, i):
        input = tb.driver.find_element_by_xpath('//*[@id="mainsrp-pager"]/div/div/div/div[2]/input')
        input.clear()
        input.send_keys(str(i))
        send = self.wait.until(EC.element_to_be_clickable(\
            (By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/div[2]/span[3]')))
        send.send_keys(str(i))
        summit = self.wait.until(EC.element_to_be_clickable(\
            (By.XPATH, '//*[@id="mainsrp-pager"]/div/div/div/div[2]/span[3]')))
        summit.click()
        time.sleep(2)

    def save_database_outter(self):
        print("入库开始")
        for i in list(self.product):
            sql = 'insert into TBData_outter1(sale_num, price, product_name, trace_price, product_url, shop_url, shop_name, shop_address)\
                  values(%s,%s,%s,%s,%s,%s,%s,%s)'
            try:
                self.cursor.execute(sql, (str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]), str(i[5]), str(i[6]), str(i[7])))
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                print("入库失败", e)

    def main(self):
        self.login()
        self.send_key()
        for i in range(1, 101):
            if i == 10:
                time.sleep(20)
            self.turn_page(i)
            self.get_products()
            time.sleep(2)
            print("第"+str(i)+"页爬虫")
            self.save_database_outter()
        print("爬虫完成")
        self.db.close()

    def request_url(self):
        sql = 'select id,product_url from TBData_outter'
        self.cursor.execute(sql)
        self.result = self.cursor.fetchall()
        for i in self.result:
            print(i)
        self.driver.get('https://detail.tmall.com/item.htm?id=520043988609&ns=1&abbucket=13')
# chromedriver_path = r'D:\UserData\Administrator\Downloads\chromedriver.exe'  # 改成你的chromedriver的完整路径地址


if __name__ == '__main__':
    tb = taobao_Scrapy()
    # tb.main()
    tb.request_url()
