'''
@Description: In User Settings Edit
@Author: your name
@Date: 2019-08-14 17:39:30
@LastEditTime: 2019-08-20 18:00:50
@LastEditors: Please set LastEditors
'''
import time
import re
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
import codecs
import pandas as pd
import json
from collections import OrderedDict

'''
@description:处理json数据格式 
@param {json} 
@return: 
'''
class WriterJson:
    def __init__(self):
        pass

    # 将单个DataFrame保存为JSON，确保中文显示正确
    def df_to_json(self, df, orient:str = 'table'):
        return json.loads(df.to_json(orient, force_ascii=False))

    # 将多个DataFrames组成的字典批量保存为JSON，确保中文显示正确:服务于类似`金融产品信息表`这样的包含多
    def dfs_to_json(self, dic_dfs, orient:str = 'table'):
        pass

    # 将单个OrderedDict保存为JSON List
    def odict_to_json(self, odict):
        items = list(odict.items())
        list_JSONed = []

        # 把列表中的每个df通过list append变成json
        for i in range(len(items)):
            try:
                list_JSONed.append([items[i][0],json.loads(items[i][1].to_json(orient='table', force_ascii=False))])
            except:
                print(items[i][0] + '表为空，请检查。')
        # 记录版本信息
        list_JSONed.append({'version_date': time.strftime("%Y/%m/%d")})

        return list_JSONed

    # 从list_JSONed获取公司名称，用于设置JSON文件名称
    def get_company_name_from_JSON(self, items_JSONed):
        pass

    # 将一个json list或者json dict存入文件
    def write_json(self, json_list, file_name, indent=4, encoding='utf-8'):
        f_out = codecs.open(file_name, 'w', encoding=encoding)
        json_str = json.dumps(json_list, indent=indent, ensure_ascii=False) #, encoding=encoding)
        f_out.write(json_str)
        f_out.close()

