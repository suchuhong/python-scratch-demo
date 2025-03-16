#!/usr/bin/env python
"""
电影推荐系统
基于用户喜好和历史记录推荐电影
"""
import os
import json
import pandas as pd
import numpy as np
import re
from collections import Counter
import pickle
from datetime import datetime

class MovieRecommender:
    """电影推荐系统类"""
    
    def __init__(self):
        """初始化推荐系统"""
        self.movies_data = []
        self.user_preferences = {}
        self.watch_history = []
        self.model_file = os.path.join(os.path.dirname(__file__), "data", "recommender_model.pkl")
        
        # 创建数据目录
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
        
        # 加载电影数据
        self._load_movie_data()
        
        # 加载保存的模型
        self._load_model()
    
    def _load_movie_data(self):
        """加载电影数据"""
        print("加载电影数据...")
        
        # 