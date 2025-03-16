#!/usr/bin/env python
"""
基础爬虫类 - 为所有电影来源网站提供通用接口
"""
from abc import ABC, abstractmethod
import pandas as pd
import os
import json
from datetime import datetime

class BaseScraper(ABC):
    """电影爬虫基类"""
    
    def __init__(self, pages=3, delay=2.0, category="最新电影"):
        """
        初始化爬虫
        
        参数:
            pages (int): 爬取页数
            delay (float): 爬取延迟(秒)
            category (str): 电影类别
        """
        self.pages = pages
        self.delay 