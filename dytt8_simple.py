"""
电影天堂网站简易爬虫 - 解决ChromeDriver兼容性问题版本
适用于最新版Chrome，不依赖webdriver-manager
"""
import os
import sys
import time
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SimpleDyttScraper:
    """简化版电影天堂爬虫"""
    
    def __init__(self, headless=False):
        """初始化爬虫"""
        self.base_url = "https://www.dytt8.com/"
        
        # 设置Chrome选项
        options = Options()
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
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
        # 使用Selenium 4的新特性，自动管理驱动程序
        print("正在初始化Chrome浏览器...")
        self.driver = webdriver.Chrome(options=options)
        print("Chrome浏览器初始化成功!")
    
    def __del__(self):
        """析构函数 - 确保浏览器关闭"""
        if hasattr(self, 'driver'):
            print("关闭浏览器...")
            self.driver.quit()
    
    def fix_encoding(self, text):
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
    
    def open_website(self):
        """打开电影天堂网站"""
        try:
            print(f"正在访问电影天堂网站: {self.base_url}")
            self.driver.get(self.base_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            print("✓ 成功打开电影天堂网站")
            return True
        except Exception as e:
            print(f"✗ 打开网站失败: {e}")
            return False
    
    def browse_movies_by_category(self, category="最新电影"):
        """按类别浏览电影"""
        if not self.open_website():
            return []
        
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
            movies = []
            
            # 查找电影链接
            try:
                print("正在收集电影信息...")
                movie_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.html')]")
                
                for link in movie_links[:30]:  # 只处理前30个链接
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
                            "link": href
                        })
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"收集电影信息时出错: {e}")
            
            print(f"找到 {len(movies)} 部电影")
            return movies
            
        except Exception as e:
            print(f"浏览电影类别时出错: {e}")
            return []
    
    def search_movie(self, keyword):
        """搜索电影"""
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
                            "link": href
                        })
                    except:
                        continue
            except Exception as e:
                print(f"处理搜索结果时出错: {e}")
            
            print(f"找到 {len(results)} 个搜索结果")
            return results
            
        except Exception as e:
            print(f"搜索电影时出错: {e}")
            return []
    
    def get_movie_details(self, movie_link):
        """获取电影详情"""
        try:
            print(f"正在获取电影详情: {movie_link}")
            
            self.driver.get(movie_link)
            time.sleep(2)  # 等待页面加载
            
            # 获取下载链接
            download_link = ""
            try:
                # 查找下载链接
                link_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'magnet:') or contains(@href, 'ed2k:') or contains(@href, 'thunder:')]")
                if link_elements:
                    download_link = link_elements[0].get_attribute("href")
                else:
                    # 尝试其他可能的下载链接位置
                    td_elements = self.driver.find_elements(By.XPATH, "//td[@bgcolor='#fdfddf']/a")
                    if td_elements:
                        download_link = td_elements[0].get_attribute("href")
            except Exception as e:
                print(f"获取下载链接时出错: {e}")
            
            # 获取电影描述
            description = ""
            try:
                desc_elements = self.driver.find_elements(By.XPATH, "//div[@id='Zoom']")
                if desc_elements:
                    description = self.fix_encoding(desc_elements[0].text)
            except Exception as e:
                print(f"获取电影描述时出错: {e}")
            
            return {
                "download_link": download_link,
                "description": description
            }
            
        except Exception as e:
            print(f"获取电影详情时出错: {e}")
            return {"download_link": "", "description": ""}


def main():
    """主函数"""
    print("=" * 60)
    print("电影天堂简易爬虫 - 兼容性修复版")
    print("=" * 60)
    
    try:
        # 创建爬虫实例
        scraper = SimpleDyttScraper(headless=False)
        
        # 显示菜单
        print("\n请选择操作:")
        print("1. 按类别浏览电影")
        print("2. 搜索电影")
        
        choice = input("\n请输入选项编号 (默认为1): ").strip() or "1"
        
        if choice == "1":
            # 显示类别选项
            categories = [
                "最新电影", "国内电影", "欧美电影", "日韩电影", 
                "华语电视", "欧美电视", "日韩电视"
            ]
            
            print("\n请选择电影类别:")
            for i, category in enumerate(categories, 1):
                print(f"{i}. {category}")
            
            cat_choice = input("\n请输入类别编号 (默认为1): ").strip() or "1"
            try:
                selected_category = categories[int(cat_choice) - 1]
            except:
                selected_category = categories[0]
            
            # 浏览电影
            movies = scraper.browse_movies_by_category(selected_category)
            
            if not movies:
                print("未找到任何电影")
                return
            
            # 显示电影列表
            print("\n电影列表:")
            for i, movie in enumerate(movies[:20], 1):  # 只显示前20部
                print(f"{i}. {movie['title']} ({movie['year']})")
            
            # 选择电影查看详情
            movie_choice = input("\n请输入电影编号查看详情 (输入q退出): ").strip()
            if movie_choice.lower() == 'q':
                return
            
            try:
                idx = int(movie_choice) - 1
                if 0 <= idx < len(movies):
                    selected_movie = movies[idx]
                    
                    # 获取电影详情
                    details = scraper.get_movie_details(selected_movie['link'])
                    
                    # 显示电影详情
                    print("\n" + "=" * 60)
                    print(f"片名: {selected_movie['title']} ({selected_movie['year']})")
                    
                    if details['download_link']:
                        print("\n下载链接:")
                        print(details['download_link'])
                    else:
                        print("\n未找到下载链接")
                    
                    if details['description']:
                        print("\n简介:")
                        desc = details['description']
                        print(desc[:500] + "..." if len(desc) > 500 else desc)
                else:
                    print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
        
        elif choice == "2":
            # 搜索电影
            keyword = input("\n请输入要搜索的电影名称: ").strip()
            if not keyword:
                print("搜索关键词不能为空")
                return
            
            # 执行搜索
            results = scraper.search_movie(keyword)
            
            if not results:
                print("未找到匹配的电影")
                return
            
            # 显示搜索结果
            print("\n搜索结果:")
            for i, movie in enumerate(results[:20], 1):  # 只显示前20个结果
                print(f"{i}. {movie['title']} ({movie['year']})")
            
            # 选择电影查看详情
            movie_choice = input("\n请输入电影编号查看详情 (输入q退出): ").strip()
            if movie_choice.lower() == 'q':
                return
            
            try:
                idx = int(movie_choice) - 1
                if 0 <= idx < len(results):
                    selected_movie = results[idx]
                    
                    # 获取电影详情
                    details = scraper.get_movie_details(selected_movie['link'])
                    
                    # 显示电影详情
                    print("\n" + "=" * 60)
                    print(f"片名: {selected_movie['title']} ({selected_movie['year']})")
                    
                    if details['download_link']:
                        print("\n下载链接:")
                        print(details['download_link'])
                    else:
                        print("\n未找到下载链接")
                    
                    if details['description']:
                        print("\n简介:")
                        desc = details['description']
                        print(desc[:500] + "..." if len(desc) > 500 else desc)
                else:
                    print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
        
        else:
            print("无效的选项")
    
    except Exception as e:
        print(f"程序运行出错: {e}")
    
    finally:
        print("\n程序已完成，谢谢使用!")


if __name__ == "__main__":
    main() 