"""
电影天堂工具集 - 核心模块
提供电影爬取和搜索的核心功能
"""

# 导入并导出主要类
from dytt8.core.dytt8_scraper import Dytt8Scraper as MovieScraper
from dytt8.core.dytt8_movie_finder import MovieFinder
from dytt8.core.dytt8_scraper_v2 import Dytt8Scraper as MovieScraperV2
from dytt8.core.dytt8_simple import SimpleDyttScraper as SimpleMovieScraper

# 为了向后兼容，提供别名
Scraper = MovieScraper
ScraperV2 = MovieScraperV2
Finder = MovieFinder
SimpleScraper = SimpleMovieScraper
