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
git clone https://github.com/Euclid-Jie/Euclidweibo-search-v2.git

# 安装依赖
pip install -r requirements.txt
```

### 2、设置 Cookie

将 `Cookie` 写入 `Cookie.txt` 中。80% 的报错/运行异常由 Cookie 设置不正确引起，特录制获取 Cookie 的[视频教程](https://www.bilibili.com/video/BV1Sh4y1J7Yz)，欢迎观看。

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
    mongo_save=True,  # True: 存入MongoDB, False: 存入CSV
    ColName="test",  # CSV文件名（mongo_save=False时有效）
)

# 运行爬虫
WeiboClassRun(search_options)
```

## 数据字段说明

| 字段名            | 说明                   |
|-----------------|------------------------|
| keyWords        | 检索的关键词             |
| mid             | 微博标识ID              |
| time            | 微博发布时间             |
| nick_name       | 发布者昵称              |
| content         | 微博内容                |
| reposts         | 转发数                  |
| comments        | 评论数                  |
| attitudes       | 点赞数                  |

## 更新日志

### 2024-03-12
- 新增: 自动更新 cookie 功能
- 优化: 自动获取用户总微博数
- 优化: 断点续爬功能

### 2023-12-15
- 简化代码结构
- 统一参数配置方式
- 优化数据存储逻辑

## 注意事项

1. Cookie 需要定期更新，建议每次使用前更新
2. 微博限制每个时间段最多显示 30-50 页数据
3. 爬取速度过快可能导致账号被限制
4. 建议使用代理 IP 进行大规模爬取

## 开源许可

本项目采用 MIT 许可证。

## 贡献指南

欢迎提交 Pull Request 或 Issues！

## 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- 邮件联系（请在 Issues 中留言获取邮箱）
