# 导入必要的库
from .Set_header import Set_header  # 导入设置请求头的函数
import json
import requests
import os

# 声明该模块对外暴露的函数
__all__ = ["Get_user_info_v2"]


def Get_user_info_v2(uid):
    """
    根据微博用户的uid获取用户信息
    
    # 函数功能说明：
    # 1. 构造微博用户信息的API请求URL(url构成示例（5976738651为用户id）："https://weibo.com/ajax/profile/detail?uid=5976738651")
    # 2. 设置请求头，包含必要的cookie信息
    # 3. 发送HTTP请求获取返回的全部数据，为json文件
    # 4. 解析响应数据并返回用户信息，尽可能全部返回
    
    # API说明：
    # - 基础URL格式："https://weibo.com/ajax/profile/detail?uid={uid}"
    # - 返回数据包含用户的基本信息，如性别、位置、认证状态等，尽可能全部返回
    
    Args:
        uid (str): 微博用户的唯一标识ID
    
    Returns:
        dict: 包含用户信息的字典数据
    """
    # 构造请求URL，将用户ID嵌入到URL中
    # 使用detail接口获取更详细的用户信息
    URL = "https://weibo.com/ajax/profile/detail?uid={}".format(uid)
    
    # 获取当前文件所在目录的绝对路径
    current_dir = os.path.abspath(os.path.dirname(__file__))
    # 获取父目录路径，用于定位cookie文件
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    # 设置请求头，包含必要的cookie信息
    header = Set_header(os.path.join(parent_dir, "cookie.txt"))
    
    # 发送GET请求获取用户详细数据
    # timeout=60 设置请求超时时间为60秒
    response = requests.get(URL, headers=header, timeout=60)
    # 将响应内容解码为UTF-8格式
    # ignore参数用于忽略无法解码的字符
    html = response.content.decode("utf-8", "ignore")
    # 解析JSON响应数据，提取data字段
    # detail接口返回的数据结构可能与info接口不同，但基本格式相似
    data_json = json.loads(html)["data"]

    return data_json
    