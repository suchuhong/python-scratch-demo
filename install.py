#!/usr/bin/env python
"""
电影天堂工具集安装脚本
"""
import os
import sys
import subprocess
import platform

def print_header():
    """打印标题"""
    print("\n" + "=" * 60)
    print("              电影天堂工具集安装向导")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print("\n检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print(f"✗ Python版本不满足要求: {sys.version}")
        print("  需要Python 3.6或更高版本")
        return False
    
    print(f"✓ Python版本满足要求: {sys.version}")
    return True

def check_pip():
    """检查pip是否可用"""
    print("\n检查pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✓ pip可用")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ pip不可用")
        return False

def install_package():
    """安装包"""
    print("\n开始安装电影天堂工具集...")
    
    # 安装依赖
    print("安装依赖...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✓ 依赖安装成功")
    except subprocess.SubprocessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False
    
    # 安装包
    print("\n安装电影天堂工具集...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                      check=True)
        print("✓ 电影天堂工具集安装成功")
    except subprocess.SubprocessError as e:
        print(f"✗ 电影天堂工具集安装失败: {e}")
        return False
    
    return True

def print_success_message():
    """打印成功信息"""
    print("\n" + "=" * 60)
    print("              安装成功!")
    print("=" * 60)
    print("\n现在您可以使用以下命令运行电影天堂工具集:")
    print("  dytt8            - 命令行界面")
    print("  dytt8-gui        - 图形用户界面")
    print("  dytt8-full       - 全功能版本")
    print("\n祝您使用愉快!")

def main():
    """主函数"""
    print_header()
    
    # 检查环境
    if not check_python_version():
        print("\n请安装Python 3.6或更高版本后再运行此脚本。")
        return
    
    if not check_pip():
        print("\n请安装pip后再运行此脚本。")
        return
    
    # 安装包
    if install_package():
        print_success_message()
    else:
        print("\n安装失败，请查看上面的错误信息。")

if __name__ == "__main__":
    main() 