# 导入必要的库
from Euclidweibo.Get_user_info import Get_user_info  # 获取基本信息（包含准确粉丝数）
from Euclidweibo.Get_user_info_v2 import Get_user_info_v2  # 获取详细信息（包含生日等）
import time
from datetime import datetime
import json
import os
import pandas as pd
import random
import re

def load_progress():
    """user_info_results
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
    initial_results_count = 0  # 新增：记录初始结果数量
    total = len(remaining_ids)
    failed_ids = []

    
    # 如果已有结果文件，加载已有结果
    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv)
        results = existing_df.to_dict('records')
        initial_results_count = len(results)  # 新增：保存初始结果数量
    
    # 遍历处理每个用户ID
    for index, uid in enumerate(remaining_ids, 1):
        try:
            print(f"正在处理 {index}/{total}: UID {uid}")
            
            # 修改为0.5-1秒的随机延时
            time.sleep(random.uniform(0.5, 1.0))
            
            # 1. 首先获取详细信息(生日、简介等)
            detail_info = Get_user_info_v2(uid)
            # print(f"已获取详细信息 API 数据")
            
            # 2. 获取基本信息(粉丝数等)
            time.sleep(random.uniform(0.5, 1.0))  # 两次请求间增加延时
            basic_info = Get_user_info(uid)
            # print(f"已获取基本信息 API 数据")
            
            # 3. 合并两个API的结果
            # 创建一个新的字典来存储合并后的数据
            user_info = detail_info.copy()
            
            # 如果详细信息中没有user字段，但基本信息中有，则添加
            if 'user' not in user_info and 'user' in basic_info:
                user_info['user'] = basic_info['user']
            
            # 提取basic_info中的粉丝数等关键数据
            if 'user' in basic_info:
                basic_user = basic_info['user']
                if 'user' in user_info:
                    # 如果粉丝数在basic_info中存在且有效，则使用它
                    if 'followers_count' in basic_user and basic_user['followers_count'] > 0:
                        user_info['user']['followers_count'] = basic_user['followers_count']
                    
                    # 同样处理好友数量
                    if 'friends_count' in basic_user and basic_user['friends_count'] > 0:
                        user_info['user']['friends_count'] = basic_user['friends_count']
            
            # 打印原始数据，帮助调试
            # print(f"合并后数据: {json.dumps(user_info, ensure_ascii=False)[:300]}...")
            
            # 保留user_data变量，但主要使用user_info直接提取数据
            user_data = user_info.get('user', {})
            # 获取basic_info中的user数据
            basic_user_data = basic_info.get('user', {})
            
            # 构建标准化的用户数据字典，补充更多详细信息
            row = {
                '用户主页的URL': f"https://weibo.com/u/{uid}",
                '唯一ID': uid,
                # 粉丝数：优先从user_data中获取，如无则尝试其他方法
                '用户粉丝数': user_data.get('followers_count', '') or extract_followers_count_from_all_sources(user_info),
                # 好友数：优先从user_data中获取，如无则尝试从friend_info提取
                '用户好友数': user_data.get('friends_count', '') or extract_friends_count(user_info),
                # 生日信息从detail_info获取
                '用户生日': user_info.get('birthday', ''),
                '用户性别': '女' if user_info.get('gender') == 'f' else '男' if user_info.get('gender') == 'm' else '未知',
                '用户所在地': user_info.get('location', '') or user_data.get('location', ''),
                '用户的认证状态': '已认证' if user_info.get('verified_url', '') or user_data.get('verified', False) else '未认证',
                '认证类型': determine_verified_type(user_info.get('verified_url', '')),
                '用户信用等级': user_info.get('sunshine_credit', {}).get('level', ''),
                '账号创建时间': user_info.get('created_at', ''),
                '个人描述': user_info.get('description', '') or user_data.get('description', ''),
                '实名认证': determine_real_auth_status(user_info),
                '公司': user_info.get('company', '') or user_info.get('career', {}).get('company', ''),
                '学校': user_info.get('education', {}).get('school', ''),
                '标签': ', '.join([label.get('name', '') for label in user_info.get('label_desc', []) if 'name' in label]) if user_info.get('label_desc') else '',
                '描述文本': user_info.get('desc_text', '')
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
    
    # 读取爬取进度文件
    progress_file = 'Weibo/爬取进度/user_crawl_progress.json'
    with open(progress_file, 'r', encoding='utf-8') as f:
        crawled_ids = json.load(f)
    
    total = len(user_ids)  # 总需要处理的用户数
    success_count = len(crawled_ids)  # 成功爬取的用户数
    failed_count = total - success_count  # 失败的用户数
    
    # 输出处理结果统计
    print(f"\n处理完成！")
    print(f"成功获取: {success_count}/{total} 个用户信息")
    print(f"失败数量: {failed_count}")
    
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
            '用户地址': user_info.get('location', ''),
            '用户信用等级': user_data.get('sunshine_credit', {}).get('level', '')
        }
        
        # 添加生日字段
        if 'birthday' in user_info:
            row['用户生日'] = user_info.get('birthday', '')
            
        # 添加信用等级字段
        sunshine_credit = user_info.get('sunshine_credit', {})
        row['用户信用等级'] = sunshine_credit.get('level', '') if sunshine_credit else ''
        
        rows.append(row)
    
    # 创建DataFrame并保存为CSV
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"数据已保存到 {output_csv}")

# 添加这个辅助函数到文件中，放在其他函数定义之前
def determine_verified_type(verified_url):
    """
    根据verified_url判断认证类型
    
    Args:
        verified_url (str): 认证URL
    
    Returns:
        str: 认证类型描述
    """
    if not verified_url:
        return '未认证'
    
    # 商业认证
    if 'bluev' in verified_url or 'biz.weibo.com' in verified_url:
        return '企业认证'
    
    # 个人认证
    if 'verified.weibo.com' in verified_url:
        return '个人认证'
    
    # 其他类型认证
    return '已认证'

# 添加这个新的辅助函数，放在determine_verified_type函数后面
def determine_real_auth_status(user_info):
    """
    综合判断用户的实名认证状态
    
    Args:
        user_info (dict): 用户信息数据
    
    Returns:
        str: 实名认证状态描述
    """
    # 如果明确标记为已实名认证
    if user_info.get('real_auth') is True:
        return '是'
    
    # 如果有认证URL，通常也意味着实名认证
    if user_info.get('verified_url', ''):
        return '是'
        
    # 检查实名信息是否存在
    real_name = user_info.get('real_name', {})
    if real_name and (real_name.get('name') or real_name.get('career')):
        return '是'
    
    # 默认情况下返回否
    return '否'

# 完全重写粉丝数提取函数
def extract_followers_count_from_all_sources(user_info):
    """
    综合多种方法提取粉丝数
    
    Args:
        user_info (dict): 用户信息数据
    
    Returns:
        str: 粉丝数量
    """
    import re
    
    # 首先尝试从标签中找粉丝数，最可能包含真实数据
    if user_info.get('label_desc'):
        for label in user_info.get('label_desc', []):
            label_name = label.get('name', '')
            
            # 尝试匹配"粉丝数xx万+"的格式
            fans_match = re.search(r'粉丝数(\d+(\.\d+)?)万\+', label_name)
            if fans_match:
                fans_count = float(fans_match.group(1)) * 10000
                return str(int(fans_count))
                
            # 尝试匹配"xx万粉丝"格式
            fans_match = re.search(r'(\d+(\.\d+)?)\s*万粉丝', label_name)
            if fans_match:
                fans_count = float(fans_match.group(1)) * 10000
                return str(int(fans_count))
                
            # 尝试匹配"粉丝xx"格式
            fans_match = re.search(r'粉丝\s*(\d+)', label_name)
            if fans_match:
                return fans_match.group(1)
                
            # 尝试匹配"xx粉丝"格式(不带万字)
            fans_match = re.search(r'(\d+)\s*粉丝', label_name)
            if fans_match:
                return fans_match.group(1)
    
    # 从描述文本中可能包含的粉丝信息提取
    desc_text = user_info.get('desc_text', '')
    if desc_text:
        # 匹配描述中可能出现的粉丝数
        fans_match = re.search(r'(\d+(\.\d+)?)\s*万粉丝', desc_text)
        if fans_match:
            fans_count = float(fans_match.group(1)) * 10000
            return str(int(fans_count))
    
    # 尝试从个人描述中提取
    description = user_info.get('description', '')
    if description:
        # 匹配描述中可能出现的粉丝数
        fans_match = re.search(r'(\d+(\.\d+)?)\s*万粉丝', description)
        if fans_match:
            fans_count = float(fans_match.group(1)) * 10000
            return str(int(fans_count))
    
    # 最后才从API返回的followers字段获取，因为可能为0
    followers = user_info.get('followers', {})
    if followers and isinstance(followers, dict) and 'total_number' in followers:
        return str(followers.get('total_number', ''))
    
    return ''

# 添加提取好友数的专用函数
def extract_friends_count(user_info):
    """
    提取好友数量
    
    Args:
        user_info (dict): 用户信息数据
    
    Returns:
        str: 好友数
    """
    friend_info = user_info.get('friend_info', '')
    
    # 处理字符串中的<a>标签
    if isinstance(friend_info, str) and friend_info:
        import re
        # 处理"他有 <a>xxx</a> 个好友"或"她有 <a>xxx</a> 个好友"的格式
        match = re.search(r'[他她]有\s*<a>(\d+)</a>', friend_info)
        if match:
            return match.group(1)
        
        # 处理"他有 <a>xxx"的格式(缺少结束标签)
        match = re.search(r'[他她]有\s*<a>(\d+)', friend_info)
        if match:
            return match.group(1)
    
    # 检查是否有别的位置存储好友数
    # 有些接口可能会直接返回数字
    if isinstance(friend_info, int) and friend_info > 0:
        return str(friend_info)
    
    return ''

# 主程序入口
if __name__ == "__main__":
    # 读取包含用户ID的CSV文件
    input_csv = "Weibo/1_可循环包装_帖子内容.csv"
    df = pd.read_csv(input_csv)
    
    # 获取不重复的用户ID列表
    test_ids = df['uid'].unique().tolist()
        
    # 设定输出文件路径和输出文件名称
    output_csv = 'Weibo/2_可循环包装_用户信息内容.csv'

    try:
        # 执行批量获取用户信息（支持断点续爬）
        batch_get_user_info(test_ids)
        print("所有结果已保存到 可循环包装_用户信息内容.csv")
    except Exception as e:
        # 异常处理
        print(f"程序执行出错: {str(e)}")
