#!/usr/bin/env python
"""
修复所有__init__.py文件中的空字节问题
"""
import os

def fix_init_files(root_dir):
    """修复所有__init__.py文件"""
    print(f"开始修复 {root_dir} 目录下的__init__.py文件...")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "__init__.py":
                filepath = os.path.join(dirpath, filename)
                print(f"修复文件: {filepath}")
                
                # 创建新的空__init__.py文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('"""Package initialization."""\n')
    
    print("修复完成!")

if __name__ == "__main__":
    fix_init_files("dytt8") 