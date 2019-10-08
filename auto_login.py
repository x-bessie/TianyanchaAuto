'''
@Description: 模拟自动登陆天眼查，并爬取里面的表格。输出展示是表格，json。
@Author:Lina
@Date: 2019-08-20 16:02:05
@LastEditTime: 2019-08-30 16:11:29
@LastEditors: Please set LastEditors
'''
from  selenium  import webdriver
from PIL import Image,ImageGrab
from io import BytesIO
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import tesserocr
import time
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
from bs4 import BeautifulSoup

#chrom的驱动位置
chrome_path='D:\Downloads\chromedriver_win32\chromedriver.exe'
driver=webdriver.Chrome(chrome_path)

class Tianyancha:
    '''
    @description: 初始化
    @param {username,password,headless} 
    @return: 
    '''
    def __init__(self,username,password,headless=False):
        self.username=username
        self.password=password
        self.headless=headless
        self.driver=self.autologin(text_login='请输入11位手机号码', text_password='请输入登录密码')

    '''
    @description: 滑块位移的计算
    @param {type} 
    @return: 
    '''
    def get_track(self,distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 2 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 1    
 
        while current < distance:
            if current < mid:
            # 加速度为正2
                a = 3.5
            else:
                # 加速度为负3
                a = -3
                # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

        '''
        @description: 登陆函数
        @param {type} 
        @return: 
        '''
    '''
    @description: 登录方法
    @param {type} 
    @return: 
    '''
    def autologin(self,text_login,text_password):

        driver.get('http://www.tianyancha.com')
        time.sleep(2)
        driver.maximize_window()
        driver.implicitly_wait(10)
        #关底部
        try:
            driver.find_element_by_xpath('//*[@id="tyc_banner_close"]').click()
        except:
            pass
            
        #登陆按钮
        driver.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[1]/div/div/div[2]/div/div[4]/a').click()
        time.sleep(2)

        # 这里点击密码登录时用id去xpath定位是不行的，因为这里的id是动态变化的，所以这里换成了class定位
        driver.find_element_by_xpath(
            './/div[@class="modal-dialog -login-box animated"]/div/div[2]/div/div/div[3]/div[1]/div[2]').click()
        time.sleep(2)
        # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
        #输入用户名和密码
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_login))[-2].send_keys(self.username)  
        driver.find_elements_by_xpath("//input[@placeholder='{}']".format(text_password))[-1].send_keys(self.password)
        clixp = './/div[@class="modal-dialog -login-box animated"]/div/div[2]/div/div/div[3]/div[2]/div[5]'
        driver.find_element_by_xpath(clixp).click()
        time.sleep(2)


        #获取图
        img = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
        time.sleep(0.5)
        location = img.location
        size = img.size
        top,bottom,left,right = location['y'], location['y']+size['height'], location['x'], location['x']+size['width']
        # 截取第一张图片(无缺口的)
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        captcha1 = screenshot.crop((left, top, right, bottom))
        print('--->', captcha1.size)
        captcha1.save('captcha1.png')
        
        #获取第二张图，先点击
        driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]').click()
        time.sleep(2)
        img1 = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
        time.sleep(0.5)
        location1 = img1.location
        size1 = img1.size
        top1,bottom1,left1,right1 = location1['y'], location1['y']+size1['height'], location1['x'], location1['x']+size1['width']
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        captcha2 = screenshot.crop((left1, top1, right1, bottom1))
        captcha2.save('captcha2.png')

        # 获取偏移量
        left = 55  # 这个是去掉开始的一部分
        for i in range(left, captcha1.size[0]):
            for j in range(captcha1.size[1]):
                # 判断两个像素点是否相同
                pixel1 = captcha1.load()[i, j]
                pixel2 = captcha2.load()[i, j]
                threshold = 60
                if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                    pixel1[2] - pixel2[2]) < threshold:
                    pass
                else:
                    left = i
        print('缺口位置', left)
        
        time.sleep(3)

        left-=54
         # 开始移动
        track = self.get_track(left)

        print('滑动轨迹', track)
        track += [5,-5]  # 滑过去再滑过来，不然有可能被吃
        # 拖动滑块
        starttime=time.time()
        slider = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]')
        ActionChains(driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
        ActionChains(driver).release().perform()
    
        endtime=time.time()
        print("时间：")
        print(endtime-starttime)
        time.sleep(1)
        try:
            if driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]'):
                print('能找到滑块，重新试')
                driver.delete_all_cookies()
                driver.refresh()
                self.autologin(text_login, text_password) #重新登陆 
            else:
                print('login success')
        except:
            print('login success')
        time.sleep(2)

        return driver

    '''
    @description: 爬虫主要方法
    @param {type} 
    @return: 
    '''
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
        # def gen_json(table_dict, keyword):
        #     list_dic = []
        #     for i in list(table_dict.keys()):
        #         list_dic.append((i, table_dict[i]))
        #     dic = OrderedDict(list_dic)
        #     list_json = WriterJson().odict_to_json(dic)
        #     WriterJson().write_json(json_list=list_json, file_name=keyword+'.json')

        time_start = time.time()
        #搜索链接
        url_search = 'http://www.tianyancha.com/search?key=%s&checkFrom=searchBox' % keyword
        self.driver = search_company(self.driver, url_search)
        table_dict=scrapy(self.driver,table)

        if export == 'xlsx':
            gen_excel(table_dict, keyword)
        # elif export == 'json':
        #     gen_json(table_dict, keyword)
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


# if __name__ == "__main__":
#     chrome_path='D:\Downloads\chromedriver_win32\chromedriver.exe'
#     driver=webdriver.Chrome(chrome_path)
    
#     # list_match=['announcementcourt','lawsuit','court','zhixing','dishonest','courtRegister' ,\
#     #             'abnormal','punish','equity','equityPledgeRatio','equityPledgeDetail','judicialSale',\
#     #             'publicnoticeItem','environmentalPenalties','pastEquityCount','judicialAid']
#     # ty=Tianyancha(username='username',password='password').tianyancha_scrapy(keyword='北京三快科技有限公司',table=list_match,export='xlsx')
#     # 批量写入
    # tuple_dicts=Tianyancha(username='username',password='password').tianyancha_scrapy_batch(input_template='input.xlsx',change_page_interval=2,export='xlsx')

