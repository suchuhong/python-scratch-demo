#!/usr/bin/env python
"""
电影天堂工具集演示脚本
"""
import os
import sys
import time
from datetime import datetime

def print_header():
    """打印标题"""
    print("\n" + "=" * 60)
    print("              电影天堂工具集演示")
    print("=" * 60)
    print("\n此脚本将演示电影天堂工具集的主要功能。")
    print("注意: 为了避免对网站造成负担，演示脚本将使用模拟数据。")

def demo_scraper():
    """演示基础爬虫功能"""
    print("\n" + "-" * 60)
    print("演示 1: 基础爬虫功能")
    print("-" * 60)
    
    try:
        from dytt8.core import MovieScraper
        print("✓ 成功导入 MovieScraper 类")
        
        print("\n模拟爬取最新电影...")
        print("电影1: 《流浪地球3》 - [科幻/冒险] - 9.2分")
        print("电影2: 《速度与激情X》 - [动作/犯罪] - 8.6分")
        print("电影3: 《复仇者联盟5》 - [科幻/动作] - 9.0分")
        print("...")
        print("共模拟爬取 10 部电影")
        
        print("\n将结果保存到 CSV 文件...")
        output_file = f"movies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        print(f"✓ 数据已保存到文件: {output_file}")
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    
    return True

def demo_movie_finder():
    """演示电影搜索功能"""
    print("\n" + "-" * 60)
    print("演示 2: 电影搜索功能")
    print("-" * 60)
    
    try:
        from dytt8.core import MovieFinder
        print("✓ 成功导入 MovieFinder 类")
        
        search_term = "复仇者联盟"
        print(f"\n搜索电影: {search_term}")
        print("搜索结果:")
        print("1. 《复仇者联盟4：终局之战》")
        print("   - 导演: 安东尼·罗素, 乔·罗素")
        print("   - 主演: 小罗伯特·唐尼, 克里斯·埃文斯, 克里斯·海姆斯沃斯")
        print("   - 下载链接: https://www.example.com/avengers_endgame.html")
        print("   - 评分: 9.1")
        print("\n2. 《复仇者联盟3：无限战争》")
        print("   - 导演: 安东尼·罗素, 乔·罗素")
        print("   - 主演: 小罗伯特·唐尼, 克里斯·海姆斯沃斯, 克里斯·埃文斯")
        print("   - 下载链接: https://www.example.com/avengers_infinity_war.html")
        print("   - 评分: 8.9")
        print("\n共找到 5 部符合条件的电影")
    
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    
    return True

def demo_gui():
    """演示图形界面功能"""
    print("\n" + "-" * 60)
    print("演示 3: 图形界面功能")
    print("-" * 60)
    
    print("图形界面需要使用 tkinter 包，无法在此演示。")
    print("您可以通过以下命令启动图形界面:")
    print("  dytt8-gui")
    
    return True

def demo_api():
    """演示API功能"""
    print("\n" + "-" * 60)
    print("演示 4: API功能")
    print("-" * 60)
    
    print("API服务器将启动一个Web服务，提供以下接口:")
    print("- GET  /api/movies        - 获取所有电影列表")
    print("- GET  /api/movies/{id}   - 获取指定ID的电影详情")
    print("- POST /api/movies/search - 搜索电影")
    print("- GET  /api/scrape        - 触发电影抓取任务")
    
    print("\n您可以通过以下命令启动API服务器:")
    print("  dytt8-full --api --port 8000")
    
    return True

def main():
    """主函数"""
    print_header()
    
    # 检查是否安装了dytt8包
    try:
        import dytt8
        print(f"✓ 已安装电影天堂工具集 (版本: {dytt8.__version__})")
    except ImportError:
        print("✗ 未安装电影天堂工具集")
        print("  请先安装: pip install -e .")
        return
    
    # 运行演示
    demo_scraper()
    time.sleep(1)
    
    demo_movie_finder()
    time.sleep(1)
    
    demo_gui()
    time.sleep(1)
    
    demo_api()
    
    print("\n" + "=" * 60)
    print("              演示完成")
    print("=" * 60)
    print("\n感谢使用电影天堂工具集！")

if __name__ == "__main__":
    main() 