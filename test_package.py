#!/usr/bin/env python
"""
测试dytt8包结构
"""
import sys
import importlib
import pkgutil

def test_package_structure():
    """测试包结构是否正确"""
    print("测试dytt8包结构...")
    
    # 测试导入主包
    try:
        import dytt8
        print(f"✓ 成功导入dytt8包 (版本: {dytt8.__version__})")
    except ImportError as e:
        print(f"✗ 导入dytt8包失败: {e}")
        return False
    
    # 测试导入子模块
    modules_to_test = [
        "dytt8.core",
        "dytt8.gui",
        "dytt8.moviegui",
        "dytt8.utils",
        "dytt8.api",
        "dytt8.recommender",
        "dytt8.scheduler",
        "dytt8.scrapers",
        "dytt8.data"
    ]
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            print(f"✓ 成功导入{module_name}模块")
        except ImportError as e:
            print(f"✗ 导入{module_name}模块失败: {e}")
    
    # 测试导入核心类
    try:
        from dytt8.core import MovieScraper, MovieFinder
        print("✓ 成功导入核心类")
    except ImportError as e:
        print(f"✗ 导入核心类失败: {e}")
    
    # 列出所有子模块
    print("\n包含的子模块:")
    for _, name, is_pkg in pkgutil.iter_modules(dytt8.__path__, dytt8.__name__ + '.'):
        print(f"  - {name}" + (" (包)" if is_pkg else ""))
    
    print("\n测试完成!")
    return True

if __name__ == "__main__":
    test_package_structure() 