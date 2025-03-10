# -*- coding: utf-8 -*-
# time: 2022/10/1 11:32
# file: WeiboClassRun.py
# author: Euclid_Jie
import pymongo
from datetime import datetime
from WeiboClassV1 import WeiboClassV1, WeiboSearchOptions
import pandas as pd
from Euclidweibo import read_mongo, weiboCookie

# 设置参数
search_options = WeiboSearchOptions(
    cookie_path="cookie.txt",
    limit=3,
    # 记得加逗号，否则会报错
    keyword_list=[
        # "绿色快递包装"
        # "环保包装"
        # "可降解包装"
        # "无塑料包装"
        # "快递回收"
        "可循环包装"
    ],
    start_time="2016-01-01-0",
    end_time="2025-01-1-0",
    keyword_contain=False,
    # 设置为True，将数据写入MongoDB, 否则写入CSV
    mongo_save=False,
    ColName="1_可循环包装_帖子内容",
)
# 运行函数前, 请先设置cookie.txt
# 自动更新cookie
# weiboCookie().update_cookie()
WeiboClassV1(search_options).main_get()

# ---------------读取MongoDB数据至CSV
# for key in keyList:
#     df = read_mongo("Weibo", key, query=None, no_id=True)
#     df = df.loc[df["time"].apply(lambda x: isinstance(x, datetime))]
#     # df = df[df['time'].str.contains('02月')].copy()
#     df = df.loc[df["time"] >= pd.to_datetime("2023-08-01")]
#     df.to_csv(
#         r"outData\2023-08-{}.csv".format(key), index=False, encoding="utf-8-sig"
#     )
