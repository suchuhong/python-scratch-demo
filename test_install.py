#!/usr/bin/env python
"""
测试dytt8包安装
"""
import sys
import importlib

def test_installation():
    """测试包是否正确安装"""
    print("测试dytt8包安装...")
    
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
            print(f"尝试导入 {module_name}...")
            module = importlib.import_module(module_name)
            print(f"✓ 成功导入{module_name}模块")
        except Exception as e:
            print(f"✗ 导入{module_name}模块失败: {e}")
            print(f"  错误类型: {type(e).__name__}")
    
    print("\n测试完成!")
    return True

if __name__ == "__main__":
    test_installation() 