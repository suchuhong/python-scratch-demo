"""
修复 webdriver_manager 兼容性问题的脚本

该脚本将检查已安装的 webdriver_manager 版本，并更新缓存的 ChromeDriver。
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def print_step(message):
    """打印带格式的步骤信息"""
    print(f"\n{'='*80}\n{message}\n{'='*80}")


def main():
    print_step("开始修复 webdriver_manager 兼容性问题")
    
    # 检查 Python 版本
    print(f"Python 版本: {sys.version}")
    
    # 检查 webdriver_manager 版本
    try:
        import webdriver_manager
        print(f"webdriver_manager 版本: {webdriver_manager.__version__}")
    except ImportError:
        print("未安装 webdriver_manager，尝试安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "webdriver-manager"], check=True)
        import webdriver_manager
        print(f"已安装 webdriver_manager 版本: {webdriver_manager.__version__}")
    
    # 检查 ChromeDriver 缓存
    try:
        from webdriver_manager.core.driver_cache import DriverCache
        cache = DriverCache()
        cache_path = cache.get_cache_path()
        print(f"ChromeDriver 缓存路径: {cache_path}")
        
        # 查看缓存目录中的文件
        cache_dir = Path(cache_path)
        if cache_dir.exists():
            drivers = list(cache_dir.glob("**/*"))
            print(f"缓存中的驱动文件数量: {len(drivers)}")
            for driver in drivers[:5]:  # 只显示前5个
                print(f" - {driver}")
            if len(drivers) > 5:
                print(f" (还有 {len(drivers) - 5} 个文件未显示)")
            
            # 清理缓存
            clear_cache = input("是否清理 ChromeDriver 缓存? (y/n): ").strip().lower() or "n"
            if clear_cache == "y":
                print("正在清理 ChromeDriver 缓存...")
                # 备份缓存目录
                backup_dir = str(cache_dir) + "_backup"
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                shutil.copytree(str(cache_dir), backup_dir)
                print(f"已备份缓存目录到: {backup_dir}")
                
                # 清理缓存
                shutil.rmtree(str(cache_dir))
                os.makedirs(str(cache_dir))
                print("缓存目录已清理")
        else:
            print("缓存目录不存在")
    except Exception as e:
        print(f"检查缓存时出错: {e}")
    
    # 尝试安装最新的 ChromeDriver
    print_step("尝试下载最新版本的 ChromeDriver")
    
    try:
        # 清理 webdriver_manager 的已有导入
        for mod in list(sys.modules.keys()):
            if mod.startswith('webdriver_manager'):
                del sys.modules[mod]
        
        # 重新导入 webdriver_manager
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # 尝试各种安装方法
        print("方法1: 使用默认参数")
        try:
            path = ChromeDriverManager().install()
            print(f"成功下载 ChromeDriver: {path}")
        except Exception as e:
            print(f"方法1失败: {e}")
            
            print("\n方法2: 指定chrome_type参数")
            try:
                # 尝试导入 ChromeType
                try:
                    from webdriver_manager.core.utils import ChromeType
                except ImportError:
                    try:
                        from webdriver_manager.utils import ChromeType
                    except ImportError:
                        # 定义一个简单的 ChromeType 类
                        class ChromeType:
                            GOOGLE = "GOOGLE"
                
                path = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
                print(f"成功下载 ChromeDriver: {path}")
            except Exception as e:
                print(f"方法2失败: {e}")
    except Exception as e:
        print(f"下载 ChromeDriver 时出错: {e}")
    
    print_step("修复完成")
    print("""
为确保脚本正常运行，建议:
1. 使用 dytt8_simple.py 或 dytt8_scraper_v2.py 脚本，它们不依赖 webdriver_manager
2. 如果仍想使用原始脚本，请先更新 webdriver_manager:
   pip install webdriver-manager --upgrade

如果问题依然存在，可以尝试使用 Firefox 浏览器代替 Chrome。
""")


if __name__ == "__main__":
    main() 