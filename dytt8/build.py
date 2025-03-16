#!/usr/bin/env python
"""
打包脚本 - 使用PyInstaller将电影天堂工具集打包成可执行文件
"""
import os
import sys
import shutil
import platform
import subprocess

def clean_build_dirs():
    """清理build和dist目录"""
    print("清理打包目录...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    spec_files = [f for f in os.listdir() if f.endswith('.spec')]
    for spec_file in spec_files:
        os.remove(spec_file)

def build_executable():
    """打包成可执行文件"""
    print(f"开始打包电影天堂工具集...")
    
    # 平台特定设置
    icon_file = ""
    separator = ";" if platform.system() == "Windows" else ":"
    if platform.system() == "Windows":
        icon_file = "--icon=icon.ico"
    elif platform.system() == "Darwin":  # macOS
        icon_file = "--icon=icon.icns" 
    else:  # Linux
        icon_file = "--icon=icon.png"
    
    # 准备文件列表
    data_files = [
        '--add-data', f'dytt8_scraper.py{separator}.', 
        '--add-data', f'dytt8_movie_finder.py{separator}.', 
        '--add-data', f'dytt8_scraper_v2.py{separator}.', 
        '--add-data', f'dytt8_simple.py{separator}.', 
        '--add-data', f'fix_webdriver_manager.py{separator}.', 
        '--add-data', f'utils.py{separator}.', 
        '--add-data', f'requirements.txt{separator}.', 
        '--add-data', f'README.md{separator}.'
    ]
    
    # 运行PyInstaller命令
    pyinstaller_cmd = [
        'pyinstaller',
        '--name=电影天堂工具集',
        '--onefile',  # 单文件模式
        '--noconsole',  # 对于GUI应用，windows下不显示控制台
        '--clean',
        icon_file
    ] + data_files + ['main.py']
    
    # 过滤掉空的icon_file
    pyinstaller_cmd = [item for item in pyinstaller_cmd if item]
    
    try:
        # 执行PyInstaller命令
        subprocess.run(pyinstaller_cmd, check=True)
        
        # 打包完成
        output_path = os.path.join('dist', '电影天堂工具集')
        if platform.system() == "Windows":
            output_path += '.exe'
            
        print(f"\n打包完成！可执行文件位于: {output_path}")
        print("\n注意：")
        print("1. 此可执行文件仍然需要目标计算机安装Chrome浏览器")
        print("2. 首次运行时会自动下载ChromeDriver")
        print("3. 如运行出错，请使用选项5修复ChromeDriver")
        
    except Exception as e:
        print(f"打包过程中出错: {e}")
        sys.exit(1)

def main():
    """主函数"""
    # 确保在脚本所在目录下执行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 清理旧的打包文件
    clean_build_dirs()
    
    # 打包可执行文件
    build_executable()

if __name__ == "__main__":
    main() 