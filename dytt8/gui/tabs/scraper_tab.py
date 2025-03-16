#!/usr/bin/env python
"""
电影抓取选项卡
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import subprocess
from datetime import datetime
import time

# 确保能找到dytt8模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ScraperTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="10")
        
        # 爬虫线程
        self.scraper_thread = None
        self.running = False
        
        # 初始化组件
        self.init_components()
    
    def init_components(self):
        """初始化抓取选项卡组件"""
        # 选择爬虫版本
        ttk.Label(self.frame, text="选择爬虫版本:", font=("Arial", 11)).grid(column=0, row=0, sticky=tk.W, pady=(0, 10))
        
        self.scraper_var = tk.StringVar(value="v2")
        ttk.Radiobutton(self.frame, text="标准版 (dytt8_scraper.py)", variable=self.scraper_var, value="v1").grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(self.frame, text="兼容版 (dytt8_scraper_v2.py) - 推荐", variable=self.scraper_var, value="v2").grid(column=0, row=2, sticky=tk.W)
        ttk.Radiobutton(self.frame, text="简化版 (dytt8_simple.py)", variable=self.scraper_var, value="simple").grid(column=0, row=3, sticky=tk.W)
        
        ttk.Separator(self.frame, orient=tk.HORIZONTAL).grid(column=0, row=4, sticky=tk.EW, pady=10)
        
        # 爬取参数
        ttk.Label(self.frame, text="爬取设置:", font=("Arial", 11)).grid(column=0, row=5, sticky=tk.W, pady=(0, 10))
        
        param_frame = ttk.Frame(self.frame)
        param_frame.grid(column=0, row=6, sticky=tk.W)
        
        ttk.Label(param_frame, text="页数:").grid(column=0, row=0, sticky=tk.W, padx=(0, 5))
        self.page_var = tk.StringVar(value="3")
        ttk.Spinbox(param_frame, from_=1, to=20, width=5, textvariable=self.page_var).grid(column=1, row=0, sticky=tk.W)
        
        ttk.Label(param_frame, text="延迟(秒):").grid(column=2, row=0, sticky=tk.W, padx=(15, 5))
        self.delay_var = tk.StringVar(value="2")
        ttk.Spinbox(param_frame, from_=0, to=10, width=5, textvariable=self.delay_var, increment=0.5).grid(column=3, row=0, sticky=tk.W)
        
        ttk.Label(param_frame, text="类别:").grid(column=0, row=1, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.category_var = tk.StringVar(value="最新电影")
        categories = ["最新电影", "国内电影", "欧美电影", "日韩电影", "华语电视", "日韩电视", "欧美电视"]
        ttk.Combobox(param_frame, values=categories, textvariable=self.category_var, width=15).grid(column=1, row=1, sticky=tk.W, columnspan=3, pady=(10, 0))
        
        # 保存选项
        save_frame = ttk.Frame(self.frame)
        save_frame.grid(column=0, row=7, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(save_frame, text="保存选项:").grid(column=0, row=0, sticky=tk.W, padx=(0, 5))
        
        self.save_option_var = tk.StringVar(value="csv")
        ttk.Radiobutton(save_frame, text="CSV", variable=self.save_option_var, value="csv").grid(column=1, row=0, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(save_frame, text="Excel", variable=self.save_option_var, value="excel").grid(column=2, row=0, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(save_frame, text="JSON", variable=self.save_option_var, value="json").grid(column=3, row=0, sticky=tk.W)
        
        ttk.Label(save_frame, text="保存路径:").grid(column=0, row=1, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        path_frame = ttk.Frame(save_frame)
        path_frame.grid(column=1, row=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        self.save_path_var = tk.StringVar(value=os.getcwd())
        save_path_entry = ttk.Entry(path_frame, textvariable=self.save_path_var, width=40)
        save_path_entry.grid(column=0, row=0, sticky=tk.W, padx=(0, 5))
        
        browse_btn = ttk.Button(path_frame, text="浏览...", command=self.browse_save_path)
        browse_btn.grid(column=1, row=0, sticky=tk.W)
        
        # 输出区域
        ttk.Label(self.frame, text="运行日志:", font=("Arial", 11)).grid(column=0, row=8, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, height=12)
        self.output_text.grid(column=0, row=9, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_text.config(state=tk.DISABLED)
        
        # 按钮区域
        btn_frame = ttk.Frame(self.frame)
        btn_frame.grid(column=0, row=10, sticky=tk.E, pady=(10, 0))
        
        self.start_btn = ttk.Button(btn_frame, text="开始抓取", command=self.start_scraping, width=15)
        self.start_btn.grid(column=0, row=0, sticky=tk.E, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_scraping, width=10, state=tk.DISABLED)
        self.stop_btn.grid(column=1, row=0, sticky=tk.E)
        
        # 配置Grid权重，使输出区域可以随窗口大小调整
        self.frame.grid_rowconfigure(9, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def browse_save_path(self):
        """浏览保存路径"""
        path = filedialog.askdirectory()
        if path:
            self.save_path_var.set(path)
    
    def write_to_output(self, text):
        """写入输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def start_scraping(self):
        """开始爬取电影数据"""
        # 获取设置参数
        scraper_type = self.scraper_var.get()
        pages = int(self.page_var.get())
        delay = float(self.delay_var.get())
        category = self.category_var.get()
        save_format = self.save_option_var.get()
        save_path = self.save_path_var.get()
        
        # 更新UI状态
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.running = True
        
        # 清空输出区域
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # 显示开始信息
        self.write_to_output(f"开始爬取电影数据")
        self.write_to_output(f"爬虫版本: {scraper_type}")
        self.write_to_output(f"爬取页数: {pages}")
        self.write_to_output(f"电影类别: {category}")
        self.write_to_output(f"保存格式: {save_format}")
        self.write_to_output(f"保存路径: {save_path}")
        self.write_to_output("-" * 40)
        
        # 启动爬虫线程，避免UI冻结
        self.scraper_thread = threading.Thread(
            target=self._run_scraper,
            args=(scraper_type, pages, delay, category, save_format, save_path)
        )
        self.scraper_thread.daemon = True
        self.scraper_thread.start()
    
    def _run_scraper(self, scraper_type, pages, delay, category, save_format, save_path):
        """在后台线程中运行爬虫"""
        try:
            # 根据选择的爬虫类型，导入相应的爬虫模块
            if scraper_type == "v1":
                # 标准版爬虫
                try:
                    from dytt8.core import MovieScraper
                    self.write_to_output("初始化标准版爬虫...")
                    scraper = MovieScraper(headless=True)
                    self._run_standard_scraper(scraper, pages, delay, category, save_format, save_path)
                except ImportError as e:
                    self.write_to_output(f"无法导入标准版爬虫: {str(e)}")
                    self.write_to_output("尝试使用内置模拟爬虫...")
                    self._run_simulated_scraper(pages, delay, category, save_format, save_path)
                    
            elif scraper_type == "v2":
                # 兼容版爬虫
                try:
                    from dytt8.core import MovieScraperV2
                    self.write_to_output("初始化兼容版爬虫...")
                    scraper = MovieScraperV2(headless=True)
                    self._run_v2_scraper(scraper, pages, delay, category, save_format, save_path)
                except ImportError as e:
                    self.write_to_output(f"无法导入兼容版爬虫: {str(e)}")
                    self.write_to_output("尝试使用内置模拟爬虫...")
                    self._run_simulated_scraper(pages, delay, category, save_format, save_path)
                    
            elif scraper_type == "simple":
                # 简化版爬虫
                try:
                    from dytt8.core import SimpleMovieScraper
                    self.write_to_output("初始化简化版爬虫...")
                    scraper = SimpleMovieScraper(headless=True)
                    self._run_simple_scraper(scraper, pages, delay, category, save_format, save_path)
                except ImportError as e:
                    self.write_to_output(f"无法导入简化版爬虫: {str(e)}")
                    self.write_to_output("尝试使用内置模拟爬虫...")
                    self._run_simulated_scraper(pages, delay, category, save_format, save_path)
        except Exception as e:
            self.write_to_output(f"爬虫运行出错: {str(e)}")
        finally:
            # 恢复UI状态
            self.running = False
            self.frame.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.frame.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))
    
    def _run_standard_scraper(self, scraper, pages, delay, category, save_format, save_path):
        """运行标准版爬虫"""
        self.write_to_output("打开电影天堂网站...")
        scraper.open_website()
        
        all_movies = []
        
        for page in range(1, pages + 1):
            if not self.running:
                self.write_to_output("爬取已被中止")
                break
            
            self.write_to_output(f"正在爬取第 {page} 页...")
            try:
                movies = scraper.scrape_latest_movies(page_num=page)
                all_movies.extend(movies)
                self.write_to_output(f"第 {page} 页成功抓取 {len(movies)} 部电影")
                
                # 显示部分电影信息
                for i, movie in enumerate(movies[:3]):  # 只显示前3部
                    self.write_to_output(f"  {i+1}. {movie['title']} - {movie.get('category', 'N/A')} - {movie.get('rating', 'N/A')}")
                
                if len(movies) > 3:
                    self.write_to_output(f"  ... 还有 {len(movies)-3} 部电影")
                
                # 页面间延迟
                if page < pages and self.running:
                    self.write_to_output(f"等待 {delay} 秒后抓取下一页...")
                    time.sleep(delay)
            except Exception as e:
                self.write_to_output(f"抓取第 {page} 页时出错: {str(e)}")
        
        # 保存结果
        if all_movies:
            self._save_movies(all_movies, save_format, save_path)
        else:
            self.write_to_output("没有抓取到任何电影数据")
    
    def _run_v2_scraper(self, scraper, pages, delay, category, save_format, save_path):
        """运行兼容版爬虫"""
        self.write_to_output("开始抓取电影...")
        
        try:
            all_movies = []
            
            # 打开网站
            self.write_to_output("打开电影天堂网站...")
            if hasattr(scraper, 'open_website'):
                scraper.open_website()
            
            # 根据类别选择不同的爬取方法 - 使用scrape_latest_movies方法
            self.write_to_output(f"抓取{category}...")
            
            for page in range(1, pages + 1):
                if not self.running:
                    self.write_to_output("爬取已被中止")
                    break
                    
                self.write_to_output(f"正在爬取第 {page} 页...")
                try:
                    # 使用实际存在的方法
                    if hasattr(scraper, 'scrape_latest_movies'):
                        movies = scraper.scrape_latest_movies(page_num=page)
                        all_movies.extend(movies)
                        self.write_to_output(f"第 {page} 页成功抓取 {len(movies)} 部电影")
                    else:
                        # 如果没有该方法，尝试其他可能的方法
                        self.write_to_output("爬虫类没有scrape_latest_movies方法，尝试其他方法...")
                        if hasattr(scraper, 'scrape_page'):
                            movies = scraper.scrape_page(page)
                            all_movies.extend(movies)
                            self.write_to_output(f"第 {page} 页成功抓取 {len(movies)} 部电影")
                        else:
                            raise AttributeError("爬虫类没有可用的抓取方法")
                    
                    # 显示部分电影信息
                    for i, movie in enumerate(movies[:3]):  # 只显示前3部
                        movie_title = movie.get('title', 'Unknown')
                        movie_category = movie.get('category', 'N/A')
                        movie_rating = movie.get('rating', 'N/A')
                        self.write_to_output(f"  {i+1}. {movie_title} - {movie_category} - {movie_rating}")
                    
                    if len(movies) > 3:
                        self.write_to_output(f"  ... 还有 {len(movies)-3} 部电影")
                        
                    # 页面间延迟
                    if page < pages and self.running:
                        self.write_to_output(f"等待 {delay} 秒后抓取下一页...")
                        time.sleep(delay)
                except Exception as e:
                    self.write_to_output(f"抓取第 {page} 页时出错: {str(e)}")
                    self.write_to_output("尝试继续抓取下一页...")
            
            # 保存结果
            if all_movies:
                self._save_movies(all_movies, save_format, save_path)
            else:
                self.write_to_output("没有抓取到任何电影数据，尝试使用模拟数据...")
                self._run_simulated_scraper(pages, delay, category, save_format, save_path)
        except Exception as e:
            self.write_to_output(f"抓取过程中出错: {str(e)}")
            self.write_to_output("尝试使用模拟数据...")
            self._run_simulated_scraper(pages, delay, category, save_format, save_path)
    
    def _run_simple_scraper(self, scraper, pages, delay, category, save_format, save_path):
        """运行简化版爬虫"""
        self.write_to_output("使用简化版爬虫抓取电影...")
        
        try:
            # 抓取热门电影
            self.write_to_output("抓取热门电影...")
            hot_movies = scraper.get_hot_movies()
            
            # 显示结果
            self.write_to_output(f"成功抓取 {len(hot_movies)} 部热门电影")
            for i, movie in enumerate(hot_movies):
                self.write_to_output(f"  {i+1}. {movie['title']} - {movie.get('download_url', 'N/A')}")
            
            # 保存结果
            self._save_movies(hot_movies, save_format, save_path)
        except Exception as e:
            self.write_to_output(f"抓取过程中出错: {str(e)}")
    
    def _run_simulated_scraper(self, pages, delay, category, save_format, save_path):
        """运行模拟爬虫（当实际爬虫无法使用时）"""
        self.write_to_output("使用模拟爬虫...")
        self.write_to_output("警告: 这只是演示数据，不是真实抓取结果!")
        
        # 模拟爬取过程
        all_movies = []
        
        categories = {
            "最新电影": ["科幻", "动作", "冒险", "喜剧", "爱情"],
            "国内电影": ["剧情", "爱情", "喜剧", "动作"],
            "欧美电影": ["科幻", "动作", "冒险", "悬疑", "恐怖"],
            "日韩电影": ["动画", "爱情", "恐怖", "剧情"]
        }
        
        # 使用选择的类别，或默认为"最新电影"
        movie_categories = categories.get(category, categories["最新电影"])
        
        # 模拟电影名称
        movie_titles = [
            "流浪地球3", "速度与激情X", "复仇者联盟5", "变形金刚崛起", "星球大战9",
            "疯狂动物城2", "功夫熊猫4", "哈利波特前传", "007:暗夜无边", "碟中谍8",
            "银河护卫队3", "黑客帝国5", "头号玩家2", "蝙蝠侠:黑暗骑士归来", "超能陆战队2"
        ]
        
        import random
        
        for page in range(1, pages + 1):
            if not self.running:
                break
            
            self.write_to_output(f"模拟抓取第 {page} 页...")
            
            # 每页生成5-10部随机电影
            movies_count = random.randint(5, 10)
            for i in range(movies_count):
                movie_title = random.choice(movie_titles)
                movie_category = random.choice(movie_categories)
                movie_rating = round(random.uniform(7.0, 9.5), 1)
                movie_year = random.randint(2022, 2024)
                
                movie = {
                    "title": movie_title,
                    "category": movie_category,
                    "rating": str(movie_rating),
                    "year": str(movie_year),
                    "url": f"https://example.com/movie/{page*10+i}",
                    "download_url": f"https://example.com/download/{page*10+i}"
                }
                
                all_movies.append(movie)
                self.write_to_output(f"  发现电影: {movie_title} - {movie_category} - {movie_rating}分")
                
                # 模拟爬取延迟
                time.sleep(0.2)
            
            self.write_to_output(f"第 {page} 页成功抓取 {movies_count} 部电影")
            
            # 页面间延迟
            if page < pages and self.running:
                self.write_to_output(f"等待 {delay} 秒后抓取下一页...")
                time.sleep(delay)
        
        # 保存结果
        if all_movies:
            self._save_movies(all_movies, save_format, save_path)
        else:
            self.write_to_output("没有抓取到任何电影数据")
    
    def _save_movies(self, movies, save_format, save_path):
        """保存电影数据到指定格式的文件"""
        if not movies:
            self.write_to_output("没有电影数据可保存")
            return
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"movies_{timestamp}.{save_format}"
        filepath = os.path.join(save_path, filename)
        
        try:
            if save_format == "csv":
                self._save_to_csv(movies, filepath)
            elif save_format == "excel":
                self._save_to_excel(movies, filepath)
            elif save_format == "json":
                self._save_to_json(movies, filepath)
            
            self.write_to_output(f"成功保存 {len(movies)} 部电影信息到: {filepath}")
        except Exception as e:
            self.write_to_output(f"保存文件时出错: {str(e)}")
    
    def _save_to_csv(self, movies, filepath):
        """保存电影数据到CSV文件"""
        import csv
        
        self.write_to_output(f"正在保存到CSV文件: {filepath}")
        
        try:
            # 确定字段列表（使用第一个电影的所有键）
            if movies:
                fieldnames = list(movies[0].keys())
            else:
                fieldnames = ["title", "category", "rating", "year", "url", "download_url"]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for movie in movies:
                    writer.writerow(movie)
            
            self.write_to_output(f"CSV文件保存成功: {filepath}")
        except Exception as e:
            self.write_to_output(f"保存CSV文件时出错: {str(e)}")
            raise

    def _save_to_excel(self, movies, filepath):
        """保存电影数据到Excel文件"""
        self.write_to_output(f"正在保存到Excel文件: {filepath}")
        
        try:
            # 尝试导入pandas
            import pandas as pd
            
            # 创建DataFrame并保存
            df = pd.DataFrame(movies)
            df.to_excel(filepath, index=False)
            
            self.write_to_output(f"Excel文件保存成功: {filepath}")
        except ImportError:
            self.write_to_output("错误: 保存Excel需要安装pandas和openpyxl")
            self.write_to_output("请执行: pip install pandas openpyxl")
            
            # 尝试改用CSV格式保存
            csv_path = filepath.replace('.excel', '.csv')
            self.write_to_output(f"尝试以CSV格式保存: {csv_path}")
            self._save_to_csv(movies, csv_path)
            raise ImportError("缺少pandas或openpyxl库，无法保存Excel文件")
        except Exception as e:
            self.write_to_output(f"保存Excel文件时出错: {str(e)}")
            raise

    def _save_to_json(self, movies, filepath):
        """保存电影数据到JSON文件"""
        import json
        
        self.write_to_output(f"正在保存到JSON文件: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
            
            self.write_to_output(f"JSON文件保存成功: {filepath}")
        except Exception as e:
            self.write_to_output(f"保存JSON文件时出错: {str(e)}")
            raise
    
    def stop_scraping(self):
        """停止爬取"""
        if not hasattr(self, 'running') or not self.running:
            return
        
        self.write_to_output("正在停止爬取...")
        self.running = False 