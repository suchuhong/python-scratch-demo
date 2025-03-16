"""
电影天堂网站爬虫 - 兼容版
适用于最新版Chrome，不依赖webdriver_manager
"""
import os
import sys
import time
import csv
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)


class Dytt8Scraper:
    """电影天堂爬虫 - 兼容版"""
    
    def __init__(self, headless: bool = False, disable_images: bool = False):
        """
        初始化爬虫
        
        Args:
            headless: 是否使用无头模式（无浏览器界面）
            disable_images: 是否禁用图片加载以提高性能
        """
        self.base_url = "https://www.dytt8.com/"
        self.results = []
        
        # 设置Chrome选项
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
        
        # 基本设置
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-allow-origins=*")  # 解决跨域问题
        
        # 隐藏自动化特征
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 禁用图片加载提高性能
        if disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # 直接使用Selenium 4的新特性，自动管理驱动程序
        print("正在初始化Chrome浏览器...")
        self.driver = webdriver.Chrome(options=options)
        print("Chrome浏览器初始化成功!")
    
    def __del__(self):
        """析构函数 - 确保浏览器关闭"""
        if hasattr(self, 'driver'):
            print("关闭浏览器...")
            self.driver.quit()
    
    def fix_encoding(self, text: str) -> str:
        """修复中文乱码问题"""
        if not text:
            return ""
        
        try:
            return text.encode('latin1').decode('utf-8')
        except:
            try:
                return text.encode('latin1').decode('gbk')
            except:
                return text
    
    def open_website(self) -> bool:
        """打开电影天堂网站"""
        try:
            print(f"正在访问电影天堂网站: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            print("成功打开电影天堂网站")
            return True
        except Exception as e:
            print(f"打开网站失败: {e}")
            return False
    
    def browse_movies_by_category(self, category: str = "最新电影") -> List[Dict[str, Any]]:
        """
        按类别浏览电影
        
        Args:
            category: 电影类别，如"最新电影"、"国内电影"等
            
        Returns:
            包含电影信息的字典列表
        """
        if not self.open_website():
            return []
        
        movies = []
        try:
            print(f"正在浏览类别: {category}")
            
            # 尝试查找类别链接
            category_found = False
            try:
                # 查找所有可能的类别链接
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    link_text = self.fix_encoding(link.text).strip()
                    if category in link_text:
                        print(f"找到类别: {link_text}")
                        link.click()
                        category_found = True
                        time.sleep(2)  # 等待页面加载
                        break
            except Exception as e:
                print(f"查找类别时出错: {e}")
            
            if not category_found:
                print(f"找不到类别: {category}，将显示首页电影")
            
            # 收集电影信息
            try:
                print("正在收集电影信息...")
                movie_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.html')]")
                
                for link in movie_links[:50]:  # 处理前50个链接
                    try:
                        title = self.fix_encoding(link.text).strip()
                        href = link.get_attribute("href")
                        
                        # 过滤无效链接
                        if (not title or len(title) < 5 or 
                            "index" in href or "list" in href or
                            "html" not in href):
                            continue
                        
                        # 提取年份
                        year_match = re.search(r'(20\d{2}|19\d{2})', title)
                        year = year_match.group(0) if year_match else "未知年份"
                        
                        # 将电影添加到列表中
                        movies.append({
                            "title": title,
                            "year": year,
                            "link": href,
                            "category": category
                        })
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"收集电影信息时出错: {e}")
            
            print(f"找到 {len(movies)} 部电影")
            
            # 获取每部电影的详细信息
            movies_with_details = []
            for i, movie in enumerate(movies[:20], 1):  # 只处理前20部电影
                print(f"正在获取第 {i}/{min(20, len(movies))} 部电影的详情: {movie['title']}")
                details = self.get_movie_details(movie['link'])
                movie.update(details)
                movies_with_details.append(movie)
                time.sleep(1)  # 避免请求过于频繁
            
            return movies_with_details
        except Exception as e:
            print(f"浏览电影类别时出错: {e}")
            return []
    
    def search_movie(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索电影
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            包含搜索结果的字典列表
        """
        if not self.open_website():
            return []
        
        try:
            print(f"正在搜索电影: {keyword}")
            
            # 使用网站URL直接搜索
            search_url = f"{self.base_url}/plus/search.php?kwtype=0&searchtype=title&keyword={keyword}"
            self.driver.get(search_url)
            time.sleep(2)  # 等待搜索结果加载
            
            # 收集搜索结果
            results = []
            
            try:
                # 查找搜索结果链接
                result_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.html')]")
                
                for link in result_links:
                    try:
                        title = self.fix_encoding(link.text).strip()
                        href = link.get_attribute("href")
                        
                        # 过滤无效链接
                        if (not title or len(title) < 5 or 
                            "index" in href or "list" in href or
                            "search" in href):
                            continue
                        
                        # 提取年份
                        year_match = re.search(r'(20\d{2}|19\d{2})', title)
                        year = year_match.group(0) if year_match else "未知年份"
                        
                        # 将结果添加到列表中
                        results.append({
                            "title": title,
                            "year": year,
                            "link": href,
                            "source": "search"
                        })
                    except:
                        continue
            except Exception as e:
                print(f"处理搜索结果时出错: {e}")
            
            print(f"找到 {len(results)} 个搜索结果")
            
            # 获取每个结果的详细信息
            results_with_details = []
            for i, result in enumerate(results[:10], 1):  # 只处理前10个结果
                print(f"正在获取第 {i}/{min(10, len(results))} 个结果的详情: {result['title']}")
                details = self.get_movie_details(result['link'])
                result.update(details)
                results_with_details.append(result)
                time.sleep(1)  # 避免请求过于频繁
            
            return results_with_details
            
        except Exception as e:
            print(f"搜索电影时出错: {e}")
            return []
    
    def get_movie_details(self, movie_link: str) -> Dict[str, Any]:
        """
        获取电影详情
        
        Args:
            movie_link: 电影详情页URL
            
        Returns:
            包含电影详情的字典
        """
        try:
            print(f"获取电影详情: {movie_link}")
            
            self.driver.get(movie_link)
            time.sleep(2)  # 等待页面加载
            
            # 初始化结果字典
            details = {
                "download_link": "",
                "description": "",
                "cover_image": "",
                "director": "",
                "actors": [],
                "rating": "",
                "release_date": ""
            }
            
            # 获取下载链接
            try:
                # 查找下载链接
                link_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'magnet:') or contains(@href, 'ed2k:') or contains(@href, 'thunder:')]")
                if link_elements:
                    details["download_link"] = link_elements[0].get_attribute("href")
                else:
                    # 尝试其他可能的下载链接位置
                    td_elements = self.driver.find_elements(By.XPATH, "//td[@bgcolor='#fdfddf']/a")
                    if td_elements:
                        details["download_link"] = td_elements[0].get_attribute("href")
            except Exception as e:
                print(f"获取下载链接时出错: {e}")
            
            # 获取电影描述
            try:
                desc_elements = self.driver.find_elements(By.XPATH, "//div[@id='Zoom']")
                if desc_elements:
                    description = self.fix_encoding(desc_elements[0].text)
                    details["description"] = description
                    
                    # 尝试从描述中提取更多信息
                    try:
                        # 提取导演
                        director_match = re.search(r'导　　演(.*?)(?:\n|$)', description)
                        if director_match:
                            details["director"] = director_match.group(1).strip()
                        
                        # 提取主演
                        actors_match = re.search(r'主　　演(.*?)(?:◎|$)', description, re.DOTALL)
                        if actors_match:
                            actors_text = actors_match.group(1).strip()
                            actors = [actor.strip() for actor in actors_text.split('\n') if actor.strip()]
                            details["actors"] = actors
                        
                        # 提取评分
                        rating_match = re.search(r'(?:豆瓣评分|IMDB评分)[^\d]*([\d\.]+)', description)
                        if rating_match:
                            details["rating"] = rating_match.group(1).strip()
                        
                        # 提取上映日期
                        date_match = re.search(r'上映日期(.*?)(?:\n|$)', description)
                        if date_match:
                            details["release_date"] = date_match.group(1).strip()
                    except Exception as e:
                        print(f"提取电影元数据时出错: {e}")
            except Exception as e:
                print(f"获取电影描述时出错: {e}")
            
            # 获取封面图片
            try:
                img_elements = self.driver.find_elements(By.XPATH, "//div[@id='Zoom']//img")
                if img_elements:
                    details["cover_image"] = img_elements[0].get_attribute("src")
            except Exception as e:
                print(f"获取封面图片时出错: {e}")
            
            return details
            
        except Exception as e:
            print(f"获取电影详情时出错: {e}")
            return {"download_link": "", "description": "", "cover_image": ""}
    
    def scrape_latest_movies(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        抓取最新电影
        
        Args:
            limit: 最大抓取数量
            
        Returns:
            包含电影信息的字典列表
        """
        return self.browse_movies_by_category("最新电影")[:limit]
    
    def export_to_csv(self, movies: List[Dict[str, Any]], filename: str = "movies.csv") -> str:
        """
        将电影信息导出到CSV文件
        
        Args:
            movies: 电影信息列表
            filename: 输出文件名
            
        Returns:
            保存的文件路径
        """
        if not movies:
            print("没有电影信息可导出")
            return ""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"{filename}_{timestamp}.csv"
            
            print(f"正在导出 {len(movies)} 部电影信息到 {filepath}")
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ["title", "year", "director", "rating", "download_link", 
                             "description", "cover_image", "category", "release_date"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for movie in movies:
                    # 只写入指定的字段
                    movie_data = {field: movie.get(field, "") for field in fieldnames}
                    writer.writerow(movie_data)
            
            print(f"电影信息已成功导出到 {filepath}")
            return filepath
        except Exception as e:
            print(f"导出到CSV文件时出错: {e}")
            return ""


def main():
    """主函数"""
    print("电影天堂网站爬虫启动...")
    
    # 创建爬虫实例
    scraper = Dytt8Scraper(headless=False, disable_images=True)
    
    while True:
        print("\n请选择要抓取的电影/电视剧类别:")
        print("1. 最新电影")
        print("2. 国内电影")
        print("3. 欧美电影")
        print("4. 日韩电影")
        print("5. 华语电视")
        print("6. 欧美电视")
        print("7. 日韩电视")
        print("8. 搜索电影")
        print("0. 退出程序")
        
        choice = input("请输入类别编号 (默认为最新电影): ").strip() or "1"
        
        if choice == "0":
            break
        
        # 映射类别编号到类别名称
        categories = {
            "1": "最新电影",
            "2": "国内电影",
            "3": "欧美电影",
            "4": "日韩电影",
            "5": "华语电视",
            "6": "欧美电视",
            "7": "日韩电视"
        }
        
        results = []
        
        if choice == "8":
            # 搜索电影
            keyword = input("请输入要搜索的电影名称: ").strip()
            if keyword:
                results = scraper.search_movie(keyword)
            else:
                print("搜索关键词不能为空")
                continue
        elif choice in categories:
            # 按类别浏览
            selected_category = categories[choice]
            results = scraper.browse_movies_by_category(selected_category)
        else:
            print("无效的选项")
            continue
        
        if not results:
            print("没有找到符合条件的电影")
            continue
        
        # 显示结果
        print("\n找到以下电影:")
        for i, movie in enumerate(results, 1):
            print(f"{i}. {movie['title']} ({movie.get('year', '未知')})")
            if movie.get('rating'):
                print(f"   评分: {movie['rating']}")
            if movie.get('director'):
                print(f"   导演: {movie['director']}")
            if movie.get('download_link'):
                print(f"   下载链接: {movie['download_link']}")
            print()
        
        # 询问是否导出结果
        export = input("是否导出结果到CSV文件? (y/n): ").strip().lower()
        if export == 'y':
            filename = input("请输入文件名 (默认为'movies'): ").strip() or "movies"
            scraper.export_to_csv(results, filename)
    
    print("电影天堂网站爬虫已关闭")


if __name__ == "__main__":
    main() 