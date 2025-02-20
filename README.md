## 功能特点

- 支持指定时间区间搜索
- 支持多关键词批量爬取
- 支持断点续爬功能
- 支持评论数据获取
- 支持 MongoDB 或 CSV 存储方式
- 自动更新 Cookie 功能

## 快速开始

### 1、下载项目并安装依赖

```bash
# 克隆项目
git clone https://github.com/Euclid-Jie/searchweibo-v2.git

# 安装依赖
pip install -r requirements.txt
```

### 2、设置 Cookie

将 `Cookie` 写入 `Cookie.txt` 中。80% 的报错/运行异常由 Cookie 设置不正确引起，可以查看这个获取 Cookie 的[视频教程](https://www.bilibili.com/video/BV1Sh4y1J7Yz)。

### 3、运行爬虫

```python
# 设置参数
search_options = WeiboSearchOptions(
    cookie_path="cookie.txt",  # cookie文件路径
    limit=3,  # 最小时间跨度更新页面数阈值，建议3~5
    keyword_list=["北师大", "BNU"],  # 关键词列表
    start_time="2020-01-01-0",  # 开始时间
    end_time="2020-01-10-0",  # 结束时间
    keyword_contain=True,  # 是否要求微博内容严格包含关键词
    mongo_save=True,  # True: 存数据库, False: 存入CSV
    ColName="test",  # CSV文件名（mongo_save=False时有效）
)

# 运行爬虫
WeiboClassRun(search_options)
```