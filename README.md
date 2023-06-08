# financial-crawler
- 科创板、创业板、主板IPO数据收集器。数据源为官网，见代码内部

## 此项目仅用于个人研究


# 设计思路

<img src="https://i.postimg.cc/Y0dzhWqW/popo-2.jpg" height="100%" width="100%">

<img src="https://i.postimg.cc/0jkCkfxv/popo-1.jpg" height="100%" width="100%">

# 完成功能
## 一阶段
- [x] 科创板、创业板、主板数据下载
- [x] 科创板、创业板、主板数据建模
- [x] 数据写入数据库，选择的数据库为postgresql
- [x] 定时功能，可指定时间每日自动下载
- [x] 只更新有更新的IPO数据
- [x] 主板招股说明书pdf解析器，用于解析得到募资金额数据
  - 说明：正确率70+%，针对主板收集到的公司进行解析，解析不正确的内容中，半数是券商等金融机构，没有募资金额数据

## 二阶段
- 主要任务是指标的构建，目前指标已思考完毕，待实现。
- [x] 基于grafana构建的自更新的指标面板：
  - 各交易所截止本日整体IPO数量、每日总量
  - 科创板本年度提交IPO，募集资金；成功IPO，募资资金；科创板本年度提交IPO按募资排序
  - 创业板本年度提交IPO，募集资金；成功IPO，募资资金；科创板本年度提交IPO按募资排序
  - 其他指标待补充

## 三阶段
- [x] 基于全面注册制，重新设计数据表，存放上交所和深交所的项目数据（IPO、再融资、并购重组、转板上市）
- [ ] 重新实现存放逻辑，由Scrapy.Item保存转为基于json驱动，json保存数据库字段、关联枚举，json中数据库可用于结果数据映射，数据格式转化，生成更新sql，及后续C端页面的展示。关联枚举基于GPT进行生成，生成时间几乎为0。

## 四阶段
- [ ] 提供指标api服务，
- [ ] 提供客户端页面（小程序 或 web站点 或 原生端）
- [ ] IPO公司详情数据展示

<img src="https://i.postimg.cc/xYD4dQXM/Picsee-3.png" height="100%" width="100%">


## 技术栈
- py3
- scrapy
- postgresql


## 启动方式
- 安装python3.x(建议通过anaconda安装)
- 到crawler文件下pip install安装requirements.txt相关依赖
- 安装并运行postgresql
- 在crawler目录下执行python crawler.py -t="10:00"，后续定时为早上10:00

## 其他
- 其他配置可查看crawler.py
- grafana数据及postgresql建表数据见design文件夹中
- 关于数据结构化可参考crawler/crawler/items内容。design/design.xmind根据数据和业务代码罗列现有业务逻辑