'''
@description: 天眼查爬虫主类
@param 
@return: 
'''        
class Tianyancha:

    # 常量定义
    url = 'https://www.tianyancha.com/login'

    def __init__(self, username, password, headless=False):
        self.username = username
        self.password = password
        self.headless = headless
        #填写信息
        self.driver = self.login(text_login='请输入11位手机号码', text_password='请输入登录密码')

    # 登录天眼查 done
    def login(self, text_login, text_password):
        time_start = time.time()

        # 操作行为提示
        print ('在自动输入完用户名和密码前，请勿操作鼠标键盘！请保持优雅勿频繁（间隔小于1分钟）登录以减轻服务器负载。')
        chromedriver="D:\Downloads\chromedriver_win32\chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chromedriver)

        # 强制声明浏览器长宽为1024*768以适配所有屏幕
        driver.set_window_position(0, 0)
        driver.set_window_size(1024, 768)
        driver.get(self.url)

        # 模拟登陆：Selenium Locating Elements by Xpath
        time.sleep(1)

        # 关闭底栏
        driver.find_element_by_xpath("//img[@id='tyc_banner_close']").click()
        driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']").click()
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(self.username)
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(self.password)

        # 手工登录，完成滑块验证码
        print ('请现在开始操作键盘鼠标，在15s内点击登录并手工完成滑块验证码。批量爬取只需一次登录。')
        time.sleep(10)
        print ('还剩5秒。')
        time.sleep(5)

        time_end = time.time()
        print('您的本次登录共用时{}秒。'.format(int(time_end - time_start)))
        return driver

    def tianyancha_scrapy(self,
                        keyword,
                        table="all",
                        change_page_interval=2,
                        export='xlsx',
                        quit_driver=True):
        """
        爬虫主程序
        keyword：关键词
        change_page_interval 翻页时的休眠时间
        """
        #公司搜索 done
        def search_company(driver,url1):
            driver.get(url1)
            #加载页面
            content=driver.page_source.encode('utf-8')
            soup1 = BeautifulSoup(content, 'lxml')
            try:
                # TODO：'中信证券股份有限公司'无法正确检索
                try:
                    url2 = soup1.find('div',class_='header').find('a', class_="name ").attrs['href']
                except:
                    # url2 = driver.find_element_by_xpath("//div[@class='web-content']/div[@class='header']/a[@class='name ']").get_attribute('href')
                    url2=driver.find_element_by_xpath('//*[@id="web-content"]//div[@class="header"]//a[position()<2]').get_attribute('href')
                print('登陆成功。')
            except:
                print('登陆过于频繁，请1分钟后再次尝试。')

            # # TODO: 如果搜索有误，手工定义URL2地址。有无改善方案？
            driver.get(url2)
            return driver
        
        #正常的表格爬取数
        def get_table_info(table):
            tab=table.find_element_by_tag_name('table')
            df = pd.read_html('<table>' + tab.get_attribute('innerHTML') + '</table>')
            
            if isinstance(df, list):
                df = df[0]
            if '操作' in df.columns:
                df = df.drop(columns='操作')
            # TODO：加入更多标准的表格处理条件data-content
            print(df)
            return df

        def tryonclick(table): # table实质上是selenium WebElement
            # 测试是否有翻页
            ## 把条件判断写进tryonclick中
            try:
                # 找到有翻页标记
                table.find_element_by_tag_name('ul')
                onclickflag = 1
            except Exception:
                print("没有翻页") ## 声明表格名称: name[x] +
                onclickflag = 0
            return onclickflag

        def tryontap(table):
            # 测试是否有翻页
            try:
                # table.find_element_by_xpath("//div[contains(@class,'over-hide changeTabLine f14')]")
                table.find_element_by_xpath("//div[@class='company_pager pagination-warp']")
                ontapflag = 1
            except:
                print("没有时间切换页") ## 声明表格名称: name[x] +
                ontapflag = 0
            return ontapflag
        def change_page(table, df, driver):
            # TODO:抽象化：频繁变换点
            # PageCount = table.find_element_by_class_name('company_pager').text #历史class_name（天眼查的反爬措施）：'total'
            # PageCount = re.sub("\D", "", PageCount)  # 使用正则表达式取字符串中的数字 ；\D表示非数字的意思
            PageCount = len(table.find_elements_by_xpath(".//ul[@class='pagination']/li")) - 1

            for _ in range(int(PageCount) - 1):
                # TODO:抽象化：频繁变换点
                button = table.find_element_by_xpath(".//a[@class='num -next']") #历史class_name（天眼查的反爬措施）：'pagination-next  ',''
                driver.execute_script("arguments[0].click();", button)
                ####################################################################################
                time.sleep(change_page_interval) # 更新换页时间间隔,以应对反爬虫
                ####################################################################################
                df2 = get_table_info(table) ## 应该可以更换不同的get_XXXX_info
                df = df.append(df2)
            return df

        # TODO：完善change_tap函数。
        def scrapy(driver,table,quit_driver=quit_driver):

            if isinstance(table, str):
                list_table = []
                list_table.append(table)
                table = list_table

            time.sleep(1)
            js="var q=document.documentElement.scrollTop=100000"  
            driver.execute_script(js)   #执行滑至底部
            
            time.sleep(1)
            tables = driver.find_elements_by_xpath("//div[contains(@id,'_container_')]")
            c = '_container_'
            name = [0] * (len(tables) - 2)
            # 生成一个独一无二的十六位参数作为公司标记，一个公司对应一个，需要插入多个数据表
            id = keyword
            table_dict = {}
            for x in range(len(tables)-2):
                name[x] = tables[x].get_attribute('id')
                name[x] = name[x].replace(c, '')  # 可以用这个名称去匹配数据库
                if ((name[x] in table) or (table == ['all'])):
                    # 检查用
                    print('正在爬取' + str(name[x]))

                    df = get_table_info(tables[x])
                    onclickflag = tryonclick(tables[x])
                    ontapflag = tryontap(tables[x])
                    # 判断此表格是否有翻页功能
                    if onclickflag == 1:
                        df = change_page(tables[x], df, driver)
                    # if ontapflag == 1:
                    #     df = change_tap(tables[x], df)
                    table_dict[name[x]] = df
                else:
                    pass
                    
            if quit_driver:
                driver.quit()
            return table_dict
        #表格格式
        def gen_excel(table_dict, keyword):
            with pd.ExcelWriter(keyword+'.xlsx') as writer:
                for sheet_name in table_dict:
                    table_dict[sheet_name].to_excel(writer, sheet_name=sheet_name, index=None)
        #json格式
        def gen_json(table_dict, keyword):
            list_dic = []
            for i in list(table_dict.keys()):
                list_dic.append((i, table_dict[i]))
            dic = OrderedDict(list_dic)
            list_json = WriterJson().odict_to_json(dic)
            WriterJson().write_json(json_list=list_json, file_name=keyword+'.json')

        time_start = time.time()
        #搜索链接
        url_search = 'http://www.tianyancha.com/search?key=%s&checkFrom=searchBox' % keyword
        self.driver = search_company(self.driver, url_search)
        table_dict=scrapy(self.driver,table)

        if export == 'xlsx':
            gen_excel(table_dict, keyword)
        elif export == 'json':
            gen_json(table_dict, keyword)
        else:
            print("请选择正确的输出格式，支持'xlsx'和'json'。")

        time_end = time.time()
        print('您的本次爬取共用时{}秒。'.format(int(time_end - time_start)))
        return table_dict
    
    #批量处理
    def tianyancha_scrapy_batch(self,input_template='input.xlsx',change_page_interval=2,export='xlsx'):
        df_input=pd.read_excel(input_template,encoding='gb18030').dropna(axis=1,how='all') #删除缺失的值，维度为1，全部元素（all）为空值才删除
        list_dicts=[]

        #逐个处理输入信息
        print(len(df_input.columns)-2)
        for i in range(len(df_input)):
            keyword=df_input['公司名称'].iloc[i]
            tables=[]
            #读取表格的位置[表名]
            for j in range(len(df_input.columns)-2):
                if not pd.isna(df_input.iloc[i,j+2]):
                    tables.append(df_input.iloc[i,j+2])
            
            table_dict=self.tianyancha_scrapy(keyword=keyword,table=tables,change_page_interval=change_page_interval,export=export, quit_driver=False)
            list_dicts.append(table_dict)
        self.driver.quit()
        return tuple(list_dicts)

'''
@description: 运行
'''
if __name__ == "__main__":
    #单个调用
    # list_match=['announcementcourt','lawsuit','court','zhixing','dishonest','courtRegister' ,\
    #             'abnormal','punish','equity','equityPledgeRatio','equityPledgeDetail','judicialSale',\
    #             'publicnoticeItem','environmentalPenalties','pastEquityCount','judicialAid']
    # ty=Tianyancha(username='13250168932',password='ilovena10').tianyancha_scrapy(keyword='广州地铁集团有限公司',table=list_match,export='xlsx')
    #批量写入
    tuple_dicts=Tianyancha(username='13250168932',password='ilovena10').tianyancha_scrapy_batch(input_template='input.xlsx',change_page_interval=2,export='xlsx')
