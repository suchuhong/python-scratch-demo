#!/usr/bin/env python
"""
电影天堂工具集 - 图形用户界面
提供更直观的用户交互体验
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import importlib.util
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class MovieToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("电影天堂工具集 v1.1")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 设置应用图标
        try:
            if os.name == 'nt':  # Windows
                self.root.iconbitmap('icon.ico')
            else:  # Linux/macOS
                logo = tk.PhotoImage(file='icon.png')
                self.root.iconphoto(True, logo)
        except:
            pass  # 图标加载失败则忽略
            
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="电影天堂工具集", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(
            title_frame, 
            text="v1.1", 
            font=("Arial", 10)
        )
        version_label.pack(side=tk.LEFT, padx=(5, 0), pady=(8, 0))
        
        # 创建选项卡控件
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # 创建各个功能的选项卡
        self.tab_scraper = ttk.Frame(self.tab_control)
        self.tab_finder = ttk.Frame(self.tab_control)
        self.tab_recommend = ttk.Frame(self.tab_control)
        self.tab_scheduler = ttk.Frame(self.tab_control)
        self.tab_settings = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_scraper, text="电影抓取")
        self.tab_control.add(self.tab_finder, text="电影搜索")
        self.tab_control.add(self.tab_recommend, text="电影推荐")
        self.tab_control.add(self.tab_scheduler, text="定时任务")
        self.tab_control.add(self.tab_settings, text="设置")
        
        self.tab_control.pack(expand=1, fill=tk.BOTH)
        
        # 初始化各选项卡的内容
        self.init_scraper_tab()
        self.init_finder_tab()
        self.init_recommend_tab()
        self.init_scheduler_tab()
        self.init_settings_tab()
        
        # 创建状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 检查环境
        self.check_environment()
    
    def init_scraper_tab(self):
        """初始化电影抓取选项卡"""
        frame = ttk.Frame(self.tab_scraper, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 选择爬虫版本
        ttk.Label(frame, text="选择爬虫版本:", font=("Arial", 11)).grid(column=0, row=0, sticky=tk.W, pady=(0, 10))
        
        self.scraper_var = tk.StringVar(value="v2")
        ttk.Radiobutton(frame, text="标准版 (dytt8_scraper.py)", variable=self.scraper_var, value="v1").grid(column=0, row=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="兼容版 (dytt8_scraper_v2.py) - 推荐", variable=self.scraper_var, value="v2").grid(column=0, row=2, sticky=tk.W)
        ttk.Radiobutton(frame, text="简化版 (dytt8_simple.py)", variable=self.scraper_var, value="simple").grid(column=0, row=3, sticky=tk.W)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(column=0, row=4, sticky=tk.EW, pady=10)
        
        # 爬取参数
        ttk.Label(frame, text="爬取设置:", font=("Arial", 11)).grid(column=0, row=5, sticky=tk.W, pady=(0, 10))
        
        param_frame = ttk.Frame(frame)
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
        save_frame = ttk.Frame(frame)
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
        ttk.Label(frame, text="运行日志:", font=("Arial", 11)).grid(column=0, row=8, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=12)
        self.output_text.grid(column=0, row=9, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_text.config(state=tk.DISABLED)
        
        # 按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(column=0, row=10, sticky=tk.E, pady=(10, 0))
        
        self.start_btn = ttk.Button(btn_frame, text="开始抓取", command=self.start_scraping, width=15)
        self.start_btn.grid(column=0, row=0, sticky=tk.E, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_scraping, width=10, state=tk.DISABLED)
        self.stop_btn.grid(column=1, row=0, sticky=tk.E)
        
        # 配置Grid权重，使输出区域可以随窗口大小调整
        frame.grid_rowconfigure(9, weight=1)
        frame.grid_columnconfigure(0, weight=1)
    
    def init_finder_tab(self):
        """初始化电影搜索选项卡"""
        frame = ttk.Frame(self.tab_finder, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 搜索区域
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="电影名称:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_movie())
        
        ttk.Button(search_frame, text="搜索", command=self.search_movie).pack(side=tk.LEFT)
        
        # 搜索结果
        result_frame = ttk.LabelFrame(frame, text="搜索结果")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("title", "year", "category", "format", "size")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        # 定义列
        self.result_tree.heading("title", text="电影名称")
        self.result_tree.heading("year", text="年份")
        self.result_tree.heading("category", text="类别")
        self.result_tree.heading("format", text="格式")
        self.result_tree.heading("size", text="大小")
        
        self.result_tree.column("title", width=300)
        self.result_tree.column("year", width=60)
        self.result_tree.column("category", width=80)
        self.result_tree.column("format", width=60)
        self.result_tree.column("size", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 双击打开下载链接
        self.result_tree.bind("<Double-1>", self.open_download_link)
        
        # 状态标签
        self.finder_status_var = tk.StringVar(value="请输入电影名称进行搜索")
        status_label = ttk.Label(frame, textvariable=self.finder_status_var)
        status_label.pack(fill=tk.X, pady=(5, 0))
    
    def init_recommend_tab(self):
        """初始化电影推荐选项卡"""
        frame = ttk.Frame(self.tab_recommend, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 喜好设置
        pref_frame = ttk.LabelFrame(frame, text="我的电影喜好")
        pref_frame.pack(fill=tk.X, pady=(0, 10))
        
        genre_frame = ttk.Frame(pref_frame)
        genre_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(genre_frame, text="喜欢的类型:").grid(row=0, column=0, sticky=tk.W)
        
        self.genre_vars = {}
        genres = ["动作", "喜剧", "爱情", "科幻", "恐怖", "动画", "剧情", "战争", "纪录片"]
        col = 1
        for genre in genres:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(genre_frame, text=genre, variable=var)
            cb.grid(row=0, column=col, padx=5)
            self.genre_vars[genre] = var
            col += 1
        
        years_frame = ttk.Frame(pref_frame)
        years_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(years_frame, text="喜欢的年代:").grid(row=0, column=0, sticky=tk.W)
        
        self.year_range_var = tk.StringVar(value="2000-至今")
        year_ranges = ["不限", "2020-至今", "2010-2020", "2000-2010", "90年代", "80年代", "更早"]
        ttk.Combobox(years_frame, values=year_ranges, textvariable=self.year_range_var, width=10).grid(row=0, column=1, padx=5)
        
        regions_frame = ttk.Frame(pref_frame)
        regions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(regions_frame, text="地区偏好:").grid(row=0, column=0, sticky=tk.W)
        
        self.region_vars = {}
        regions = ["中国大陆", "中国香港", "中国台湾", "美国", "韩国", "日本", "欧洲", "其他"]
        col = 1
        for region in regions:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(regions_frame, text=region, variable=var)
            cb.grid(row=0, column=col, padx=5)
            self.region_vars[region] = var
            col += 1
            if col > 4:
                col = 1
                regions_frame.grid_rowconfigure(1, weight=1)
        
        # 历史记录导入
        history_frame = ttk.Frame(pref_frame)
        history_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Label(history_frame, text="导入观影历史:").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(history_frame, text="选择CSV文件", command=self.import_history).grid(row=0, column=1, padx=5)
        
        self.history_status_var = tk.StringVar(value="未导入")
        ttk.Label(history_frame, textvariable=self.history_status_var).grid(row=0, column=2, padx=5)
        
        # 推荐结果
        recommend_btn_frame = ttk.Frame(frame)
        recommend_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(recommend_btn_frame, text="获取推荐电影", command=self.get_recommendations, width=20).pack(side=tk.LEFT)
        
        self.recommend_source_var = tk.StringVar(value="all")
        ttk.Radiobutton(recommend_btn_frame, text="所有来源", variable=self.recommend_source_var, value="all").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Radiobutton(recommend_btn_frame, text="仅电影天堂", variable=self.recommend_source_var, value="dytt").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(recommend_btn_frame, text="仅豆瓣", variable=self.recommend_source_var, value="douban").pack(side=tk.LEFT, padx=5)
        
        # 推荐结果表格
        result_frame = ttk.LabelFrame(frame, text="为您推荐的电影")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("rank", "title", "year", "rating", "reason", "source")
        self.recommend_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        
        # 定义列
        self.recommend_tree.heading("rank", text="#")
        self.recommend_tree.heading("title", text="电影名称")
        self.recommend_tree.heading("year", text="年份")
        self.recommend_tree.heading("rating", text="评分")
        self.recommend_tree.heading("reason", text="推荐理由")
        self.recommend_tree.heading("source", text="数据来源")
        
        self.recommend_tree.column("rank", width=30)
        self.recommend_tree.column("title", width=250)
        self.recommend_tree.column("year", width=60)
        self.recommend_tree.column("rating", width=60)
        self.recommend_tree.column("reason", width=250)
        self.recommend_tree.column("source", width=80)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.recommend_tree.yview)
        self.recommend_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recommend_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 双击查看详情
        self.recommend_tree.bind("<Double-1>", self.show_movie_details)
    
    def init_scheduler_tab(self):
        """初始化定时任务选项卡"""
        frame = ttk.Frame(self.tab_scheduler, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 任务设置
        task_frame = ttk.LabelFrame(frame, text="定时任务设置")
        task_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 任务类型
        type_frame = ttk.Frame(task_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(type_frame, text="任务类型:").grid(row=0, column=0, sticky=tk.W)
        
        self.task_type_var = tk.StringVar(value="scrape")
        ttk.Radiobutton(type_frame, text="爬取电影", variable=self.task_type_var, value="scrape").grid(row=0, column=1, padx=(5, 15))
        ttk.Radiobutton(type_frame, text="更新推荐", variable=self.task_type_var, value="recommend").grid(row=0, column=2, padx=5)
        
        # 时间设置
        schedule_frame = ttk.Frame(task_frame)
        schedule_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(schedule_frame, text="执行频率:").grid(row=0, column=0, sticky=tk.W)
        
        self.schedule_freq_var = tk.StringVar(value="daily")
        freq_combo = ttk.Combobox(schedule_frame, values=["每小时", "每天", "每周", "每月"], textvariable=self.schedule_freq_var, width=10)
        freq_combo.grid(row=0, column=1, padx=5)
        freq_combo.bind("<<ComboboxSelected>>", self.update_schedule_options)
        
        # 时间选择框架
        self.time_options_frame = ttk.Frame(task_frame)
        self.time_options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 初始化为"每天"选项
        self.init_daily_schedule()
        
        # 任务参数
        param_frame = ttk.Frame(task_frame)
        param_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Label(param_frame, text="使用与对应选项卡相同的参数配置").grid(row=0, column=0, sticky=tk.W)
        
        # 任务列表
        task_list_frame = ttk.LabelFrame(frame, text="计划任务列表")
        task_list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("status", "type", "schedule", "next_run", "last_run")
        self.task_tree = ttk.Treeview(task_list_frame, columns=columns, show="headings")
        
        # 定义列
        self.task_tree.heading("status", text="状态")
        self.task_tree.heading("type", text="任务类型")
        self.task_tree.heading("schedule", text="执行计划")
        self.task_tree.heading("next_run", text="下次执行")
        self.task_tree.heading("last_run", text="上次执行")
        
        self.task_tree.column("status", width=60)
        self.task_tree.column("type", width=100)
        self.task_tree.column("schedule", width=200)
        self.task_tree.column("next_run", width=150)
        self.task_tree.column("last_run", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(task_list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 任务操作按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="添加任务", command=self.add_task, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除任务", command=self.delete_task, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="暂停任务", command=self.pause_task, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="启动任务", command=self.resume_task, width=15).pack(side=tk.LEFT)
    
    def init_daily_schedule(self):
        """初始化每日计划UI"""
        # 清除现有内容
        for widget in self.time_options_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.time_options_frame, text="执行时间:").grid(row=0, column=0, sticky=tk.W)
        
        # 小时选择
        self.hour_var = tk.StringVar(value="03")
        hours = [f"{h:02d}" for h in range(24)]
        ttk.Combobox(self.time_options_frame, values=hours, textvariable=self.hour_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(self.time_options_frame, text=":").grid(row=0, column=2)
        
        # 分钟选择
        self.minute_var = tk.StringVar(value="00")
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ttk.Combobox(self.time_options_frame, values=minutes, textvariable=self.minute_var, width=5).grid(row=0, column=3, padx=5)
    
    def init_weekly_schedule(self):
        """初始化每周计划UI"""
        # 清除现有内容
        for widget in self.time_options_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.time_options_frame, text="执行日:").grid(row=0, column=0, sticky=tk.W)
        
        # 周几选择
        self.weekday_var = tk.StringVar(value="星期一")
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        ttk.Combobox(self.time_options_frame, values=weekdays, textvariable=self.weekday_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(self.time_options_frame, text="时间:").grid(row=0, column=2, padx=(10, 5))
        
        # 小时选择
        self.hour_var = tk.StringVar(value="03")
        hours = [f"{h:02d}" for h in range(24)]
        ttk.Combobox(self.time_options_frame, values=hours, textvariable=self.hour_var, width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(self.time_options_frame, text=":").grid(row=0, column=4)
        
        # 分钟选择
        self.minute_var = tk.StringVar(value="00")
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ttk.Combobox(self.time_options_frame, values=minutes, textvariable=self.minute_var, width=5).grid(row=0, column=5, padx=5)
    
    def init_monthly_schedule(self):
        """初始化每月计划UI"""
        # 清除现有内容
        for widget in self.time_options_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.time_options_frame, text="执行日期:").grid(row=0, column=0, sticky=tk.W)
        
        # 日期选择
        self.day_var = tk.StringVar(value="1")
        days = [str(d) for d in range(1, 32)]
        ttk.Combobox(self.time_options_frame, values=days, textvariable=self.day_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(self.time_options_frame, text="时间:").grid(row=0, column=2, padx=(10, 5))
        
        # 小时选择
        self.hour_var = tk.StringVar(value="03")
        hours = [f"{h:02d}" for h in range(24)]
        ttk.Combobox(self.time_options_frame, values=hours, textvariable=self.hour_var, width=5).grid(row=0, column=3, padx=5)
        
        ttk.Label(self.time_options_frame, text=":").grid(row=0, column=4)
        
        # 分钟选择
        self.minute_var = tk.StringVar(value="00")
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ttk.Combobox(self.time_options_frame, values=minutes, textvariable=self.minute_var, width=5).grid(row=0, column=5, padx=5)
    
    def init_hourly_schedule(self):
        """初始化每小时计划UI"""
        # 清除现有内容
        for widget in self.time_options_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.time_options_frame, text="执行分钟:").grid(row=0, column=0, sticky=tk.W)
        
        # 分钟选择
        self.minute_var = tk.StringVar(value="00")
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        ttk.Combobox(self.time_options_frame, values=minutes, textvariable=self.minute_var, width=5).grid(row=0, column=1, padx=5)
    
    def init_settings_tab(self):
        """初始化设置选项卡"""
        frame = ttk.Frame(self.tab_settings, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 基本设置
        basic_frame = ttk.LabelFrame(frame, text="基本设置")
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 数据保存设置
        save_frame = ttk.Frame(basic_frame)
        save_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(save_frame, text="默认保存格式:").grid(row=0, column=0, sticky=tk.W)
        
        self.default_format_var = tk.StringVar(value="csv")
        formats = ["csv", "excel", "json"]
        ttk.Combobox(save_frame, values=formats, textvariable=self.default_format_var, width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(save_frame, text="默认保存路径:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.default_path_var = tk.StringVar(value=os.getcwd())
        path_frame = ttk.Frame(save_frame)
        path_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        ttk.Entry(path_frame, textvariable=self.default_path_var, width=40).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Button(path_frame, text="浏览...", command=self.browse_default_path).grid(row=0, column=1, sticky=tk.W)
        
        # 浏览器设置
        browser_frame = ttk.LabelFrame(frame, text="浏览器设置")
        browser_frame.pack(fill=tk.X, pady=(0, 10))
        
        driver_frame = ttk.Frame(browser_frame)
        driver_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(driver_frame, text="WebDriver模式:").grid(row=0, column=0, sticky=tk.W)
        
        self.driver_mode_var = tk.StringVar(value="auto")
        ttk.Radiobutton(driver_frame, text="自动管理", variable=self.driver_mode_var, value="auto").grid(row=0, column=1, padx=(5, 15))
        ttk.Radiobutton(driver_frame, text="手动设置", variable=self.driver_mode_var, value="manual").grid(row=0, column=2, padx=5)
        
        ttk.Label(driver_frame, text="ChromeDriver路径:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.driver_path_var = tk.StringVar()
        driver_path_frame = ttk.Frame(driver_frame)
        driver_path_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(10, 0))
        
        driver_path_entry = ttk.Entry(driver_path_frame, textvariable=self.driver_path_var, width=40)
        driver_path_entry.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        driver_path_entry.config(state="disabled")
        
        self.browse_driver_btn = ttk.Button(driver_path_frame, text="浏览...", command=self.browse_driver_path, state=tk.DISABLED)
        self.browse_driver_btn.grid(row=0, column=1, sticky=tk.W)
        
        # 绑定事件
        self.driver_mode_var.trace("w", self.toggle_driver_path)
        
        # 代理设置
        proxy_frame = ttk.LabelFrame(frame, text="代理设置")
        proxy_frame.pack(fill=tk.X, pady=(0, 10))
        
        proxy_options_frame = ttk.Frame(proxy_frame)
        proxy_options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(proxy_options_frame, text="使用代理:").grid(row=0, column=0, sticky=tk.W)
        
        self.use_proxy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(proxy_options_frame, variable=self.use_proxy_var, command=self.toggle_proxy).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(proxy_options_frame, text="代理地址:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.proxy_var = tk.StringVar()
        self.proxy_entry = ttk.Entry(proxy_options_frame, textvariable=self.proxy_var, width=40)
        self.proxy_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        self.proxy_entry.config(state="disabled")
        
        ttk.Label(proxy_options_frame, text="格式: http://host:port").grid(row=2, column=1, sticky=tk.W)
        
        # 数据来源设置
        source_frame = ttk.LabelFrame(frame, text="数据来源设置")
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        source_options_frame = ttk.Frame(source_frame)
        source_options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(source_options_frame, text="启用电影天堂:").grid(row=0, column=0, sticky=tk.W)
        
        self.use_dytt_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(source_options_frame, variable=self.use_dytt_var).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(source_options_frame, text="启用豆瓣电影:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.use_douban_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(source_options_frame, variable=self.use_douban_var).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # API设置
        api_frame = ttk.LabelFrame(frame, text="API设置")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        api_options_frame = ttk.Frame(api_frame)
        api_options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(api_options_frame, text="启用API服务:").grid(row=0, column=0, sticky=tk.W)
        
        self.use_api_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(api_options_frame, variable=self.use_api_var, command=self.toggle_api).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(api_options_frame, text="API端口:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        self.api_port_var = tk.StringVar(value="8000")
        self.api_port_entry = ttk.Entry(api_options_frame, textvariable=self.api_port_var, width=10)
        self.api_port_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        self.api_port_entry.config(state="disabled")
        
        # 保存和重置按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="保存设置", command=self.save_settings, width=15).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="重置", command=self.reset_settings, width=10).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="修复ChromeDriver", command=self.fix_chrome_driver, width=20).pack(side=tk.LEFT)
    
    # 辅助方法
    def check_environment(self):
        """检查环境配置"""
        try:
            # 尝试导入selenium
            import selenium
            version = selenium.__version__
            self.write_to_output(f"✓ 已安装Selenium: 版本 {version}")
            
            # 尝试导入WebDriver
            from selenium import webdriver
            self.write_to_output("✓ 已导入WebDriver")
            
            # 检查Chrome版本
            chrome_version = None
            try:
                # 在Windows上尝试获取Chrome版本
                if os.name == 'nt':
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
                    chrome_version = winreg.QueryValueEx(key, "version")[0]
            except Exception:
                pass
            
            if chrome_version:
                self.write_to_output(f"✓ 检测到Chrome浏览器: 版本 {chrome_version}")
            else:
                self.write_to_output("ℹ 未能检测到Chrome版本，请确保已安装Chrome浏览器")
            
            self.write_to_output("\n环境检查完成。如果您遇到兼容性问题，请使用设置选项卡中的'修复ChromeDriver'功能。")
            return True
            
        except ImportError as e:
            self.write_to_output(f"✗ 导入错误: {e}")
            self.write_to_output("请确保已安装所有依赖: pip install -r requirements.txt")
            return False
    
    def write_to_output(self, text):
        """写入输出区域"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def browse_save_path(self):
        """浏览保存路径"""
        path = filedialog.askdirectory()
        if path:
            self.save_path_var.set(path)
    
    def browse_default_path(self):
        """浏览默认保存路径"""
        path = filedialog.askdirectory()
        if path:
            self.default_path_var.set(path)
    
    def browse_driver_path(self):
        """浏览ChromeDriver路径"""
        path = filedialog.askopenfilename(
            filetypes=[("ChromeDriver", "chromedriver.exe"), ("All Files", "*.*")]
        )
        if path:
            self.driver_path_var.set(path)
    
    def toggle_driver_path(self, *args):
        """切换ChromeDriver路径输入状态"""
        if self.driver_mode_var.get() == "manual":
            self.browse_driver_btn.config(state=tk.NORMAL)
            for child in self.browse_driver_btn.master.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.config(state=tk.NORMAL)
        else:
            self.browse_driver_btn.config(state=tk.DISABLED)
            for child in self.browse_driver_btn.master.winfo_children():
                if isinstance(child, ttk.Entry):
                    child.config(state=tk.DISABLED)
    
    def toggle_proxy(self):
        """切换代理设置状态"""
        if self.use_proxy_var.get():
            self.proxy_entry.config(state=tk.NORMAL)
        else:
            self.proxy_entry.config(state=tk.DISABLED)
    
    def toggle_api(self):
        """切换API设置状态"""
        if self.use_api_var.get():
            self.api_port_entry.config(state=tk.NORMAL)
        else:
            self.api_port_entry.config(state=tk.DISABLED)
    
    def update_schedule_options(self, event):
        """根据选择的执行频率更新UI"""
        freq = self.schedule_freq_var.get()
        if freq == "每天":
            self.init_daily_schedule()
        elif freq == "每周":
            self.init_weekly_schedule()
        elif freq == "每月":
            self.init_monthly_schedule()
        elif freq == "每小时":
            self.init_hourly_schedule()
    
    # 功能方法
    def start_scraping(self):
        """开始爬取电影数据"""
        # 禁用开始按钮，启用停止按钮
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 清空输出区域
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        # 获取参数
        scraper_version = self.scraper_var.get()
        pages = int(self.page_var.get())
        delay = float(self.delay_var.get())
        category = self.category_var.get()
        save_format = self.save_option_var.get()
        save_path = self.save_path_var.get()
        
        # 更新状态
        self.status_var.set("正在爬取电影数据...")
        self.write_to_output(f"开始爬取电影数据...")
        self.write_to_output(f"使用爬虫版本: {scraper_version}")
        self.write_to_output(f"页数: {pages}, 延迟: {delay}秒, 类别: {category}")
        self.write_to_output(f"保存格式: {save_format}, 路径: {save_path}")
        
        # 在新线程中运行爬虫
        threading.Thread(target=self.run_scraper, args=(
            scraper_version, pages, delay, category, save_format, save_path
        )).start()
    
    def run_scraper(self, version, pages, delay, category, save_format, save_path):
        """在线程中运行爬虫"""
        try:
            # 根据不同版本选择不同脚本
            script_name = ""
            if version == "v1":
                script_name = "dytt8_scraper.py"
            elif version == "v2":
                script_name = "dytt8_scraper_v2.py"
            elif version == "simple":
                script_name = "dytt8_simple.py"
            
            # 构建脚本路径
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            
            # 构建命令行参数
            cmd_args = [
                sys.executable,
                script_path,
                "--pages", str(pages),
                "--delay", str(delay),
                "--category", category,
                "--format", save_format,
                "--output", save_path
            ]
            
            # 运行子进程
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.write_to_output(line.strip())
            
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.write_to_output("爬取完成!")
                self.status_var.set("爬取完成")
            else:
                self.write_to_output(f"爬取过程中出错，返回代码: {return_code}")
                self.status_var.set("爬取出错")
            
        except Exception as e:
            self.write_to_output(f"发生错误: {e}")
            self.status_var.set("爬取出错")
        
        finally:
            # 恢复按钮状态
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_scraping(self):
        """停止爬取"""
        self.write_to_output("正在尝试停止爬取...")
        # 这里需要实现停止子进程的逻辑
        # 暂时实现为简单的状态更新
        self.status_var.set("已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def search_movie(self):
        """搜索电影"""
        query = self.search_var.get().strip()
        if not query:
            self.finder_status_var.set("请输入电影名称进行搜索")
            return
        
        # 清空现有结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        self.finder_status_var.set("正在搜索...")
        
        # 在新线程中运行搜索
        threading.Thread(target=self.run_search, args=(query,)).start()
    
    def run_search(self, query):
        """在线程中运行搜索"""
        try:
            # 构建脚本路径
            script_path = os.path.join(os.path.dirname(__file__), "dytt8_movie_finder.py")
            
            # 构建命令行参数
            cmd_args = [
                sys.executable,
                script_path,
                "--query", query,
                "--json"  # 以JSON格式输出便于解析
            ]
            
            # 运行子进程
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # 解析JSON结果
                import json
                try:
                    results = json.loads(stdout)
                    if results:
                        for i, movie in enumerate(results, 1):
                            self.result_tree.insert("", "end", values=(
                                movie.get("title", "未知"),
                                movie.get("year", ""),
                                movie.get("category", ""),
                                movie.get("format", ""),
                                movie.get("size", "")
                            ), tags=(json.dumps(movie),))
                        self.finder_status_var.set(f"共找到 {len(results)} 个结果")
                    else:
                        self.finder_status_var.set("未找到相关电影")
                except json.JSONDecodeError:
                    self.finder_status_var.set("解析结果失败")
            else:
                self.finder_status_var.set(f"搜索出错: {stderr}")
        
        except Exception as e:
            self.finder_status_var.set(f"发生错误: {e}")
    
    def open_download_link(self, event):
        """打开下载链接"""
        selected_item = self.result_tree.selection()
        if not selected_item:
            return
        
        # 获取电影数据
        try:
            import json
            tags = self.result_tree.item(selected_item[0], "tags")
            if tags:
                movie_data = json.loads(tags[0])
                download_link = movie_data.get("download_link")
                if download_link:
                    # 尝试打开浏览器
                    import webbrowser
                    webbrowser.open(download_link)
                else:
                    messagebox.showinfo("提示", "没有可用的下载链接")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开下载链接: {e}")
    
    def import_history(self):
        """导入观影历史"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                # 简单读取文件，此处可以扩展为更复杂的数据处理
                import pandas as pd
                df = pd.read_csv(file_path)
                self.history_status_var.set(f"已导入 {len(df)} 条记录")
            except Exception as e:
                messagebox.showerror("导入错误", f"无法导入文件: {e}")
    
    def get_recommendations(self):
        """获取电影推荐"""
        # 清空现有推荐
        for item in self.recommend_tree.get_children():
            self.recommend_tree.delete(item)
        
        # 收集用户喜好
        genres = [genre for genre, var in self.genre_vars.items() if var.get()]
        year_range = self.year_range_var.get()
        regions = [region for region, var in self.region_vars.items() if var.get()]
        recommend_source = self.recommend_source_var.get()
        
        if not genres and not regions:
            messagebox.showinfo("提示", "请至少选择一个喜好类型或地区")
            return
        
        # 模拟推荐结果，实际应该调用推荐算法
        # 这里仅做界面演示
        import random
        
        # 模拟电影数据
        sample_movies = [
            ("黑客帝国", "1999", "9.0", "经典科幻动作片，符合您的科幻喜好", "豆瓣"),
            ("肖申克的救赎", "1994", "9.7", "经典剧情片，高分推荐", "豆瓣"),
            ("寻梦环游记", "2017", "9.1", "高口碑动画片，符合您的动画喜好", "豆瓣"),
            ("釜山行", "2016", "8.5", "优秀的韩国丧尸片，符合您的恐怖喜好", "豆瓣"),
            ("流浪地球", "2019", "8.0", "中国科幻代表作，符合您的地区偏好", "电影天堂"),
            ("我不是药神", "2018", "9.0", "现实题材佳作，符合您的剧情喜好", "电影天堂"),
            ("让子弹飞", "2010", "9.0", "黑色幽默佳作，符合您的喜剧喜好", "电影天堂"),
            ("西虹市首富", "2018", "6.6", "喜剧片，符合您的喜剧喜好", "电影天堂"),
            ("你好，李焕英", "2021", "8.1", "喜剧催泪，符合您的喜剧喜好", "电影天堂"),
            ("复仇者联盟4", "2019", "8.5", "漫威系列最终章，符合您的动作喜好", "电影天堂")
        ]
        
        # 根据数据源筛选
        if recommend_source == "douban":
            filtered_movies = [m for m in sample_movies if m[4] == "豆瓣"]
        elif recommend_source == "dytt":
            filtered_movies = [m for m in sample_movies if m[4] == "电影天堂"]
        else:
            filtered_movies = sample_movies
        
        # 显示推荐结果
        for i, movie in enumerate(filtered_movies, 1):
            self.recommend_tree.insert("", "end", values=(
                i, movie[0], movie[1], movie[2], movie[3], movie[4]
            ))
    
    def show_movie_details(self, event):
        """显示电影详情"""
        selected_item = self.recommend_tree.selection()
        if not selected_item:
            return
        
        # 获取电影数据
        values = self.recommend_tree.item(selected_item[0], "values")
        if values:
            title = values[1]
            year = values[2]
            rating = values[3]
            reason = values[4]
            source = values[5]
            
            # 显示详情对话框
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"{title} ({year})")
            detail_window.geometry("500x400")
            detail_window.transient(self.root)  # 设置为主窗口的子窗口
            
            # 内容框架
            content_frame = ttk.Frame(detail_window, padding="20")
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # 电影信息
            ttk.Label(content_frame, text=title, font=("Arial", 16, "bold")).pack(anchor=tk.W)
            ttk.Label(content_frame, text=f"年份: {year}").pack(anchor=tk.W, pady=(10, 0))
            ttk.Label(content_frame, text=f"评分: {rating}").pack(anchor=tk.W, pady=(5, 0))
            ttk.Label(content_frame, text=f"数据来源: {source}").pack(anchor=tk.W, pady=(5, 0))
            
            ttk.Label(content_frame, text="推荐理由:", font=("Arial", 11)).pack(anchor=tk.W, pady=(15, 5))
            reason_text = tk.Text(content_frame, wrap=tk.WORD, height=5)
            reason_text.pack(fill=tk.X)
            reason_text.insert(tk.END, reason)
            reason_text.config(state=tk.DISABLED)
            
            # 按钮区域
            btn_frame = ttk.Frame(content_frame)
            btn_frame.pack(fill=tk.X, pady=(20, 0))
            
            ttk.Button(btn_frame, text="关闭", command=detail_window.destroy, width=10).pack(side=tk.RIGHT)
            ttk.Button(btn_frame, text="搜索此电影", command=lambda: self.search_specific_movie(title), width=15).pack(side=tk.LEFT)
    
    def search_specific_movie(self, title):
        """搜索特定电影"""
        # 切换到搜索选项卡
        self.tab_control.select(self.tab_finder)
        
        # 设置搜索内容并执行搜索
        self.search_var.set(title)
        self.search_movie()
    
    def add_task(self):
        """添加计划任务"""
        # 获取任务设置
        task_type = self.task_type_var.get()
        schedule_freq = self.schedule_freq_var.get()
        
        # 生成计划描述
        schedule_desc = ""
        if schedule_freq == "每小时":
            minute = self.minute_var.get()
            schedule_desc = f"{schedule_freq} {minute}分"
            next_run = "下一个整点"
        elif schedule_freq == "每天":
            hour = self.hour_var.get()
            minute = self.minute_var.get()
            schedule_desc = f"{schedule_freq} {hour}:{minute}"
            next_run = f"明天 {hour}:{minute}"
        elif schedule_freq == "每周":
            weekday = self.weekday_var.get()
            hour = self.hour_var.get()
            minute = self.minute_var.get()
            schedule_desc = f"{schedule_freq} {weekday} {hour}:{minute}"
            next_run = f"下个{weekday} {hour}:{minute}"
        elif schedule_freq == "每月":
            day = self.day_var.get()
            hour = self.hour_var.get()
            minute = self.minute_var.get()
            schedule_desc = f"{schedule_freq} {day}日 {hour}:{minute}"
            next_run = f"下月{day}日 {hour}:{minute}"
        
        # 任务类型描述
        task_desc = "电影抓取" if task_type == "scrape" else "电影推荐更新"
        
        # 添加到任务列表
        self.task_tree.insert("", "end", values=(
            "活动", task_desc, schedule_desc, next_run, "从未运行"
        ))
        
        messagebox.showinfo("成功", f"已添加计划任务: {schedule_desc} {task_desc}")
    
    def delete_task(self):
        """删除计划任务"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要删除的任务")
            return
        
        for item in selected_items:
            self.task_tree.delete(item)
    
    def pause_task(self):
        """暂停计划任务"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要暂停的任务")
            return
        
        for item in selected_items:
            self.task_tree.item(item, values=(
                "暂停", *self.task_tree.item(item, "values")[1:]
            ))
    
    def resume_task(self):
        """恢复计划任务"""
        selected_items = self.task_tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要启动的任务")
            return
        
        for item in selected_items:
            self.task_tree.item(item, values=(
                "活动", *self.task_tree.item(item, "values")[1:]
            ))
    
    def save_settings(self):
        """保存设置"""
        # 实际实现中应该将设置写入配置文件
        messagebox.showinfo("成功", "设置已保存")
    
    def reset_settings(self):
        """重置设置"""
        # 实际实现中应该重置为默认设置
        self.default_format_var.set("csv")
        self.default_path_var.set(os.getcwd())
        self.driver_mode_var.set("auto")
        self.driver_path_var.set("")
        self.use_proxy_var.set(False)
        self.proxy_var.set("")
        self.use_dytt_var.set(True)
        self.use_douban_var.set(False)
        self.use_api_var.set(False)
        self.api_port_var.set("8000")
        
        # 更新UI状态
        self.toggle_driver_path()
        self.toggle_proxy()
        self.toggle_api()
        
        messagebox.showinfo("成功", "设置已重置为默认值")
    
    def fix_chrome_driver(self):
        """修复ChromeDriver"""
        self.write_to_output("正在修复ChromeDriver...")
        
        try:
            # 构建脚本路径
            script_path = os.path.join(os.path.dirname(__file__), "fix_webdriver_manager.py")
            
            # 运行修复脚本
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 读取输出
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.write_to_output(line.strip())
            
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.write_to_output("ChromeDriver修复完成!")
                messagebox.showinfo("成功", "ChromeDriver已成功修复")
            else:
                self.write_to_output(f"修复过程中出错，返回代码: {return_code}")
                messagebox.showerror("错误", "ChromeDriver修复失败")
            
        except Exception as e:
            self.write_to_output(f"发生错误: {e}")
            messagebox.showerror("错误", f"修复过程中出错: {e}")

def main():
    """主函数"""
    root = tk.Tk()
    app = MovieToolkitGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 