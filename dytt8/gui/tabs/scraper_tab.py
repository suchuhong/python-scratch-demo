#!/usr/bin/env python
"""
电影抓取选项卡
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import subprocess

class ScraperTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="10")
        
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
        # 实现爬取功能
        pass
        
    def stop_scraping(self):
        """停止爬取"""
        # 实现停止功能
        pass 