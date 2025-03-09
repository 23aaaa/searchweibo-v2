# 微博数据爬虫工具

## 项目结构

```
.
├── Weibo/                    # 存储爬取数据的目录
│   ├── 1_可循环包装_帖子内容.csv   # 存储微博帖子内容
│   ├── 2_可循环包装_用户信息内容.csv # 存储用户信息内容
│   ├── 3_可循环包装_评论数据.csv   # 存储评论数据
│   ├── 4_可循环包装_地理定位数据.csv # 存储地理定位数据
│   └── 爬取进度/              # 存储爬虫进度信息，用于断点续爬
├── Euclidweibo/              # 核心功能模块目录
├── 1_WeiboClassRun.py        # 主程序入口，用于爬取微博内容
├── 2_get_username_finish.py  # 获取用户信息程序
├── 3_get_pinglun.py          # 获取评论数据程序
├── WeiboClassV1.py           # 微博爬虫基础类
├── cookie.txt                # 存储Cookie
├── requirements.txt          # 项目依赖
└── README.md                 # 项目说明文档
```


## 详细安装步骤

### 1、下载项目并安装依赖

```bash
# 克隆项目
git clone https://github.com/Euclid-Jie/Euclidweibo-search-v2.git

# 创建并激活虚拟环境（可选但推荐）
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2、设置 Cookie

Cookie是爬虫运行的关键。将 `Cookie` 写入 `Cookie.txt` 中。特别注意：80% 的报错/运行异常由 Cookie 设置不正确引起，请参考[视频教程](https://www.bilibili.com/video/BV1Sh4y1J7Yz)获取正确设置方法。

Cookie获取步骤：
1. 登录微博网页版 https://weibo.com
2. 按F12打开开发者工具，切换到网络(Network)标签
3. 刷新页面，在请求列表中找到weibo.com的请求
4. 在请求头(Headers)中找到Cookie字段，复制其完整内容
5. 将复制的内容粘贴到cookie.txt文件中

您也可以使用自动更新功能：
```python
from Euclidweibo import weiboCookie
weiboCookie().update_cookie()
```

### 3、爬虫使用流程

#### 步骤一：微博内容爬取（1_WeiboClassRun.py）

```python
from WeiboClassV1 import WeiboClassV1, WeiboSearchOptions

# 设置参数
search_options = WeiboSearchOptions(
    cookie_path="cookie.txt",  # cookie文件路径
    limit=3,  # 最小时间跨度更新页面数阈值，建议3~5
    keyword_list=["可循环包装"],  # 关键词列表
    start_time="2016-01-01-0",  # 开始时间
    end_time="2025-01-01-0",  # 结束时间
    keyword_contain=False,  # 是否要求微博内容严格包含关键词
    mongo_save=False,  # True: 存入MongoDB, False: 存入CSV
    ColName="1_可循环包装_帖子内容",  # 存储文件名
)

