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

# 确保父级目录在路径中，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MovieToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("电影天堂工具集 v1.1")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 设置应用图标
        try:
            if os.name == 'nt':  # Windows
                self.root.iconbitmap(os.path.join(os.path.dirname(__file__), 'icon.ico'))
            else:  # Linux/macOS
                logo = tk.PhotoImage(file=os.path.join(os.path.dirname(__file__), 'icon.png'))
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