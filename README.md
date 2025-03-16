# 电影天堂工具集 (DYTT8)

一个功能强大的电影资源爬取与管理工具，基于Python和Selenium开发。

[中文文档](README_zh.md) | [English](README.md)

**文档:**
- [高级使用指南 (中文)](advanced_guide_zh.md) - 复杂场景解决方案

## 功能特点

- 🔍 **电影资源爬取**: 自动从电影天堂网站抓取最新电影资源
- 🔎 **电影搜索**: 快速搜索已抓取的电影资源
- 👍 **电影推荐**: 基于用户喜好推荐相似电影
- ⏰ **定时任务**: 设置定时任务自动抓取最新资源
- 🖥️ **图形界面**: 提供直观的用户界面，易于操作
- 🌐 **API服务**: 提供RESTful API接口，方便集成到其他应用

## 安装

### 方法1: 使用pip安装

```bash
pip install dytt8
```

### 方法2: 从源码安装

```bash
git clone https://github.com/yourusername/dytt8.git
cd dytt8
pip install -e .
```

## 使用方法

### 命令行界面

```bash
# 启动命令行界面
dytt8
```

### 图形用户界面

```bash
# 启动图形用户界面
dytt8-gui
```

### 全功能版本

```bash
# 启动全功能版本（包含GUI、API服务器和任务调度器）
dytt8-full

# 启动API服务器
dytt8-full --api --port 8000

# 启动任务调度器
dytt8-full --scheduler

# 启动图形界面
dytt8-full --gui
```

## 项目结构

```
dytt8/
├── api/            # API服务器模块
├── core/           # 核心功能模块
├── data/           # 数据存储模块
├── gui/            # 图形界面模块
├── moviegui/       # 电影管理GUI模块
├── recommender/    # 电影推荐模块
├── scheduler/      # 任务调度模块
├── scrapers/       # 爬虫模块
├── utils/          # 工具函数模块
├── __init__.py     # 包初始化文件
├── __main__.py     # 命令行入口点
├── main.py         # 基础功能入口
└── main_full.py    # 全功能入口点
```

## 依赖项

- Python 3.6+
- Selenium 4.0.0+
- webdriver-manager 3.8.0+
- pandas 1.0.0+
- requests 2.25.0+
- beautifulsoup4 4.9.0+
- lxml 4.6.0+
- tqdm 4.50.0+

## API参考

### 核心API

```python
# 导入核心类
from dytt8.core import MovieScraper, MovieFinder, MovieScraperV2, SimpleMovieScraper

# 爬取电影信息
scraper = MovieScraper(headless=True)
scraper.open_website()
movies = scraper.scrape_latest_movies(max_pages=3)

# 保存结果为CSV
scraper.save_to_csv(movies, "movies.csv")

# 搜索电影
finder = MovieFinder()
results = finder.search_movie("复仇者联盟")
for movie in results:
    print(f"片名: {movie['title']}")
    print(f"下载链接: {movie['download_url']}")
```

### 高级API

```python
# 使用兼容性更好的V2版本
from dytt8.core import MovieScraperV2

scraper = MovieScraperV2(headless=True)
scraper.scrape_recent_movies(days=7)  # 爬取最近7天的电影
scraper.export_to_csv()  # 导出结果
```

### GUI应用

```python
# 启动图形界面
from dytt8.gui.app import main
main()
```

### 完整Web应用

```python
# 启动API服务器
from dytt8.api.server import start_server
start_server(port=8000)
```

## 开发指南

### 环境设置

1. 克隆仓库:
   ```bash
   git clone https://github.com/yourusername/dytt8.git
   cd dytt8
   ```

2. 创建虚拟环境:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. 安装开发依赖:
   ```bash
   pip install -e ".[dev]"
   ```

### 目录结构详解

```
dytt8/
├── api/            # API服务器模块
│   ├── server.py   # Flask服务器
│   ├── routes.py   # API路由
│   └── templates/  # HTML模板
├── core/           # 核心功能模块
│   ├── dytt8_scraper.py     # 基础爬虫
│   ├── dytt8_movie_finder.py # 电影搜索器
│   ├── dytt8_scraper_v2.py  # 兼容版爬虫
│   └── dytt8_simple.py      # 简化版爬虫
├── data/           # 数据存储模块
│   └── output/     # 输出数据存储目录
├── gui/            # 图形界面模块
│   ├── app.py      # 主应用
│   ├── gui.py      # GUI组件
│   └── tabs/       # 选项卡实现
├── moviegui/       # 电影管理GUI模块
│   ├── app.py      # 电影管理应用
│   └── launcher.py # 启动器
├── recommender/    # 电影推荐模块
│   └── recommender.py # 推荐引擎
├── scheduler/      # 任务调度模块
│   └── scheduler.py  # 定时任务
├── scrapers/       # 爬虫模块
│   ├── base_scraper.py   # 基础爬虫类
│   └── dytt8_scraper.py  # DYTT8网站爬虫
├── utils/          # 工具函数模块
│   ├── utils.py          # 工具函数
│   └── webdriver_utils.py # WebDriver工具
├── __init__.py     # 包初始化文件
├── __main__.py     # 命令行入口点
├── main.py         # 基础功能入口
└── main_full.py    # 全功能入口点
```

### 扩展指南

#### 添加新的爬虫

1. 在`scrapers`目录下创建新的爬虫文件，如`new_site_scraper.py`
2. 继承`base_scraper.py`中的基础类
3. 实现特定网站的抓取逻辑
4. 在`__init__.py`中导出新类

#### 添加新的GUI功能

1. 在`gui/tabs`目录下创建新的选项卡文件
2. 将选项卡添加到`gui/app.py`中的主应用
3. 实现必要的回调和事件处理

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

- 感谢所有开源项目的贡献者
- 特别感谢Selenium项目提供的强大功能 