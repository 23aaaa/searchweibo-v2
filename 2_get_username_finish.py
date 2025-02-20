# 导入必要的库
from Euclidweibo.Get_user_info import Get_user_info
import time
from datetime import datetime
import json
import os
import pandas as pd
import random

def load_progress():
    """
    加载断点续爬进度
    
    Returns:
        set: 已处理过的用户ID集合
    """
    progress_file = 'Weibo/爬取进度/user_crawl_progress.json'
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_progress(processed_ids):
    """
    保存爬取进度
    
    Args:
        processed_ids (set): 已处理的用户ID集合
    """
    progress_file = 'Weibo/爬取进度/user_crawl_progress.json'
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(list(processed_ids), f)

def batch_get_user_info(user_ids):
    """
    批量获取微博用户信息的主函数
    
    # 函数功能说明：
    # 1. 遍历用户ID列表，逐个获取用户信息
    # 2. 对每个用户的信息进行格式化处理
    # 3. 实时保存处理结果到CSV文件
    # 4. 记录处理失败的用户ID
    
    Args:
        user_ids: 包含用户ID的列表
    """
    # 加载已处理的用户ID
    processed_ids = load_progress()
    print(f"已处理的用户数: {len(processed_ids)}")
    
    # 过滤出未处理的用户ID
    remaining_ids = [uid for uid in user_ids if str(uid) not in processed_ids]
    print(f"待处理的用户数: {len(remaining_ids)}")
    
    # 如果所有用户都已处理，直接返回
    if not remaining_ids:
        print("所有用户都已处理完成！")
        return
    
    # 初始化结果列表和失败ID列表
    results = []
    total = len(remaining_ids)
    failed_ids = []
    
    # 设定输出文件路径和输出文件名称
    output_csv = 'Weibo/user_info_results.csv'
    
    # 如果已有结果文件，加载已有结果
    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv)
        results = existing_df.to_dict('records')
    
    # 遍历处理每个用户ID
    for index, uid in enumerate(remaining_ids, 1):
        try:
            print(f"正在处理 {index}/{total}: UID {uid}")
            
            # 修改为0.5-1秒的随机延时
            time.sleep(random.uniform(0.5, 1.0))
            
            # 调用API获取用户信息
            user_info = Get_user_info(uid)
            
            # 从返回的数据中提取user字段
            user_data = user_info.get('user', {})
            
            # 构建标准化的用户数据字典
            row = {
                '用户主页的URL': f"https://weibo.com/u/{uid}",
                '唯一ID': uid,
                '用户粉丝数': user_data.get('followers_count', ''),
                '用户生日': '',  # API中没有返回生日字段
                '用户性别': '女' if user_data.get('gender') == 'f' else '男' if user_data.get('gender') == 'm' else '未知',
                '用户个人主页显示的地址': user_data.get('location', ''),
                '用户的认证状态': '已认证' if user_data.get('verified') else '未认证',
                '认证类型': user_data.get('verified_type', ''),
                '用户地址': user_data.get('location', '')
            }
            
            # 将处理结果添加到结果列表
            results.append(row)
            
            # 实时保存当前所有结果到CSV文件
            df = pd.DataFrame(results)
            df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            
            # 记录处理成功的ID并保存进度
            processed_ids.add(str(uid))
            save_progress(processed_ids)
            
            print(f"已保存用户 {uid} 的信息到 {output_csv}")
            
        except Exception as e:
            # 异常处理：记录失败的用户ID并延长等待时间
            print(f"获取用户 {uid} 信息失败: {str(e)}")
            failed_ids.append(uid)
            # 失败时仍然保持较长的等待时间
            time.sleep(random.uniform(3, 5))
    
    # 输出处理结果统计
    print(f"\n处理完成！")
    print(f"成功获取: {len(results)}/{total} 个用户信息")
    if failed_ids:
        print(f"失败的用户ID: {failed_ids}")
        # 将失败的ID保存到文件
        with open('Weibo/failed_ids.json', 'w', encoding='utf-8') as f:
            json.dump(failed_ids, f)

def save_results(results, filename):
    """
    将结果保存到JSON文件
    
    # 函数功能说明：
    # 1. 将处理结果以JSON格式保存
    # 2. 确保中文正确保存
    # 3. 保持良好的文件可读性
    
    Args:
        results: 要保存的结果字典
        filename: 保存的文件名
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # ensure_ascii=False 确保中文能够正确保存
        # indent=2 使JSON文件具有较好的可读性
        json.dump(results, f, ensure_ascii=False, indent=2)

def process_user_info(json_file, output_csv):
    """
    将用户信息JSON文件转换为CSV格式
    
    # 函数功能说明：
    # 1. 读取JSON格式的用户信息
    # 2. 将数据转换为标准化的表格格式
    # 3. 保存为CSV文件
    
    Args:
        json_file: 输入的JSON文件名
        output_csv: 输出的CSV文件名
    """
    # 读取JSON数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化数据行列表
    rows = []
    
    # 处理每个用户的数据
    for user_id, user_data in data.items():
        user_info = user_data.get('user', {})
        
        # 构建用户主页URL
        profile_url = f"https://weibo.com/u/{user_id}"
        
        # 提取并格式化用户信息
        row = {
            '用户主页的URL': profile_url,
            '唯一ID': user_id,
            '用户粉丝数': user_info.get('followers_count', ''),
            '用户生日': user_info.get('birthday', ''),
            '用户性别': '女' if user_info.get('gender') == 'f' else '男' if user_info.get('gender') == 'm' else '未知',
            '用户个人主页显示的地址': user_info.get('location', ''),
            '用户的认证状态': '已认证' if user_info.get('verified') else '未认证',
            '认证类型': user_info.get('verified_type', ''),
            '用户地址': user_info.get('location', '')
        }
        rows.append(row)
    
    # 创建DataFrame并保存为CSV
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"数据已保存到 {output_csv}")

# 主程序入口
if __name__ == "__main__":
    # 读取包含用户ID的CSV文件
    input_csv = "Weibo/快递回收.csv"
    df = pd.read_csv(input_csv)
    
    # 获取不重复的用户ID列表
    test_ids = df['uid'].unique().tolist()
    
    try:
        # 执行批量获取用户信息（支持断点续爬）
        batch_get_user_info(test_ids)
        print("所有结果已保存到 user_info_results.csv")
    except Exception as e:
        # 异常处理
        print(f"程序执行出错: {str(e)}")
