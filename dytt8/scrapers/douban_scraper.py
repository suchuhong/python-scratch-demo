#!/usr/bin/env python
"""
豆瓣电影爬虫实现
"""
import os
import time
import re
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class DoubanScraper(BaseScraper):
    """豆瓣电影网站爬虫"""
    
    def __init__(self, pages=3, delay=2.0, category="热门", headless=True):
        """
        初始化豆瓣电影爬虫
        
        参数:
            pages (int): 爬取页数
            delay (float): 爬取延迟(秒)
            category (str): 电影类别 (热门, 最新, 经典, 华语, 欧美, 韩国)
            headless (bool): 是否使用无头模式
        """
        super().__init__(pages, delay, category)
        self.base_url = "https://movie.douban.com"
        self.headless = headless
        self.driver = None
    
    def _setup_driver(self):
        """设置WebDriver"""
        print("初始化Chrome浏览器...")
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 设置UA
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            print(f"WebDriver初始化失败: {e}")
            print("请尝试使用 fix_webdriver.py 修复")
            return None
    
    def _get_category_url(self):
        """获取分类URL"""
        category_map = {
            "热门": "/explore",
            "最新": "/explore?sort=time",
            "经典": "/explore?sort=rank",
            "华语": "/tag/华语",
            "欧美": "/tag/欧美",
            "韩国": "/tag/韩国",
            "日本": "/tag/日本",
            "动作": "/tag/动作",
            "喜剧": "/tag/喜剧",
            "爱情": "/tag/爱情",
            "科幻": "/tag/科幻",
            "悬疑": "/tag/悬疑",
            "恐怖": "/tag/恐怖",
            "动画": "/tag/动画"
        }
        
        if self.category in category_map:
            return self.base_url + category_map[self.category]
        else:
            print(f"未知类别: {self.category}，使用默认类别: 热门")
            return self.base_url + category_map["热门"]
    
    def _extract_movie_info(self, url):
        """从电影详情页提取信息"""
        try:
            # 使用requests获取页面
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # 豆瓣反爬较为严格，使用Selenium访问
            self.driver.get(url)
            
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "content"))
                )
            except Exception as e:
                print(f"页面加载等待超时: {e}")
            
            # 获取页面内容
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # 检查是否被反爬
            if "检测到有异常请求" in page_source:
                print("被豆瓣反爬系统拦截，请稍后再试或减慢爬取速度")
                return None
            
            # 获取标题
            title_elem = soup.select_one("h1 span[property='v:itemreviewed']")
            title = title_elem.text.strip() if title_elem else "未知标题"
            
            # 获取年份
            year_elem = soup.select_one("h1 .year")
            year = year_elem.text.strip("()") if year_elem else ""
            
            # 获取导演
            directors = []
            director_elems = soup.select("a[rel='v:directedBy']")
            for elem in director_elems:
                directors.append(elem.text.strip())
            director = ", ".join(directors) if directors else "未知"
            
            # 获取主演
            actors = []
            actor_elems = soup.select("#info .actor .attrs a")
            for elem in actor_elems:
                actors.append(elem.text.strip())
            actors = ", ".join(actors[:3]) if actors else "未知"  # 只取前3位主演
            
            # 获取类别
            genres = []
            genre_elems = soup.select("span[property='v:genre']")
            for elem in genre_elems:
                genres.append(elem.text.strip())
            category = ", ".join(genres) if genres else ""
            
            # 获取国家/地区
            info_text = soup.select_one("#info").text if soup.select_one("#info") else ""
            country_match = re.search(r'制片国家/地区:\s*([^\n]+)', info_text)
            country = country_match.group(1).strip() if country_match else ""
            
            # 获取语言
            language_match = re.search(r'语言:\s*([^\n]+)', info_text)
            language = language_match.group(1).strip() if language_match else ""
            
            # 获取上映日期
            release_dates = []
            release_date_elems = soup.select("span[property='v:initialReleaseDate']")
            for elem in release_date_elems:
                release_dates.append(elem.text.strip())
            release_date = ", ".join(release_dates) if release_dates else ""
            
            # 获取评分
            rating_elem = soup.select_one("strong[property='v:average']")
            rating = rating_elem.text.strip() if rating_elem else ""
            score = f"{rating}/10" if rating else ""
            
            # 获取片长
            duration_elem = soup.select_one("span[property='v:runtime']")
            duration = duration_elem.text.strip() if duration_elem else ""
            
            # 获取简介
            summary_elem = soup.select_one("span[property='v:summary']")
            summary = summary_elem.text.strip() if summary_elem else ""
            
            # 下载链接通常豆瓣不提供，置为空
            download_link = ""
            
            return {
                "title": title,
                "year": year,
                "director": director,
                "actors": actors,
                "category": category,
                "country": country,
                "language": language,
                "release_date": release_date,
                "score": score,
                "duration": duration,
                "summary": summary,
                "download_link": download_link,
                "size": "",  # 豆瓣不提供大小信息
                "format": "",  # 豆瓣不提供格式信息
                "source_url": url,
                "source": "豆瓣电影"
            }
            
        except Exception as e:
            print(f"处理页面出错: {url}, 错误: {e}")
            return None
    
    def scrape(self):
        """执行爬取操作"""
        print(f"开始爬取豆瓣电影 - {self.category}...")
        self.results = []
        
        # 初始化WebDriver
        self.driver = self._setup_driver()
        if not self.driver:
            print("WebDriver初始化失败，无法继续爬取")
            return self.results
        
        try:
            # 获取分类URL
            category_url = self._get_category_url()
            print(f"分类URL: {category_url}")
            
            # 爬取指定页数
            current_page_url = category_url
            
            # 注意：豆瓣电影的分页机制不同，通常需要点击"加载更多"按钮
            # 这里简化处理，只获取第一页内容
            
            self.driver.get(current_page_url)
            
            # 等待页面加载
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "article"))
                )
            except Exception as e:
                print(f"页面加载等待超时: {e}")
            
            # 点击"加载更多"按钮模拟翻页，爬取多页内容
            for page in range(1, self.pages + 1):
                print(f"正在爬取第 {page}/{self.pages} 页...")
                
                # 获取电影链接
                movie_links = []
                try:
                    # 找到所有电影卡片
                    link_elements = self.driver.find_elements(By.XPATH, '//div[contains(@class, "cover-wp")]//a')
                    for link in link_elements:
                        href = link.get_attribute("href")
                        if href and "/subject/" in href:
                            movie_links.append(href)
                except Exception as e:
                    print(f"获取电影链接失败: {e}")
                
                print(f"找到 {len(movie_links)} 个电影链接")
                
                # 访问每个电影详情页
                for i, link in enumerate(movie_links):
                    print(f"正在处理第 {i+1}/{len(movie_links)} 个电影: {link}")
                    
                    # 提取电影信息
                    movie_info = self._extract_movie_info(link)
                    
                    if movie_info:
                        self.results.append(movie_info)
                        print(f"已爬取: {movie_info['title']}")
                    
                    # 添加随机延迟
                    delay_time = self.delay * (1 + random.random())  # 豆瓣反爬严格，增加延迟
                    print(f"等待 {delay_time:.2f} 秒...")
                    time.sleep(delay_time)
                
                # 如果有下一页，点击"加载更多"按钮
                if page < self.pages:
                    try:
                        # 滚动到页面底部
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(1)  # 等待页面响应
                        
                        # 查找并点击"加载更多"按钮
                        more_btn = self.driver.find_element(By.CLASS_NAME, "more")
                        if more_btn.is_displayed():
                            more_btn.click()
                            print("点击加载更多...")
                            time.sleep(2)  # 等待内容加载
                        else:
                            print("没有更多内容可加载")
                            break
                    except Exception as e:
                        print(f"加载更多内容失败: {e}")
                        break
            
            print(f"爬取完成，共获取 {len(self.results)} 部电影信息")
            return self.results
            
        except Exception as e:
            print(f"爬取过程中发生错误: {e}")
            return self.results
            
        finally:
            # 关闭WebDriver
            if self.driver:
                self.driver.quit()
                print("已关闭WebDriver") 