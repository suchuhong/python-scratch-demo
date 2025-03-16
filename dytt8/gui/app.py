#!/usr/bin/env python
"""
电影天堂工具集 - 图形用户界面主应用
"""
import os
import sys
import tkinter as tk
from tkinter import ttk

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 仅导入现有的选项卡模块
from dytt8.gui.tabs.scraper_tab import ScraperTab

class MovieToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("电影天堂工具集 v1.1")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 设置应用图标
        try:
            if os.name == 'nt':  # Windows
                icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.ico')
                self.root.iconbitmap(icon_path)
            else:  # Linux/macOS
                icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.png')
                logo = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, logo)
        except Exception as e:
            print(f"加载图标失败: {e}")
            
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        self.create_title()
        
        # 创建选项卡控件
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # 创建各个功能的选项卡
        self.scraper_tab = ScraperTab(self.tab_control)
        
        self.tab_control.add(self.scraper_tab.frame, text="电影抓取")
        
        # 创建临时占位标签提示其他功能未实现
        for tab_name in ["电影搜索", "电影推荐", "定时任务", "设置"]:
            temp_frame = ttk.Frame(self.tab_control, padding="20")
            ttk.Label(temp_frame, text=f"{tab_name}功能正在开发中...", font=("Arial", 14)).pack(pady=100)
            self.tab_control.add(temp_frame, text=tab_name)
        
        self.tab_control.pack(expand=1, fill=tk.BOTH)
        
        # 创建状态栏
        self.create_status_bar()
        
        # 检查环境
        self.check_environment()
    
    def create_title(self):
        """创建标题栏"""
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
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_bar = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def check_environment(self):
        """检查环境配置"""
        # 检查Selenium等依赖
        try:
            import selenium
            self.status_var.set(f"Selenium已安装 - 版本{selenium.__version__}")
        except ImportError:
            self.status_var.set("警告: Selenium未安装，某些功能可能不可用")

def main():
    """主函数"""
    root = tk.Tk()
    app = MovieToolkitGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 