# 运行爬虫
WeiboClassV1(search_options).main_get()
```

#### 步骤二：采集用户信息（2_get_username_finish.py）

执行该脚本会自动读取步骤一中爬取的微博内容，提取用户ID并获取用户详细信息：

```python
python 2_get_username_finish.py
```

#### 步骤三：获取评论和地理位置数据（3_get_pinglun.py）

执行该脚本会获取微博评论数据以及相关地理位置信息：

```python
python 3_get_pinglun.py
```

## 高级配置选项

### WeiboSearchOptions 参数详解

| 参数名 | 类型 | 默认值 | 说明 |
|-------|------|--------|------|
| cookie_path | str | "cookie.txt" | Cookie文件路径 |
| limit | int | 5 | 用于控制更新时间跨度的阈值 |
| keyword_list | List | ["人工智能"] | 关键词列表 |
| start_time | str | "2023-03-01-0" | 开始时间（格式：YYYY-MM-DD-H） |
| end_time | str | "2023-08-01-0" | 结束时间（格式：YYYY-MM-DD-H） |
| keyword_contain | bool | False | 是否要求微博内容严格包含关键词 |
| mongo_save | bool | False | 是否保存到MongoDB |
| ColName | str | Optional | 文件名或集合名 |

### 断点续爬机制

本爬虫支持断点续爬功能，中断后可以从上次爬取的位置继续：

- 微博内容爬取支持按时间分片的自动续爬
- 用户信息支持根据已处理ID列表的续爬
- 评论数据支持按微博ID的续爬

断点续爬数据存储在`Weibo/爬取进度/`目录下的相应文件中。


## 数据存储与导出

### CSV存储（mongo_save=False）

CSV文件将保存在Weibo目录下，包含以下几个文件：
- 1_xxx_帖子内容.csv：微博内容数据
- 2_xxx_用户信息内容.csv：用户信息数据
- 3_xxx_评论数据.csv：评论数据
- 4_xxx_地理定位数据.csv：地理位置数据

## 数据字段说明

### 帖子内容字段说明
| 中文字段 | 英文字段 | 释义 |
|---------|---------|------|
| keyWords | Keywords | 关键词，用于描述微博内容的主题或标签，常用于搜索和分类。 |
| mid | Message ID | 微博帖子的唯一标识符（Message ID），用于定位具体的微博内容。 |
| mblogid | Microblog ID | 微博内容的唯一标识符，与 mid 类似，具体差异可能因数据来源而异。 |
| uid | User ID | 用户的唯一标识符，用于区分微博平台上的不同用户。 |
| nick_name | Nickname | 用户昵称，即用户在微博上显示的名字，可能更改但非唯一。 |
| time | Timestamp | 发布时间，记录微博内容的发布时间，通常以时间戳或日期格式表示。 |
| content | Content | 微博正文内容，即用户发布的文本信息，可能包含文字、链接或多媒体描述。 |
| 转发数 | Reposts Count | 转发数量，表示该微博被其他用户转发的次数。 |
| 评价数 | Comments Count | 评论数量，表示该微博收到的评论条数。 |
| 点赞数 | Attitudes Count | 点赞数量，表示该微博被其他用户点赞的次数。 |

### 用户信息字段说明

| 中文字段 | 英文字段 | 释义 |
|---------|---------|------|
| 用户主页的URL | Profile URL | 用户的微博主页链接，可通过此链接访问用户的个人主页。 |
| 唯一ID | User ID | 用户的唯一标识符，用于精确识别特定用户。 |
| 用户粉丝数 | Followers Count | 该用户的粉丝数量，反映用户的影响力。 |
| 用户性别 | Gender | 用户的性别信息（男/女/未知）。 |
| 用户个人主页显示的地址 | Location | 用户在个人资料中设置的地理位置信息。 |
| 用户的认证状态 | Verified Status | 表示用户是否通过微博官方认证（已认证/未认证）。 |
| 认证类型 | Verification Type | 用户认证的具体类型（如个人认证、机构认证等）。 |
| 用户地址 | User Location | 用户设置的所在城市。 |

### 评论数据字段说明
| 中文字段 | 英文字段 | 释义 |
|---------|---------|------|
| 帖子的URL | Post URL | 原微博帖子的链接地址，用于定位评论所属的具体微博。 |
| 微博唯一ID | Comment ID | 评论的唯一标识符，用于区分不同的评论。 |
| 带时区时间格式 | Timestamp | 评论发布的具体时间。 |
| 评论内容 | Comment Content | 用户发表的评论文本内容。 |
| 转发量 | Reposts Count | 该评论被转发的次数（评论一般为0）。 |
| 评论量 | Reply Count | 该评论收到的回复数量，即子评论数。 |
| 点赞量 | Like Count | 该评论获得的点赞数量。 |
| 地理定位解析结果 | Source Location | 发表评论时的地理位置信息或设备来源（去除"来自"前缀）。 |


## 注意事项

1. Cookie 需要定期更新，建议每次使用前更新
2. 请遵守网站的robots协议和相关法律法规，合理使用爬虫

## 开源许可

本项目采用 MIT 许可证。

## 贡献指南

欢迎提交 Pull Request 或 Issues！

## 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- 邮件联系（请在 Issues 中留言获取邮箱）
