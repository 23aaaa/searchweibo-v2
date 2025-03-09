# 微博数据爬虫工具

## 功能特点

- 支持指定时间区间搜索
- 支持多关键词批量爬取
- 支持断点续爬功能
- 支持评论数据获取
- 支持用户信息批量采集
- 支持地理位置数据采集
- 支持 MongoDB 或 CSV 存储方式
- 自动更新 Cookie 功能

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

## 【小白入门】零基础快速上手

如果你是爬虫小白，请按照以下步骤一步一步操作：

### 环境准备 (Windows系统为例)

1. **安装Python**：
   - 下载并安装Python 3.8或更高版本 [Python官网下载](https://www.python.org/downloads/)
   - 安装时勾选"Add Python to PATH"选项
   - 验证安装：打开命令提示符(CMD)，输入`python --version`，应显示Python版本号

2. **安装Git**（用于克隆项目）：
   - 下载并安装Git [Git官网下载](https://git-scm.com/downloads)
   - 验证安装：打开CMD，输入`git --version`，应显示Git版本号

### 项目安装与配置

1. **下载项目**：
   - 方式一：使用Git克隆
     ```bash
     # 打开CMD，进入你想保存项目的文件夹，例如D盘
     cd /d D:\Projects
     # 克隆项目
     git clone https://github.com/Euclid-Jie/Euclidweibo-search-v2.git
     # 进入项目目录
     cd Euclidweibo-search-v2
     ```
   - 方式二：直接下载ZIP压缩包
     - 访问 https://github.com/Euclid-Jie/Euclidweibo-search-v2
     - 点击"Code"按钮，选择"Download ZIP"
     - 解压到你想要的位置，如D:\Projects\Euclidweibo-search-v2

2. **创建虚拟环境**（推荐但非必须）：
   ```bash
   # 在项目目录下创建虚拟环境
   python -m venv .venv
   # 激活虚拟环境
   .venv\Scripts\activate
   # 激活后命令行前会出现(.venv)前缀
   ```

3. **安装依赖**：
   ```bash
   # 确保你在项目目录下，并且已激活虚拟环境(如果使用)
   pip install -r requirements.txt
   ```
   > 注意：如果安装过程较慢，可以使用国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

4. **填写微博Cookie**：
   
   获取Cookie是成功运行爬虫的关键步骤！
   
   详细图文步骤：
   - 打开浏览器（推荐使用Chrome或Edge），访问 https://weibo.com 并登录你的账号
   - 按F12打开开发者工具，切换到"Network"(网络)标签
   - 刷新页面
   - 在请求列表中，找到任一 weibo.com 请求（通常在顶部）
   - 右键点击该请求 → 选择"Headers"(标头)标签
   - 在"Request Headers"中找到"Cookie:"开头的行
   - 复制完整的Cookie值（很长的一串文字）
   
   ![获取Cookie示意图](https://i.imgur.com/example.jpg)
   
   - 在项目根目录，创建或编辑cookie.txt文件，将复制的Cookie值粘贴进去并保存

### 使用教程：三步抓取微博数据

#### 步骤一：采集微博内容

1. **修改配置**：
   - 用任意文本编辑器（如记事本、VSCode）打开`1_WeiboClassRun.py`
   - 修改关键词和时间范围：
   ```python
   search_options = WeiboSearchOptions(
       cookie_path="cookie.txt",  # cookie文件路径，通常不用修改
       limit=3,  # 最小时间跨度更新页面数阈值，建议初学者保持默认值
       keyword_list=[
           # 取消注释你想搜索的关键词，记住每行结尾要有逗号
           # "绿色快递包装",
           # "环保包装",
           "可循环包装"  # 最后一个关键词后面不需要逗号
       ],
       start_time="2023-01-01-0",  # 开始时间，格式：年-月-日-小时(0-23)
       end_time="2023-12-31-23",   # 结束时间
       keyword_contain=False,  # 是否严格包含关键词，False表示宽松匹配
       mongo_save=False,       # 新手建议使用CSV格式保存(False)
       ColName="1_可循环包装_帖子内容",  # 输出文件名前缀
   )
   ```

2. **运行脚本**：
   ```bash
   # 确保在项目根目录下运行
   python 1_WeiboClassRun.py
   ```

3. **检查结果**：
   - 成功运行后，在`Weibo`文件夹中会生成`1_可循环包装_帖子内容.csv`文件
   - 可用Excel或任意文本编辑器打开查看

**运行截图示例**：
```
开始爬取关键词: 可循环包装
时间区间: 2023-01-01-0 至 2023-12-31-23
...
共获取100条微博数据
数据已保存至: Weibo/1_可循环包装_帖子内容.csv
```

#### 步骤二：获取用户信息

1. **无需修改配置**，直接运行：
   ```bash
   python 2_get_username_finish.py
   ```

2. **脚本说明**：
   - 该脚本会读取步骤一生成的帖子内容CSV，自动提取用户ID
   - 为每个用户获取详细信息（如粉丝数、认证状态等）
   - 支持断点续爬，如果中断可以继续从上次位置爬取

3. **检查结果**：
   - 成功运行后，在`Weibo`文件夹中会生成`2_可循环包装_用户信息内容.csv`文件

#### 步骤三：获取评论和地理位置数据

1. **无需修改配置**，直接运行：
   ```bash
   python 3_get_pinglun.py
   ```

2. **脚本说明**：
   - 该脚本会读取步骤一生成的帖子内容，获取每条微博的评论数据
   - 同时会解析并保存地理位置信息

3. **检查结果**：
   - 成功运行后，在`Weibo`文件夹中会生成：
     - `3_可循环包装_评论数据.csv`：包含评论内容
     - `4_可循环包装_地理定位数据.csv`：包含地理位置信息

### 常见问题与解决方法

#### 1. "无法连接到服务器"或"请求超时"
- **问题原因**：网络连接问题或微博服务器繁忙
- **解决方法**：
  - 检查网络连接
  - 等待几分钟后重试
  - 如使用VPN，尝试关闭或更换节点

#### 2. "登录状态异常"或"Cookie失效"
- **问题原因**：Cookie已过期（通常有效期为几天到几周）
- **解决方法**：
  - 重新获取Cookie并更新cookie.txt
  - 或尝试自动更新Cookie功能：
    ```python
    from Euclidweibo import weiboCookie
    weiboCookie().update_cookie()
    ```

#### 3. 数据量很少或为空
- **问题原因**：关键词太冷门、时间范围设置不当或Cookie问题
- **解决方法**：
  - 尝试更热门的关键词
  - 扩大时间范围
  - 检查Cookie是否正确
  - 设置`keyword_contain=False`进行宽松匹配

#### 4. 程序运行中断
- **问题原因**：网络不稳定、微博反爬机制或系统限制
- **解决方法**：
  - 直接重新运行脚本，程序会自动从断点处继续
  - 若频繁中断，可考虑减小时间范围，分批爬取
  - 在请求之间增加延时：修改`Utils.py`中的休眠时间

#### 5. 无法安装某些依赖
- **问题原因**：版本冲突或系统兼容性问题
- **解决方法**：
  - 尝试单独安装问题依赖：`pip install 包名==版本号`
  - 使用conda环境（如Anaconda）替代venv

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

### 代理配置

如需使用代理，可修改`Set_proxies.py`文件：

```python
# 示例: 配置HTTP代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
```

## 常见问题解决

1. **Cookie失效问题**
   - 症状：报错信息包含"请求失败"、"登录失效"等
   - 解决方法：更新Cookie，可手动更新或使用`weiboCookie().update_cookie()`

2. **IP被限制**
   - 症状：大量请求后无法获取数据或返回空结果
   - 解决方法：降低请求频率，设置合理的时间间隔；使用代理IP

3. **数据量过大导致程序崩溃**
   - 症状：内存错误或程序卡死
   - 解决方法：缩小时间范围分批爬取；使用MongoDB存储减轻内存压力

4. **字段解析错误**
   - 症状：某些字段显示为空或格式错误
   - 解决方法：检查微博HTML结构是否变更；更新代码中的解析逻辑

## 数据存储与导出

### MongoDB存储（mongo_save=True）

使用MongoDB存储时，数据将保存在名为"Weibo"的数据库中，集合名为指定的ColName。

从MongoDB导出数据到CSV:
```python
from Euclidweibo import read_mongo
import pandas as pd

# 读取MongoDB数据
df = read_mongo("Weibo", "集合名称", query=None, no_id=True)
# 筛选数据（可选）
df = df.loc[df["time"] >= pd.to_datetime("2023-01-01")]
# 导出到CSV
df.to_csv("output.csv", index=False, encoding="utf-8-sig")
```

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


## 性能与优化建议

1. **时间范围控制**：建议将大范围时间拆分为多个小范围（如按月）分别爬取
2. **关键词精确**：使用精确关键词可以减少数据量和处理时间
3. **MongoDB存储**：对于大规模数据爬取，推荐使用MongoDB存储
4. **代理设置**：长时间爬取建议配置代理IP池
5. **合理休眠**：在请求之间设置适当的休眠时间，避免被封

## 更新日志

## 注意事项

1. Cookie 需要定期更新，建议每次使用前更新
2. 微博限制每个时间段最多显示 30-50 页数据
3. 爬取速度过快可能导致账号被限制
4. 请遵守网站的robots协议和相关法律法规，合理使用爬虫

## 开源许可

本项目采用 MIT 许可证。

## 贡献指南

欢迎提交 Pull Request 或 Issues！

## 联系方式

如有问题，请通过以下方式联系：
- GitHub Issues
- 邮件联系（请在 Issues 中留言获取邮箱）
