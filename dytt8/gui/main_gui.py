#!/usr/bin/env python
"""
电影天堂工具集 - GUI入口点
"""
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_gui():
    """启动GUI界面"""
    try:
        from gui.app import main
        main()
    except ImportError as e:
        print(f"GUI模块加载失败: {e}")
        print("请确保已安装tkinter")
        sys.exit(1)

if __name__ == "__main__":
    start_gui() 