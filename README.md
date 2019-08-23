<!--
 * @Description: 
 * @Author: bessie
 * @Date: 2019-08-23 09:43:17
 * @LastEditTime: 2019-08-23 10:13:17
 * @LastEditors: Please set LastEditors
 -->

# TiayanchaAuto

** 此脚本是爬取天眼查的搜索关键词，爬取搜索到的公司的司法风险和经营风险 **

#### 运行环境
python 3
selenium 3.141.0
pandas 
ChromeDriver   这个的版本要看Selenium 和Chrom浏览器的版本。具体自己查.....

主要是以上


#### 使用方法

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

#### 温馨提示
里面的xpath有些不是固定的，反扒工程师会不定期修改，有改请告知。

