#!/usr/bin/env python
"""
初始化所有模块的__init__.py文件
"""
import os

module_docstrings = {
    "api": "电影天堂工具集 - API模块\n提供RESTful API接口服务",
    "utils": "电影天堂工具集 - 工具模块\n提供通用工具函数",
    "gui": "电影天堂工具集 - GUI模块\n提供图形用户界面",
    "moviegui": "电影天堂工具集 - 电影GUI模块\n提供电影管理界面",
    "recommender": "电影天堂工具集 - 推荐模块\n提供电影推荐功能",
    "scheduler": "电影天堂工具集 - 调度模块\n提供定时任务功能",
    "scrapers": "电影天堂工具集 - 爬虫模块\n提供各种网站爬虫实现",
    "data": "电影天堂工具集 - 数据模块\n提供数据存储和处理功能"
}

def init_module(module_path, docstring):
    """初始化模块的__init__.py文件"""
    init_file = os.path.join(module_path, "__init__.py")
    content = f'"""\n{docstring}\n"""\n\n'
    
    # 写入文件
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已更新: {init_file}")

def main():
    """主函数"""
    print("开始初始化模块__init__.py文件...")
    
    for module_name, docstring in module_docstrings.items():
        module_path = os.path.join("dytt8", module_name)
        if os.path.isdir(module_path):
            init_module(module_path, docstring)
        else:
            print(f"目录不存在: {module_path}")
    
    print("初始化完成!")

if __name__ == "__main__":
    main() 