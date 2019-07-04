import json
import re

import pymssql
import requests
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import selenium.common.exceptions
import time


class TMShop(object):
    def __init__(self):
        self.startTime = '2019-07-03'
        self.endTime = '2019-07-03'
        self.url = 'https://web.cbbs.tmall.com/'
        self.rootUrl = 'https://dataweb.cbbs.tmall.com/data/service/invoke.json?'
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 隐藏程序模拟浏览器
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.db = pymssql.connect(host='192.168.0.186', user='sa', password='987987abc#', port='1433',
                                  database='TopSystem_D11', charset="utf8")
        self.cursor = self.db.cursor()

    def login(self):
        # self.driver.get(self.url)
        # uname = self.wait.until(EC.presence_of_element_located(\
        #     (By.XPATH, '//*[@id="pageContainer"]/div/div/div/div/div[2]/div/div/div/div[1]/form/div[1]/div/div[1]/div/div[1]/div/span/span[2]/input')))
        # uname.send_keys(self.username)
        # pw = self.wait.until(EC.presence_of_element_located(\
        #     (By.XPATH, '//*[@id="pageContainer"]/div/div/div/div/div[2]/div/div/div/div[1]/form/div[1]/div/div[2]/div/div[1]/div/span/span[2]/input')))
        # pw.send_keys(self.password)
        # time.sleep(10)
        # action = self.wait.until(EC.presence_of_element_located(\
        #     (By.XPATH, '//*[@id="pageContainer"]/div/div/div/div/div[2]/div/div/div/div[4]/button')))
        # action.click()
        self.driver.get("https://web.cbbs.tmall.com/")
        with open("cookies_tm.json", "r", encoding="utf8") as fp:
            cookies = json.loads(fp.read())
        for item in cookies:
            self.driver.add_cookie(item)
        # self.driver.get("https://web.cbbs.tmall.com/?SCMSESSID=xVaJIDdF7jaPsiolnqla9fqhLCA&frameUrl=https%3A%2F%2Fweb.cbbs.tmall.com%2Fpages%2Fchaoshi%2Fflowanalyze%3F__IFRAME_CONTAINER_IFRAME_ID__%3D3#m471%2F4822")

    def is_element(self, check, html):
        try:
            return re.findall(check, html)
        except Exception:
            return ""

    def is_Error(self, er, flag):
        if 'dataSource' in er and flag == 1:
            return er
        elif 'data' in er and flag == 2:
            return er
        else:
            return False


    def page_parse_ll(self):
        self.login()
        time.sleep(2)
        # 请求地区json
        self.driver.get(str(self.rootUrl)+'serviceId=sm_option_area')
        area_html = re.findall(r'<pre.*">(.*?)</pre>', self.driver.page_source)
        area_html = json.loads(area_html[0]).get('data')
        area_data = [ar.get('label') for ar in area_html]

        # 请求品牌json
        self.driver.get(str(self.rootUrl)+'serviceId=sm_option_brand'+'&optionAll=false')
        bank_html = re.findall(r'<pre.*">(.*?)</pre>', self.driver.page_source)
        bank_html = json.loads(bank_html[0]).get('data')
        bank_label = [ar.get('label') for ar in bank_html]
        self.bank_value = [ar.get('value') for ar in bank_html]

        # 拼接链接
        # 请求三级类目的下拉列表
        for i in self.bank_value:
            self.driver.get(str(self.rootUrl)+'serviceId=sm_option_category_3&brandId='+str(i))
            time.sleep(1)
            product_html = re.findall(r'<pre.*">(.*?)</pre>', self.driver.page_source)
            product_html = json.loads(product_html[0]).get('data')
            product_html_label = [ii.get('label') for ii in product_html]
            self.product_html_value = [ii.get('value') for ii in product_html]
            time.sleep(1)

            for action in self.product_html_value:
                # 拼接的客户信息链接
                urlu = 'https://dataweb.cbbs.tmall.com/data/service/41/invoke.json'+'?brandId ='+str(i)+'&cate3Id ='+str(action)+'&endTime'+str(self.endTime)+'&id=sm_uv_overview'+'&logicArea=-99999'+'&startTime='+str(self.startTime)
                self.driver.get(urlu.replace(' ', ''))
                time.sleep(1)
                # json页面的解析到10个数组的上一级
                consumer_html = self.is_element(r'<pre.*">(.*?)</pre>', self.driver.page_source)
                consumer_html = self.is_Error(json.loads(consumer_html[0]).get('data').get('views')[0].get('value'), 1)
                if consumer_html:
                    buyerAll = consumer_html.get('dataSource')[0].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    buyerNew = consumer_html.get('dataSource')[1].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    buyerOld = consumer_html.get('dataSource')[2].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    payAmtPerByrAll = consumer_html.get('dataSource')[3].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    payAmtPerByrNew = consumer_html.get('dataSource')[4].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    payAmtPerByrOld = consumer_html.get('dataSource')[5].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    brandId = consumer_html.get('dataSource')[6].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('元', '')
                    CategoryId = consumer_html.get('dataSource')[7].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    AccessDate = consumer_html.get('dataSource')[8].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('人', '')
                    Account = consumer_html.get('dataSource')[9].get('ext').get('overviewList')[0].get('data')[0].get('value').replace('元', '')
                else:
                    buyerAll = ""
                    buyerNew = ""
                    buyerOld = ""
                    payAmtPerByrAll = ""
                    payAmtPerByrNew = ""
                    payAmtPerByrOld = ""
                    brandId = ""
                    CategoryId = ""
                    AccessDate = ""
                    Account = ""
                time.sleep(3)
                print(buyerAll, buyerNew, buyerOld, payAmtPerByrAll, payAmtPerByrNew, payAmtPerByrOld, brandId, CategoryId, AccessDate, Account)
                if buyerAll != "":
                    try:
                        sql = 'insert into TS_MemberAnalysis_OverViewNew(buyerAll, buyerNew, buyerOld, payAmtPerByrAll, payAmtPerByrNew, payAmtPerByrOld, brandId, CategoryId, AccessDate, Account)\
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                        self.cursor.execute(sql, (buyerAll, buyerNew, buyerOld, payAmtPerByrAll, payAmtPerByrNew, payAmtPerByrOld, brandId, CategoryId, AccessDate, Account))
                    except Exception as e:
                        print("入库失误"+e)
                        self.db.rollback()
                    self.db.commit()
            time.sleep(5)
        self.db.close()



            # print(i, product_html_value)
        # print(bank_label, bank_value)

    def page_parsr_hy(self):
        self.login()
        time.sleep(2)
        # 请求地区json
        self.driver.get(str(self.rootUrl)+'serviceId=sm_option_area')
        area_html = re.findall(r'<pre.*">(.*?)</pre>', self.driver.page_source)
        area_html = json.loads(area_html[0]).get('data')
        area_data = [ar.get('label') for ar in area_html]

        # 请求品牌json
        self.driver.get(str(self.rootUrl)+'serviceId=sm_option_brand'+'&optionAll=false')
        bank_html = re.findall(r'<pre.*">(.*?)</pre>', self.driver.page_source)
        bank_html = json.loads(bank_html[0]).get('data')
        bank_label = [ar.get('label') for ar in bank_html]
        self.bank_value = [ar.get('value') for ar in bank_html]

        # 拼接链接
        # 请求三级类目的下拉列表
        for i in self.bank_value:
            self.driver.get(str(self.rootUrl)+'serviceId=sm_option_category_3&brandId='+str(i))
            time.sleep(1)
            product_html = re.findall(r'<pre.*">(.*?)</pre>', self.driver.page_source)
            product_html = json.loads(product_html[0]).get('data')
            product_html_label = [ii.get('label') for ii in product_html]
            self.product_html_value = [ii.get('value') for ii in product_html]
            time.sleep(1)

            for action in self.product_html_value:
                # 拼接的客户信息链接
                urlu = 'https://dataweb.cbbs.tmall.com/data/service/invoke.json'+\
                    '?query.brandId='+str(i)+\
                    '&query.cate3Id='+str(action)+\
                    '&query.endTime='+str(self.endTime)+\
                    '&query.logicArea=-99999'+\
                    '&query.startTime='+str(self.startTime)+\
                    '&serviceId=sm_member_analysis_overview'
                self.driver.get(urlu.replace(' ', ''))
                user_html = self.is_element(r'<pre.*">(.*?)</pre>', self.driver.page_source)
                user_html = self.is_Error((json.loads(user_html[0]).get('data')[0].get('value')), 2)
                if user_html:
                    demo1 = user_html.get('data')[0].get('description').replace('人', '')
                    demo2 = user_html.get('data')[1].get('description').replace('人', '')
                    demo3 = user_html.get('data')[2].get('description').replace('人', '')
                    demo4 = user_html.get('data')[3].get('description').replace('元', '')
                    demo5 = user_html.get('data')[4].get('description').replace('元', '')
                    demo6 = user_html.get('data')[5].get('description').replace('元', '')
                else:
                    demo1 = ""
                    demo2 = ""
                    demo3 = ""
                    demo4 = ""
                    demo5 = ""
                    demo6 = ""
                if user_html:
                    try:
                        sql = 'insert into TS_UV_OverViewNew() values(%s,%s,%s,%s,%s,%s)'
                        self.cursor.execute(sql, ())
                    except Exception:
                        self.db.rollback()
                    self.db.commit()
                print(demo1, demo2, demo3, demo4, demo5, demo6)
            time.sleep(2)
        self.db.close()

if __name__ == '__main__':
    tm = TMShop()
    # tm.page_parse_ll()
    tm.page_parsr_hy()