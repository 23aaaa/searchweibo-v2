# 导入必要的库
import pandas as pd
from Euclidweibo.Get_single_weibo_details import Get_single_weibo_details
from Euclidweibo.Set_header import Set_header
import time
from datetime import datetime
import random
import requests
import json
import os
# 添加dateutil库用于解析不规则时间格式
from dateutil import parser

# 添加全局变量
failed_ids = []
location_data = []  # 新增全局变量用于存储地理定位数据

def load_progress():
    """
    加载断点续爬进度
    
    Returns:
        set: 已处理过的微博ID集合
    """
    progress_file = 'Weibo/爬取进度/comment_crawl_progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_progress(processed_ids):
    """
    保存爬取进度
    
    Args:
        processed_ids (set): 已处理的微博ID集合
    """
    # 确保目录存在
    os.makedirs('Weibo/爬取进度', exist_ok=True)
    progress_file = 'Weibo/爬取进度/comment_crawl_progress.json'
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(list(processed_ids), f)

def save_location_data():
    """
    将收集的地理定位数据保存到单独的CSV文件
    
    # 函数功能说明：
    # 1. 将全局变量location_data中的地理定位数据整理为DataFrame
    # 2. 保存到CSV文件中
    # 3. 只保存必要的地理位置相关信息
    """
    if location_data:
        # 创建保存目录（如果不存在）
        os.makedirs('Weibo', exist_ok=True)
        
        # 定义输出文件路径
        location_file = 'Weibo/4_可循环包装_地理定位数据.csv'
        
        # 将数据保存为CSV
        location_df = pd.DataFrame(location_data)
        
        # 只保留地理定位相关的必要列
        essential_columns = ['微博唯一ID', '帖子的URL', '地理定位解析结果', '带时区时间格式']
        # 只保留存在的列
        existing_columns = [col for col in essential_columns if col in location_df.columns]
        location_df = location_df[existing_columns]
        
        location_df.to_csv(location_file, index=False, encoding='utf-8-sig')
        print(f"\n地理定位数据已保存到 {location_file}")
        print(f"共收集了 {len(location_data)} 条地理定位数据")

# 添加时间格式转换函数
def format_weibo_time(time_str):
    """
    将微博API返回的英文时间格式转换为标准格式
    
    Args:
        time_str (str): 原始时间字符串，如 "Tue Dec 31 11:28:41 +0800 2024"
        
    Returns:
        str: 格式化后的时间字符串，如 "2024-12-31 11:28:41"
    """
    if not time_str:
        return ""
    
    try:
        # 使用dateutil解析各种时间格式
        dt = parser.parse(time_str)
        # 转换为标准格式的字符串
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"时间格式转换错误: {str(e)}, 原始时间: {time_str}")
        return time_str  # 如果转换失败，返回原始字符串

