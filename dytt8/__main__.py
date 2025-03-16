#!/usr/bin/env python
"""
电影天堂工具集 - 入口点脚本
提供统一界面选择要运行的脚本
"""
import os
import sys
import importlib.util
import subprocess


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """打印标题"""
    print("\n" + "=" * 60)
    print("              电影天堂工具集 v1.0")
    print("=" * 60)


def print_menu():
    """打印菜单"""
    print("\n请选择要运行的脚本:")
    print("1. 电影天堂爬虫 (dytt8_scraper.py)")
    print("2. 电影资源搜索器 (dytt8_movie_finder.py)")
    print("3. 兼容版电影天堂爬虫 (dytt8_scraper_v2.py) - 推荐")
    print("4. 简化版电影天堂工具 (dytt8_simple.py)")
    print("5. ChromeDriver兼容性修复工具 (fix_webdriver_manager.py)")
    print("0. 退出")


def check_environment():
    """检查环境是否配置正确"""
    try:
        import selenium
        print(f"✓ 已安装Selenium: 版本 {selenium.__version__}")
    except ImportError:
        print("✗ 未安装Selenium，请运行: pip install -r requirements.txt")
        return False
    
    try:
        from selenium import webdriver
        print("✓ 已导入WebDriver")
    except ImportError:
        print("✗ WebDriver导入失败")
        return False
    
    chrome_version = None
    try:
        # 在Windows上尝试获取Chrome版本
        if os.name == 'nt':
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            chrome_version = winreg.QueryValueEx(key, "version")[0]
    except:
        pass
    
    if chrome_version:
        print(f"✓ 检测到Chrome浏览器: 版本 {chrome_version}")
    else:
        print("ℹ 未能检测到Chrome版本，请确保已安装Chrome浏览器")
    
    print("\n环境检查完成。如果您遇到兼容性问题，请选择选项3或4。")
    return True


def run_script(script_name):
    """运行指定的脚本"""
    print(f"\n正在启动 {script_name}...")
    
    # 使用subprocess运行脚本，确保正确处理输入输出
    try:
        # 构建绝对路径
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        # 使用Python解释器运行脚本
        python_executable = sys.executable
        subprocess.run([python_executable, script_path], check=True)
        
    except Exception as e:
        print(f"运行脚本时出错: {e}")


def main():
    """主函数"""
    clear_screen()
    print_header()
    
    # 检查环境
    if not check_environment():
        input("\n请安装必要的依赖后再运行。按Enter键退出...")
        return
    
    while True:
        print_menu()
        choice = input("\n请输入选项编号: ").strip()
        
        if choice == '0':
            print("\n感谢使用电影天堂工具集！再见！")
            break
        elif choice == '1':
            run_script("dytt8_scraper.py")
            break
        elif choice == '2':
            run_script("dytt8_movie_finder.py")
            break
        elif choice == '3':
            run_script("dytt8_scraper_v2.py")
            break
        elif choice == '4':
            run_script("dytt8_simple.py")
            break
        elif choice == '5':
            run_script("fix_webdriver_manager.py")
            # 修复工具运行完后不退出
            input("\n按Enter键继续...")
            clear_screen()
            print_header()
        else:
            print("\n无效的选项，请重新选择！")


if __name__ == "__main__":
    main() 