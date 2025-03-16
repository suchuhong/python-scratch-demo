#!/usr/bin/env python
"""
电影天堂工具集 - GUI版本入口点
"""
import os
import sys

# 确保父级目录在路径中，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def start_gui():
    """启动GUI界面"""
    try:
        from moviegui.app import main
        main()
    except ImportError as e:
        print(f"GUI模块不可用: {e}")
        print("请确保已安装tkinter")
        print("如果你想使用命令行版本，请运行 main.py")
        sys.exit(1)

if __name__ == "__main__":
    start_gui() 