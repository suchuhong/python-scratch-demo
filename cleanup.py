#!/usr/bin/env python
"""
清理临时文件和构建产物
"""
import os
import shutil

def clean_build_artifacts():
    """清理构建产物"""
    paths_to_remove = [
        "build",
        "dist",
        "*.egg-info",
        "__pycache__",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
    ]
    
    for path in paths_to_remove:
        if "*" in path:
            # 处理通配符
            import glob
            for item in glob.glob(path, recursive=True):
                try:
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                        print(f"已删除目录: {item}")
                    else:
                        os.remove(item)
                        print(f"已删除文件: {item}")
                except Exception as e:
                    print(f"无法删除 {item}: {e}")
        else:
            # 处理具体路径
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        print(f"已删除目录: {path}")
                    else:
                        os.remove(path)
                        print(f"已删除文件: {path}")
                except Exception as e:
                    print(f"无法删除 {path}: {e}")

def clean_temp_files():
    """清理临时文件"""
    temp_files = [
        "dytt8_init.py",
        "dytt8_core_init.py",
        "core_init.py",
        "*.log",
        "*.tmp",
        "*.bak",
    ]
    
    for file_pattern in temp_files:
        if "*" in file_pattern:
            import glob
            for file in glob.glob(file_pattern):
                try:
                    os.remove(file)
                    print(f"已删除临时文件: {file}")
                except Exception as e:
                    print(f"无法删除 {file}: {e}")
        elif os.path.exists(file_pattern):
            try:
                os.remove(file_pattern)
                print(f"已删除临时文件: {file_pattern}")
            except Exception as e:
                print(f"无法删除 {file_pattern}: {e}")

def main():
    """主函数"""
    print("开始清理构建产物和临时文件...")
    clean_build_artifacts()
    clean_temp_files()
    print("清理完成!")

if __name__ == "__main__":
    main() 