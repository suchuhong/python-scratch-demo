"""
电影天堂网站抓取器 - 基于 Selenium 的网站自动化脚本
用于从电影天堂网站(https://www.dytt8.com/)抓取电影信息
处理特殊字符编码问题并提取电影数据
"""
import os
import sys
import time
import csv
import re
from datetime import datetime
from urllib.parse import urljoin

# 导入父目录的工具函数
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    setup_chrome_driver,
    wait_for_element,
    safe_click,
    get_element_text
)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class Dytt8Scraper:
    """电影天堂网站爬虫类"""
    
    def __init__(self, headless=True, disable_images=True):
        """初始化爬虫"""
        self.base_url = "https://www.dytt8.com/"
        self.driver = setup_chrome_driver(headless=headless, disable_images=disable_images)
        # 解决中文乱码问题的配置
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "languages", {get: function() {return ["zh-CN", "zh", "en"]}})'
        })
        
    def __del__(self):
        """析构函数 - 确保浏览器关闭"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def open_website(self):
        """打开电影天堂网站"""
        try:
            self.driver.get(self.base_url)
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("成功打开电影天堂网站")
            return True
        except Exception as e:
            print(f"打开网站失败: {e}")
            return False
    
    def fix_encoding(self, text):
        """修复中文乱码问题"""
        if not text:
            return ""
        
        # 尝试不同的编码方式
        try:
            # 对于某些特殊情况下的编码修复
            return text.encode('latin1').decode('utf-8')
        except:
            try:
                # 对于某些特殊情况下的编码修复
                return text.encode('latin1').decode('gbk')
            except:
                # 如果无法修复，则返回原始文本
                return text
    
    def extract_movie_info(self, movie_element):
        """从电影元素中提取信息"""
        try:
            # 提取电影标题和年份
            title_element = movie_element.find_element(By.TAG_NAME, "a")
            title_text = title_element.text
            
            # 修复编码
            title_text = self.fix_encoding(title_text)
            
            # 使用正则表达式提取年份
            year_match = re.search(r'(20\d{2}|19\d{2})', title_text)
            year = year_match.group(0) if year_match else "未知年份"
            
            # 清理标题
            title = re.sub(r'《|》|\(.*?\)|\[.*?\]|20\d{2}|19\d{2}', '', title_text).strip()
            
            # 获取电影详情页链接
            movie_link = title_element.get_attribute("href")
            
            return {
                "title": title,
                "year": year,
                "link": movie_link,
                "raw_title": title_text
            }
        except Exception as e:
            print(f"提取电影信息时出错: {e}")
            return None
    
    def get_movie_details(self, movie_info):
        """访问电影详情页获取更多信息"""
        try:
            # 访问电影详情页
            self.driver.get(movie_info["link"])
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 提取下载链接 (多种可能的选择器适应网站不同版面)
            download_link = None
            selectors = [
                "//a[contains(@href, 'magnet:')]",
                "//a[contains(@href, 'thunder:')]",
                "//a[contains(@href, 'ed2k:')]",
                "//a[contains(@href, '.torrent')]",
                "//a[contains(text(), '下载')]",
                "//a[contains(text(), '磁力')]",
                "//a[contains(text(), '迅雷')]",
                "//td[@bgcolor='#fdfddf']/a"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        download_link = elements[0].get_attribute("href")
                        break
                except:
                    continue
            
            # 提取电影描述信息
            description = ""
            try:
                # 尝试找到包含电影描述的元素
                desc_element = self.driver.find_element(By.XPATH, "//div[@id='Zoom']")
                if desc_element:
                    description = desc_element.text
                    description = self.fix_encoding(description)
            except:
                pass
            
            # 提取封面图片URL
            cover_image = ""
            try:
                img_elements = self.driver.find_elements(By.XPATH, "//div[@id='Zoom']//img")
                if img_elements:
                    cover_image = img_elements[0].get_attribute("src")
            except:
                pass
            
            # 更新电影信息
            movie_info.update({
                "download_link": download_link,
                "description": description,
                "cover_image": cover_image
            })
            
            return movie_info
        except Exception as e:
            print(f"获取电影详情时出错: {e}")
            return movie_info
    
    def scrape_latest_movies(self, max_pages=3, category=None):
        """抓取最新电影列表"""
        all_movies = []
        current_page = 1
        
        # 打开网站
        if not self.open_website():
            return all_movies
        
        # 如果指定了类别，先切换到相应类别
        if category:
            try:
                # 尝试按类别筛选
                category_links = self.driver.find_elements(By.XPATH, f"//a[contains(text(), '{category}')]")
                if category_links:
                    safe_click(self.driver, category_links[0])
                    # 等待页面加载
                    time.sleep(2)
                else:
                    print(f"找不到类别: {category}")
            except Exception as e:
                print(f"切换类别时出错: {e}")
        
        # 开始抓取电影列表
        try:
            while current_page <= max_pages:
                print(f"正在抓取第 {current_page} 页...")
                
                # 找到电影列表
                movie_elements = []
                try:
                    # 尝试不同的选择器找到电影列表
                    selectors = [
                        "//div[@class='co_content8']//td//a[contains(@href, '.html')]",
                        "//div[@class='co_content8']//table//a[contains(@href, '.html')]",
                        "//a[contains(@href, '.html')]"
                    ]
                    
                    for selector in selectors:
                        movie_elements = self.driver.find_elements(By.XPATH, selector)
                        if movie_elements:
                            break
                except:
                    pass
                
                # 如果找不到电影元素，则退出循环
                if not movie_elements:
                    print("找不到电影列表元素")
                    break
                
                # 处理找到的电影元素
                for element in movie_elements:
                    try:
                        # 排除导航链接
                        href = element.get_attribute("href")
                        if not href or "index.html" in href or "list" in href:
                            continue
                        
                        # 创建基本电影信息
                        movie = {
                            "title": self.fix_encoding(element.text),
                            "link": href
                        }
                        
                        # 检查是否是有效的电影条目
                        if movie["title"] and len(movie["title"]) > 2:
                            # 尝试提取年份
                            year_match = re.search(r'(20\d{2}|19\d{2})', movie["title"])
                            movie["year"] = year_match.group(0) if year_match else "未知年份"
                            
                            all_movies.append(movie)
                            
                            # 如果收集了足够多的电影，可以提前退出
                            if len(all_movies) >= 30:
                                break
                    except Exception as e:
                        print(f"处理电影元素时出错: {e}")
                
                # 尝试点击下一页
                try:
                    next_page = self.driver.find_element(By.XPATH, "//a[contains(text(), '下一页')]")
                    if next_page:
                        safe_click(self.driver, next_page)
                        time.sleep(2)  # 等待新页面加载
                        current_page += 1
                    else:
                        break
                except:
                    # 找不到下一页按钮，退出循环
                    break
            
            # 获取详细信息（仅处理前10部电影以节省时间）
            detailed_movies = []
            for i, movie in enumerate(all_movies[:10]):
                print(f"正在获取电影详情 {i+1}/10: {movie['title']}")
                detailed_info = self.get_movie_details(movie)
                detailed_movies.append(detailed_info)
                # 短暂暂停以减轻服务器负担
                time.sleep(1)
            
            return detailed_movies
        
        except Exception as e:
            print(f"抓取电影列表时出错: {e}")
            return all_movies
    
    def save_to_csv(self, movies, filename=None):
        """将电影信息保存到CSV文件"""
        if not movies:
            print("没有电影数据可保存")
            return False
        
        if not filename:
            # 生成默认文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dytt8_movies_{timestamp}.csv"
        
        try:
            # 确定要保存的字段
            fieldnames = ["title", "year", "link", "download_link", "description", "cover_image"]
            
            # 写入CSV文件
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for movie in movies:
                    # 只保存特定字段
                    row = {field: movie.get(field, "") for field in fieldnames}
                    writer.writerow(row)
            
            print(f"成功保存 {len(movies)} 部电影信息到 {filename}")
            return True
        
        except Exception as e:
            print(f"保存CSV文件时出错: {e}")
            return False


def main():
    """主函数"""
    print("电影天堂网站爬虫启动...")
    
    # 创建爬虫实例
    scraper = Dytt8Scraper(headless=False)  # 设置为False可以查看浏览器操作
    
    try:
        # 电影类别选项
        categories = {
            "1": "最新电影",
            "2": "国内电影",
            "3": "欧美电影",
            "4": "日韩电影",
            "5": "华语电视",
            "6": "欧美电视",
            "7": "日韩电视"
        }
        
        # 显示类别选项
        print("请选择要抓取的电影/电视剧类别:")
        for key, value in categories.items():
            print(f"{key}. {value}")
        
        # 获取用户输入（如果是自动运行，可以设定默认值）
        category_choice = input("请输入类别编号 (默认为最新电影): ").strip() or "1"
        selected_category = categories.get(category_choice, "最新电影")
        
        # 获取页数
        pages = input("要抓取多少页数据? (默认为2): ").strip()
        pages = int(pages) if pages.isdigit() and int(pages) > 0 else 2
        
        print(f"开始抓取 '{selected_category}' 类别的电影，页数: {pages}")
        
        # 开始抓取
        movies = scraper.scrape_latest_movies(max_pages=pages, category=selected_category)
        
        # 显示结果
        if movies:
            print(f"\n成功抓取 {len(movies)} 部电影:")
            for i, movie in enumerate(movies[:5], 1):
                print(f"{i}. {movie['title']} ({movie.get('year', '未知年份')})")
                if movie.get('download_link'):
                    print(f"   下载链接: {movie['download_link']}")
                print("---")
            
            if len(movies) > 5:
                print(f"... 以及 {len(movies) - 5} 部其他电影")
            
            # 保存结果
            should_save = input("是否保存为CSV文件? (y/n, 默认为y): ").strip().lower() or "y"
            if should_save == "y":
                filename = input("请输入文件名 (默认为自动生成): ").strip()
                scraper.save_to_csv(movies, filename)
        else:
            print("未找到任何电影信息")
    
    except Exception as e:
        print(f"程序运行出错: {e}")
    
    finally:
        # 确保浏览器关闭
        del scraper
        print("电影天堂网站爬虫已关闭")


if __name__ == "__main__":
    main() 