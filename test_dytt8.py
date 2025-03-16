#!/usr/bin/env python
"""
电影天堂工具集基本测试
"""
import unittest
import importlib

class TestDytt8(unittest.TestCase):
    """电影天堂工具集测试类"""
    
    def test_package_import(self):
        """测试包导入"""
        import dytt8
        self.assertEqual(dytt8.__version__, "1.0.0")
    
    def test_core_modules_import(self):
        """测试核心模块导入"""
        from dytt8.core import MovieScraper, MovieFinder, MovieScraperV2, SimpleMovieScraper
        self.assertTrue(hasattr(MovieScraper, '__init__'))
        self.assertTrue(hasattr(MovieFinder, '__init__'))
        self.assertTrue(hasattr(MovieScraperV2, '__init__'))
        self.assertTrue(hasattr(SimpleMovieScraper, '__init__'))
    
    def test_submodules_import(self):
        """测试子模块导入"""
        submodules = [
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
        
        for module_name in submodules:
            try:
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)
            except ImportError as e:
                self.fail(f"无法导入模块 {module_name}: {e}")

if __name__ == "__main__":
    unittest.main() 