def process_weibo_data(csv_file):
    """
    处理微博数据，获取每条微博的详细信息和评论数据
    
    # 函数功能说明：
    # 1. 读取包含微博ID的CSV文件
    # 2. 获取每条微博的详细信息（转发量、评论量、点赞量等）
    # 3. 获取每条微博下的评论数据
    # 4. 实时保存数据到CSV文件
    
    Args:
        csv_file: 包含微博ID的CSV文件路径
    """
    # 读取cookie文件，用于模拟登录状态
    try:
        with open('cookie.txt', 'r') as f:
            cookie = f.read().strip()
        print("成功读取cookie文件")
    except Exception as e:
        print(f"读取cookie文件失败: {str(e)}")
        return

    # 设置请求头，模拟浏览器行为
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': cookie,
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'connection': 'keep-alive'
    }
    
    # 加载已处理的微博ID
    processed_ids = load_progress()
    initial_processed_count = len(processed_ids)  # 记录初始已处理数量
    print(f"已处理的微博数: {initial_processed_count}")
    
    # 读取CSV文件
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(csv_file, encoding='gbk')
        except Exception as e:
            print(f"读取CSV文件失败: {str(e)}")
            return
    
    # 确保评价数字段为数值类型
    df['评价数'] = pd.to_numeric(df['评价数'])
    # 筛选评论数>=1的数据
    total_count = len(df)
    df = df[df['评价数'] >= 0]
    filtered_count = len(df)
    
    print(f"总微博数: {total_count}")
    print(f"评论数>=1的微博数: {filtered_count}")
    print(f"已过滤掉 {total_count - filtered_count} 条评论数<1的微博")
    
    # 确保类型一致性
    df['mblogid'] = df['mblogid'].astype(str)
    processed_ids = set(str(id) for id in processed_ids)
    
    # 过滤出未处理的微博ID
    df = df[~df['mblogid'].astype(str).isin(processed_ids)]
    print(f"待处理的微博数: {len(df)}")
    
    # 如果所有微博都已处理，直接返回
    if len(df) == 0:
        print("所有微博都已处理完成！")
        return
    
    # 输出数据基本信息
    print("CSV文件的列名:", df.columns.tolist())
    
    # 存储所有微博详细信息的列表
    weibo_details = []
    
    # 加载已有的微博详情数据（如果存在）
    output_file = 'weibo_details.csv'
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file, encoding='utf-8-sig')
        weibo_details = existing_df.to_dict('records')
    
    # 输出当前使用的请求头信息（调试用）
    # print("当前使用的请求头:", header)
    
    # 遍历处理每条微博
    for index, row in df.iterrows():
        try:
            # 添加一个计数器来记录实际处理的微博数
            processed_count = len(processed_ids)
            mblogid = str(row['mblogid'])
            print(f"\n处理第 {processed_count + 1}/{len(df)} 条微博: {mblogid} (评论数: {row['评价数']})")
            
            # 获取单条微博的详细信息
            try:
                # 构造微博详情API的URL
                test_url = f"https://weibo.com/ajax/statuses/show?id={mblogid}"
                response = requests.get(test_url, headers=header)
                
                # 检查请求是否成功
                if response.status_code != 200:
                    print(f"请求失败，状态码: {response.status_code}")
                    print(f"响应内容: {response.text}")
                    continue  # 改为在失败时记录错误信息
                
                # 解析API返回的JSON数据
                response_json = response.json()
                print(f"成功获取微博基础数据")
                
                # 使用API返回的数据作为基础信息
                basic_info = response_json
                
                if basic_info:
                    # 构建微博详情页面的URL
                    weibo_url = f"https://weibo.com/detail/{mblogid}"
                    
                    # 整理微博基础信息
                    detail = {
                        '帖子的URL': weibo_url,
                        '微博唯一ID': mblogid,
                        '带时区时间格式': format_weibo_time(basic_info.get('created_at', '')),
                        '评论内容': basic_info.get('text_raw', ''),
                        '转发量': basic_info.get('reposts_count', 0),
                        '评论量': basic_info.get('comments_count', 0),
                        '点赞量': basic_info.get('attitudes_count', 0),
                        '地理定位解析结果': basic_info.get('region_name', '')
                    }
                    
                    weibo_details.append(detail)
                    
                    # 将地理定位数据添加到全局变量，只保留必要信息
                    location_info = {
                        '微博唯一ID': mblogid,
                        '帖子的URL': weibo_url,
                        '带时区时间格式': format_weibo_time(basic_info.get('created_at', '')),
                        '地理定位解析结果': basic_info.get('region_name', '')
                    }
                    location_data.append(location_info)
                    
                    # 每处理一条微博后，立即保存一次地理定位数据，确保数据不会丢失
                    save_location_data()
                    
                    try:
                        # 获取该微博下的评论信息
                        print(f"开始获取评论数据...")
                        # 构造评论API的URL
                        comments_url = f"https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={mblogid}&is_show_bulletin=2"
                        comments_response = requests.get(comments_url, headers=header)
                        
                        # 处理评论数据
                        if comments_response.status_code == 200:
                            comments_data = comments_response.json()
                            comments_list = comments_data.get('data', [])
                            
                            # 设置评论数据输出保存路径
                            comments_file = 'Weibo/3_可循环包装_评论数据.csv'
                            
                            # 如果获取到评论数据
                            if comments_list:
                                # 定义评论数据的字段
                                fieldnames = ['帖子的URL', '微博唯一ID', '带时区时间格式', '评论内容', 
                                            '转发量', '评论量', '点赞量', '地理定位解析结果']
                                
                                # 如果评论文件不存在，创建文件并写入表头
                                if not os.path.exists(comments_file):
                                    with open(comments_file, 'w', encoding='utf-8-sig', newline='') as f:
                                        writer = pd.DataFrame(columns=fieldnames)
                                        writer.to_csv(f, index=False)
                                
                                # 处理每条评论
                                for comment in comments_list:
                                    # 整理评论数据
                                    comment_data = {
                                        '帖子的URL': f"https://weibo.com/detail/{mblogid}",
                                        '微博唯一ID': comment.get('id', ''),
                                        '带时区时间格式': format_weibo_time(comment.get('created_at', '')),
                                        '评论内容': comment.get('text_raw', ''),
                                        '转发量': 0,  # 评论通常没有转发数
                                        '评论量': len(comment.get('comments', [])),  # 子评论数量
                                        '点赞量': comment.get('like_counts', 0),
                                        '地理定位解析结果': comment.get('source', '').replace('来自', '')  # 评论来源地
                                    }
                                    
                                    # 将单条评论数据追加到CSV文件
                                    comment_df = pd.DataFrame([comment_data])
                                    comment_df.to_csv(comments_file, mode='a', header=False, index=False, encoding='utf-8-sig')
                                    print(f"已保存一条评论")
                                    
                                    # 添加随机延时，避免请求过快
                                    sleep_time = random.uniform(0.1, 0.3)  # 1-3秒随机延时
                                    time.sleep(sleep_time)
                                
                                # 每批评论处理完后添加较长延时
                                time.sleep(random.uniform(0.5, 1))  # 3-5秒随机延时
                                
                                print(f"评论数据已保存到 {comments_file}")
                            else:
                                print("没有找到评论数据")
                        else:
                            print(f"获取评论失败，状态码: {comments_response.status_code}")
                            
                    except Exception as comment_error:
                        print(f"获取评论时出错: {str(comment_error)}")
                        time.sleep(5)  # 出错时等待较长时间
                        
                else:
                    print(f"未能获取微博数据: {mblogid}")
                
            except requests.RequestException as e:
                print(f"处理微博 {mblogid} 时发生网络请求错误: {str(e)}")
                time.sleep(5)  # 添加延时
                continue
            except json.JSONDecodeError as e:
                print(f"处理微博 {mblogid} 时发生JSON解析错误: {str(e)}")
                print(f"响应内容: {response.text}")
                time.sleep(5)  # 添加延时
                continue
            
            # 每条微博处理完后的延时
            time.sleep(random.uniform(0.5, 1))  # 0.5-1秒随机延时
            
            # 在成功处理完一条微博后，记录进度
            processed_ids.add(mblogid)
            save_progress(processed_ids)
            
        except Exception as e:
            print(f"处理微博 {mblogid} 时发生未知错误: {str(e)}")
            failed_ids.append(mblogid)
            save_progress(processed_ids)
            time.sleep(5)
            continue
    
    # 保存所有微博的详细信息
    if weibo_details:
        result_df = pd.DataFrame(weibo_details)
        output_file = 'weibo_details.csv'
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到 {output_file}")
        print(f"共处理成功 {len(weibo_details)} 条微博")
    else:
        print("没有成功获取任何微博数据")

    # 保存地理定位数据
    save_location_data()
    
    # 在主循环结束后，添加最终统计
    final_processed_count = len(processed_ids)
    newly_processed = final_processed_count - initial_processed_count
    print("\n爬取统计:")
    print(f"本次新增处理: {newly_processed} 条")
    print(f"成功获取: {newly_processed - len(failed_ids)} 条")  # 需要在代码中定义 failed_ids = []
    print(f"失败数量: {len(failed_ids)} 条")

# 主程序入口
if __name__ == "__main__":
    # 设置输入文件路径
    input_csv = "Weibo/1_可循环包装_帖子内容.csv"
    
    try:
        # 执行微博数据处理
        process_weibo_data(input_csv)
    except Exception as e:
        # 异常处理
        print(f"程序执行出错: {str(e)}")