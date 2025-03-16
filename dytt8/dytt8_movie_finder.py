"""
电影天堂资源搜索器 - 基于 Selenium 的电影搜索工具
用于在电影天堂网站(https://www.dytt8.com/)上搜索特定电影并获取下载链接
支持按电影名称搜索和获取最新热门电影资源
"""
import os
import sys
import time
import re
from urllib.parse import quote

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


class MovieFinder:
    """电影查找器类"""
    
    def __init__(self, headless=True):
        """初始化电影查找器"""
        self.base_url = "https://www.dytt8.com/"
        self.driver = setup_chrome_driver(headless=headless, disable_images=True)
        
        # 解决中文乱码问题的配置
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "languages", {get: function() {return ["zh-CN", "zh", "en"]}})'
        })
    
    def __del__(self):
        """析构函数 - 确保浏览器关闭"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def fix_encoding(self, text):
        """修复中文乱码问题"""
        if not text:
            return ""
        
        # 尝试不同的编码方式
        try:
            return text.encode('latin1').decode('utf-8')
        except:
            try:
                return text.encode('latin1').decode('gbk')
            except:
                return text
    
    def open_website(self):
        """打开电影天堂网站"""
        try:
            self.driver.get(self.base_url)
            # 等待页面加载完成
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("✓ 成功打开电影天堂网站")
            return True
        except Exception as e:
            print(f"✗ 打开网站失败: {e}")
            return False
    
    def search_movie(self, movie_name):
        """搜索特定电影"""
        if not self.open_website():
            return []
        
        try:
            print(f"正在搜索电影: {movie_name}")
            
            # 尝试使用搜索框
            try:
                # 寻找搜索框
                search_input = None
                search_selectors = [
                    "//input[@name='q']",
                    "//input[@name='keyword']",
                    "//input[@type='text']"
                ]
                
                for selector in search_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        if elements:
                            search_input = elements[0]
                            break
                    except:
                        continue
                
                if search_input:
                    search_input.clear()
                    search_input.send_keys(movie_name)
                    
                    # 查找搜索按钮
                    search_button = None
                    button_selectors = [
                        "//input[@type='submit']",
                        "//button[contains(text(), '搜')]",
                        "//button[contains(text(), '查')]",
                        "//button[contains(@class, 'search')]"
                    ]
                    
                    for selector in button_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            if elements:
                                search_button = elements[0]
                                break
                        except:
                            continue
                    
                    if search_button:
                        safe_click(self.driver, search_button)
                        time.sleep(2)  # 等待搜索结果加载
                    else:
                        # 尝试按回车键提交搜索
                        search_input.submit()
                        time.sleep(2)
                
                # 如果没有找到搜索框或无法提交搜索，使用备用方法
                else:
                    # 备用搜索方法：某些网站使用GET方式搜索，使用URL直接搜索
                    search_url = f"{self.base_url}/plusSearch.php?q={quote(movie_name)}"
                    self.driver.get(search_url)
                    time.sleep(2)
            
            except Exception as e:
                print(f"使用搜索框搜索失败: {e}")
                # 备用搜索方法：某些网站使用GET方式搜索，使用URL直接搜索
                search_url = f"{self.base_url}/plus/search.php?kwtype=0&searchtype=title&keyword={quote(movie_name)}"
                self.driver.get(search_url)
                time.sleep(2)
            
            # 收集搜索结果
            search_results = []
            result_elements = []
            
            # 尝试不同的选择器找到搜索结果
            result_selectors = [
                "//div[@class='co_content8']//a[contains(@href, '.html')]",
                "//a[contains(@href, '.html')]",
                "//td//a[contains(@href, '.html')]"
            ]
            
            for selector in result_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        result_elements = elements
                        break
                except:
                    continue
            
            # 处理搜索结果
            for element in result_elements:
                try:
                    title = self.fix_encoding(element.text)
                    link = element.get_attribute("href")
                    
                    # 排除导航链接和空标题
                    if (not title or len(title) < 2 or 
                        "index" in link or "list" in link or 
                        "search" in link):
                        continue
                    
                    # 检查标题中是否包含搜索关键词（简单匹配）
                    if movie_name.lower() in title.lower() or movie_name in title:
                        # 提取年份
                        year_match = re.search(r'(20\d{2}|19\d{2})', title)
                        year = year_match.group(0) if year_match else "未知年份"
                        
                        result = {
                            "title": title,
                            "link": link,
                            "year": year
                        }
                        search_results.append(result)
                except Exception as e:
                    print(f"处理搜索结果时出错: {e}")
            
            print(f"找到 {len(search_results)} 个可能的结果")
            return search_results
        
        except Exception as e:
            print(f"搜索电影时出错: {e}")
            return []
    
    def get_download_links(self, movie_info):
        """获取电影下载链接"""
        try:
            print(f"正在获取《{movie_info['title']}》的下载链接...")
            
            # 访问电影详情页
            self.driver.get(movie_info["link"])
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 提取所有可能的下载链接
            download_links = []
            
            # 查找所有可能的下载链接
            link_selectors = [
                "//a[contains(@href, 'magnet:')]",
                "//a[contains(@href, 'thunder:')]",
                "//a[contains(@href, 'ed2k:')]",
                "//a[contains(@href, '.torrent')]",
                "//a[contains(text(), '下载')]",
                "//a[contains(text(), '磁力')]",
                "//a[contains(text(), '迅雷')]",
                "//td[@bgcolor='#fdfddf']/a"
            ]
            
            for selector in link_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and href not in download_links:
                            link_text = element.text
                            download_links.append({
                                "url": href,
                                "text": self.fix_encoding(link_text) if link_text else "下载链接"
                            })
                except:
                    continue
            
            # 获取电影描述
            description = ""
            try:
                desc_element = self.driver.find_element(By.XPATH, "//div[@id='Zoom']")
                if desc_element:
                    description = self.fix_encoding(desc_element.text)
            except:
                pass
            
            # 更新电影信息
            movie_info.update({
                "download_links": download_links,
                "description": description
            })
            
            return movie_info
        
        except Exception as e:
            print(f"获取下载链接时出错: {e}")
            movie_info["download_links"] = []
            return movie_info
    
    def get_hot_movies(self, limit=10):
        """获取热门电影"""
        if not self.open_website():
            return []
        
        try:
            print("正在获取最新热门电影...")
            
            # 找到首页热门电影区域
            hot_movies = []
            movie_elements = []
            
            # 尝试不同的选择器找到电影列表
            selectors = [
                "//div[@class='co_content8']//a[contains(@href, '.html')]",
                "//div[@class='co_content2']//a[contains(@href, '.html')]",
                "//a[contains(@href, '.html') and string-length(text()) > 10]"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        movie_elements = elements
                        break
                except:
                    continue
            
            # 处理找到的电影元素
            for element in movie_elements[:limit*2]:  # 获取更多，以防有些不是电影
                try:
                    title = self.fix_encoding(element.text)
                    link = element.get_attribute("href")
                    
                    # 排除导航链接和空标题
                    if (not title or len(title) < 5 or 
                        "index" in link or "list" in link):
                        continue
                    
                    # 提取年份
                    year_match = re.search(r'(20\d{2}|19\d{2})', title)
                    year = year_match.group(0) if year_match else "未知年份"
                    
                    movie = {
                        "title": title,
                        "link": link,
                        "year": year
                    }
                    
                    hot_movies.append(movie)
                    
                    # 如果已经收集了足够的电影，就停止
                    if len(hot_movies) >= limit:
                        break
                        
                except Exception as e:
                    print(f"处理热门电影时出错: {e}")
            
            print(f"找到 {len(hot_movies)} 部热门电影")
            return hot_movies
            
        except Exception as e:
            print(f"获取热门电影时出错: {e}")
            return []


def main():
    """主函数"""
    print("=" * 50)
    print("电影天堂资源搜索器 v1.0")
    print("=" * 50)
    
    # 创建电影查找器实例
    finder = MovieFinder(headless=False)  # 设置为False可以看到浏览器操作
    
    try:
        # 显示功能选项菜单
        print("\n请选择功能:")
        print("1. 搜索特定电影")
        print("2. 获取最新热门电影")
        
        choice = input("请输入选项编号 (默认为1): ").strip() or "1"
        
        if choice == "1":
            # 搜索特定电影
            movie_name = input("请输入要搜索的电影名称: ").strip()
            if not movie_name:
                print("电影名称不能为空!")
                return
            
            results = finder.search_movie(movie_name)
            
            if not results:
                print("没有找到匹配的电影，请尝试其他关键词。")
                return
            
            # 显示搜索结果
            print("\n搜索结果:")
            for i, movie in enumerate(results, 1):
                print(f"{i}. {movie['title']} ({movie['year']})")
            
            # 用户选择感兴趣的电影
            select_num = input("\n请输入要查看详情的电影编号 (输入q退出): ").strip()
            if select_num.lower() == 'q':
                return
            
            try:
                select_num = int(select_num)
                if 1 <= select_num <= len(results):
                    selected_movie = results[select_num - 1]
                    
                    # 获取下载链接
                    movie_detail = finder.get_download_links(selected_movie)
                    
                    if movie_detail.get("download_links"):
                        print("\n电影详情:")
                        print(f"片名: {movie_detail['title']} ({movie_detail['year']})")
                        print("\n下载链接:")
                        
                        for i, link in enumerate(movie_detail["download_links"], 1):
                            print(f"{i}. {link['text']}")
                            print(f"   {link['url']}")
                        
                        # 显示简要描述
                        if movie_detail.get("description"):
                            desc = movie_detail["description"]
                            # 限制描述长度，避免过长
                            if len(desc) > 300:
                                desc = desc[:300] + "..."
                            print("\n电影简介:")
                            print(desc)
                    else:
                        print("未找到此电影的下载链接。")
                else:
                    print("无效的选择。")
            except ValueError:
                print("请输入有效的数字。")
        
        elif choice == "2":
            # 获取热门电影
            limit = input("要获取多少部热门电影? (默认为10): ").strip()
            limit = int(limit) if limit.isdigit() and int(limit) > 0 else 10
            
            hot_movies = finder.get_hot_movies(limit)
            
            if not hot_movies:
                print("获取热门电影失败。")
                return
            
            # 显示热门电影列表
            print("\n热门电影:")
            for i, movie in enumerate(hot_movies, 1):
                print(f"{i}. {movie['title']} ({movie['year']})")
            
            # 用户选择感兴趣的电影
            select_num = input("\n请输入要查看详情的电影编号 (输入q退出): ").strip()
            if select_num.lower() == 'q':
                return
            
            try:
                select_num = int(select_num)
                if 1 <= select_num <= len(hot_movies):
                    selected_movie = hot_movies[select_num - 1]
                    
                    # 获取下载链接
                    movie_detail = finder.get_download_links(selected_movie)
                    
                    if movie_detail.get("download_links"):
                        print("\n电影详情:")
                        print(f"片名: {movie_detail['title']} ({movie_detail['year']})")
                        print("\n下载链接:")
                        
                        for i, link in enumerate(movie_detail["download_links"], 1):
                            print(f"{i}. {link['text']}")
                            print(f"   {link['url']}")
                        
                        # 显示简要描述
                        if movie_detail.get("description"):
                            desc = movie_detail["description"]
                            # 限制描述长度，避免过长
                            if len(desc) > 300:
                                desc = desc[:300] + "..."
                            print("\n电影简介:")
                            print(desc)
                    else:
                        print("未找到此电影的下载链接。")
                else:
                    print("无效的选择。")
            except ValueError:
                print("请输入有效的数字。")
        
        else:
            print("无效的选项。")
    
    except Exception as e:
        print(f"程序运行出错: {e}")
    
    finally:
        # 确保浏览器关闭
        print("\n正在关闭浏览器...")
        del finder
        print("程序已退出。")


if __name__ == "__main__":
    main() 