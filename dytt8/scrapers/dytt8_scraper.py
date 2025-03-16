#!/usr/bin/env python
"""
电影天堂(dytt8)爬虫实现
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

class Dytt8Scraper(BaseScraper):
    """电影天堂网站爬虫"""
    
    def __init__(self, pages=3, delay=2.0, category="最新电影", headless=True):
        """
        初始化电影天堂爬虫
        
        参数:
            pages (int): 爬取页数
            delay (float): 爬取延迟(秒)
            category (str): 电影类别
            headless (bool): 是否使用无头模式
        """
        super().__init__(pages, delay, category)
        self.base_url = "https://www.dytt8.net"
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
            "最新电影": "/html/gndy/dyzz/index.html",
            "国内电影": "/html/gndy/china/index.html",
            "欧美电影": "/html/gndy/oumei/index.html",
            "日韩电影": "/html/gndy/rihan/index.html",
            "华语电视": "/html/tv/hytv/index.html",
            "日韩电视": "/html/tv/rihantv/index.html",
            "欧美电视": "/html/tv/oumeitv/index.html"
        }
        
        if self.category in category_map:
            return self.base_url + category_map[self.category]
        else:
            print(f"未知类别: {self.category}，使用默认类别: 最新电影")
            return self.base_url + category_map["最新电影"]
    
    def _extract_movie_info(self, url):
        """从电影详情页提取信息"""
        try:
            # 使用requests获取页面，避免频繁启动Selenium
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.encoding = 'gb2312'  # 设置正确的编码
            
            if response.status_code != 200:
                print(f"获取页面失败: {url}, 状态码: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 获取标题
            title_elem = soup.select_one("div.title_all h1")
            title = title_elem.text.strip() if title_elem else "未知标题"
            
            # 获取内容
            content = soup.select_one("div#Zoom")
            if not content:
                print(f"无法找到内容区域: {url}")
                return None
            
            content_text = content.text
            
            # 提取年份
            year_match = re.search(r'年\s*代:\s*(\d{4})', content_text) or \
                        re.search(r'(\d{4})年', title)
            year = year_match.group(1) if year_match else "未知年份"
            
            # 提取类别
            category_elem = soup.select_one("div.title_all a:nth-child(2)")
            category = category_elem.text.strip() if category_elem else "未知类别"
            
            # 提取格式
            format_elem = soup.select_one("div.title_all a:nth-child(3)")
            format = format_elem.text.strip() if format_elem else "未知格式"
            
            # 提取大小
            size_elem = soup.select_one("div.title_all a:nth-child(4)")
            size = size_elem.text.strip() if size_elem else "未知大小"
            
            # 提取下载链接
            download_link_elem = soup.select_one("div.title_all a:nth-child(5)")
            download_link = download_link_elem['href'] if download_link_elem else "无法获取下载链接"
            
            # 提取电影信息
            movie_info = {
                "title": title,
                "year": year,
                "category": category,
                "format": format,
                "size": size,
                "download_link": download_link
            }
            
            return movie_info
        except Exception as e:
            print(f"提取电影信息失败: {e}")
            return None 