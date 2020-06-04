<!--
 * @Description: 
 * @Author: bessie
 * @Date: 2019-08-23 09:43:17
 * @LastEditTime: 2019-08-30 16:19:14
 * @LastEditors: Please set LastEditors
 -->

# TiayanchaAuto

** 此脚本是爬取天眼查的搜索关键词，爬取搜索到的公司的司法风险和经营风险 **

#### 运行环境以及下载地址
- python 3.6  (Anaconda 5.2.0   Anaconda3-5.2.0-Windows-x86_64.exe 地址：https://repo.anaconda.com/archive/)
- selenium 3.141.0
- tesserocr v2.4.0 - Python 3.6 - 64bit  https://github.com/simonflueckiger/tesserocr-windows_build/releases
- pandas 
- ChromeDriver   这个的版本要看Selenium 和Chrome浏览器的版本。 https://blog.csdn.net/yoyocat915/article/details/80580066|https://blog.csdn.net/yoyocat915/article/details/80580066
chromedriver download : http://chromedriver.storage.googleapis.com/index.html
- VS Code
辅助工具：
- XPath Helper  （chrome的插件，非主要，提取页面dom用）

#### 安装步骤
1.安装 python3.6  此程序使用Anaconda 集成,直接安装即可。
2.安装selenium    pip install selenium==3.141.0 (百度: python pip )
3.安装tesserocr   pip install tesserocr==2.2.2   失败请见：https://blog.csdn.net/coolcooljob/article/details/80385711  
下载后离线包后：pip install tesserocr-2.4.0-cp36-cp36m-win_amd64.whl
4.下载ChromeDriver，请务必对应Chrome版本
5.（开发环境配置） VS Code需要安装python调试环境，`File->perferences->settings ->'输入查找：Python:conda Path'->输入python.exe绝对路径（我的C:\Users\qctc\Anaconda3\python.exe`）


#### 使用方法
run.py
启动主程序中加入自己的账号密码和要爬取的规则
username：用户名
password：密码
input.xlsx :要爬取的公司表格
备注：这个表格必须严格按照格式输入，公司名必须正确。里面的字段直接复制。具体看示例input.xlsx
change_page_interval 默认2
export:导出格式默认为 xlsx
list_match:爬取的table名称
keyword:公司名称

单个实例：
```
    list_match=['announcementcourt','lawsuit','court','zhixing','dishonest','courtRegister' ,\
                'abnormal','punish','equity','equityPledgeRatio','equityPledgeDetail','judicialSale',\
                'publicnoticeItem','environmentalPenalties','pastEquityCount','judicialAid']

    ty=Tianyancha(username='',password='').tianyancha_scrapy(keyword='广州地铁集团有限公司',table=list_match,export='xlsx')

```
批量实例：
```
ty=Tiyancha(username='',passord='').tianyancha_scrapy_batch(input_template='input.xlsx',change_page_interval=2,export='xlsx')
```

#### 温馨提示  19/08/30
里面的xpath有些不是固定的，反扒工程师会不定期修改，有改请告知。


#### 19/08/30
添加了滑块滑动的破解方法，现在完全全自动
    文件：auto_login.py
    运行使用run.py
    
#### 20/06/04
更新部分xpath元素定位

#### 项目结构 20/6/2

```
run.py   项目启动
auto_login.py   全自动爬取天眼查公司风险（最终版本v3）
```
scrapy_table_name.txt   爬取页面上的表格的名称
tinayancha.py （手动处理滑块 version 1）
tianyanchaAuto.py 

##### 爬取前设置
1.input.xls 
只需将公司名称填入，后面表格名可以按照爬取需求增加或删除。


表名对应scrapy_table_name。
2.scrapy_table_name  的字段需定时维护，可能有改动。
3.设置账号密码


##### 项目启动
开发： 启动 run.py文件
客户使用： 
在有基本运行环境基础上， 在**项目目录**下命令启动:
`python  run.py`


