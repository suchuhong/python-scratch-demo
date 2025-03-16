#!/usr/bin/env python
"""
电影天堂工具集 - 全功能入口点
集成GUI、爬虫、推荐、调度和API功能
"""
import os
import sys
import argparse
import threading
import logging
import webbrowser
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "app.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('main')

def start_gui():
    """启动GUI界面"""
    try:
        from gui.app import main
        main()
    except ImportError as e:
        logger.error(f"启动GUI失败: {e}")
        print("GUI模块不可用，请确保已安装tkinter")
        print("如果你想使用命令行版本，请添加 --cli 参数")
        sys.exit(1)

def start_cli():
    """启动命令行界面"""
    from main import main as cli_main
    cli_main()

def start_api_server(port=8000):
    """启动API服务器"""
    try:
        from api.server import start_server
        start_server(port=port)
    except ImportError as e:
        logger.error(f"启动API服务器失败: {e}")
        print(f"API服务器模块不可用: {e}")
        print("请确保已安装Flask和其他依赖")
        sys.exit(1)

def start_scheduler():
    """启动任务调度器"""
    try:
        from scheduler.task_manager import TaskScheduler
        scheduler = TaskScheduler()
        scheduler.start()
        return scheduler
    except ImportError as e:
        logger.error(f"启动任务调度器失败: {e}")
        print(f"任务调度器模块不可用: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='电影天堂工具集')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面')
    parser.add_argument('--gui', action='store_true', help='使用图形界面')
    parser.add_argument('--api', action='store_true', help='启动API服务器')
    parser.add_argument('--port', type=int, default=8000, help='API服务器端口')
    parser.add_argument('--scheduler', action='store_true', help='启动任务调度器')
    parser.add_argument('--chrome', action='store_true', help='自动启动Chrome浏览器访问Web界面')
    
    args = parser.parse_args()
    
    # 如果没有指定任何参数，默认启动GUI
    if not (args.cli or args.gui or args.api or args.scheduler):
        args.gui = True
    
    # 启动组件
    scheduler = None
    api_thread = None
    
    # 启动任务调度器
    if args.scheduler:
        print("启动任务调度器...")
        scheduler = start_scheduler()
    
    # 启动API服务器
    if args.api:
        print(f"启动API服务器在端口 {args.port}...")
        api_thread = threading.Thread(target=start_api_server, args=(args.port,))
        api_thread.daemon = True  # 设置为守护线程，主线程退出时将终止
        api_thread.start()
        
        # 如果指定了--chrome参数，打开浏览器
        if args.chrome:
            url = f"http://localhost:{args.port}/"
            print(f"启动浏览器访问 {url}...")
            webbrowser.open(url)
    
    # 启动用户界面
    if args.cli:
        print("启动命令行界面...")
        start_cli()
    elif args.gui:
        print("启动图形用户界面...")
        start_gui()
    
    # 如果只启动了API服务器或调度器，保持主线程运行
    if (args.api or args.scheduler) and not (args.cli or args.gui):
        try:
            print("服务已启动，按Ctrl+C停止...")
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("接收到停止信号，正在关闭...")
            if scheduler:
                scheduler.stop()
            print("已停止所有服务")

if __name__ == "__main__":
    main() 