# 电影天堂工具集快速入门指南

本文档提供了使用电影天堂工具集的快速指南，帮助您迅速上手并使用该工具包。

## 安装

### 方法1: 使用pip安装（建议）

```bash
pip install dytt8
```

### 方法2: 从源码安装

```bash
git clone https://github.com/yourusername/dytt8.git
cd dytt8
pip install -e .
```

## 快速入门

### 基础爬虫 - 抓取最新电影

```python
from dytt8.core import MovieScraper

# 创建爬虫实例（默认为无头模式）
scraper = MovieScraper(headless=True)

# 打开电影天堂网站
scraper.open_website()

# 爬取最新电影（默认爬取第一页）
movies = scraper.scrape_latest_movies()

# 保存结果到CSV文件
scraper.save_to_csv(movies, "latest_movies.csv")

# 打印爬取结果
for movie in movies[:5]:  # 只显示前5部电影
    print(f"片名: {movie['title']}")
    print(f"类型: {movie['category']}")
    print(f"评分: {movie['rating']}")
    print(f"下载: {movie['download_url']}")
    print("-" * 30)
```

### 电影搜索 - 查找特定电影

```python
from dytt8.core import MovieFinder

# 创建搜索器实例
finder = MovieFinder()

# 搜索电影
search_term = "蜘蛛侠"
results = finder.search_movie(search_term)

# 打印搜索结果
print(f"找到 {len(results)} 部与 '{search_term}' 相关的电影:")
for idx, movie in enumerate(results, 1):
    print(f"{idx}. {movie['title']}")
    print(f"   导演: {movie['director']}")
    print(f"   主演: {movie['actors']}")
    print(f"   下载: {movie['download_url']}")
    print()
```

### 使用兼容版爬虫 (V2)

如果您在使用基础爬虫时遇到问题，可以尝试使用兼容性更好的V2版本：

```python
from dytt8.core import MovieScraperV2

# 创建V2爬虫实例
scraper = MovieScraperV2(headless=True)

# 爬取最近一周的电影
scraper.scrape_recent_movies(days=7)

# 导出结果到CSV文件
scraper.export_to_csv(filename="recent_movies.csv")
```

### 使用简化版爬虫

如果您想使用更简单的接口，可以尝试使用简化版爬虫：

```python
from dytt8.core import SimpleMovieScraper

# 创建简化版爬虫实例
scraper = SimpleMovieScraper()

# 获取热门电影
hot_movies = scraper.get_hot_movies()

# 打印结果
for movie in hot_movies:
    print(f"{movie['title']} - {movie['download_url']}")
```

## 图形界面

电影天堂工具集提供了图形界面，方便非技术用户使用：

```bash
# 启动图形界面
dytt8-gui
```

## API服务器

您也可以启动API服务器，提供RESTful API接口：

```bash
# 启动API服务器
dytt8-full --api --port 8000
```

启动后，可以通过以下URL访问API：

- `http://localhost:8000/api/movies` - 获取所有电影列表
- `http://localhost:8000/api/movies/{id}` - 获取指定ID的电影详情
- `http://localhost:8000/api/movies/search?q=关键词` - 搜索电影
- `http://localhost:8000/api/scrape` - 触发电影抓取任务

## 常见问题

### Q: 运行时遇到ChromeDriver错误怎么办？

A: 您可以使用内置的修复工具：

```python
from dytt8.utils.fix_webdriver_manager import fix_chrome_driver
fix_chrome_driver()
```

或者使用命令行：

```bash
dytt8 --fix-chromedriver
```

### Q: 如何设置代理？

A: 您可以在创建爬虫实例时设置代理：

```python
scraper = MovieScraper(proxy="http://your-proxy-server:port")
```

### Q: 如何定期自动抓取电影？

A: 您可以使用调度器：

```python
from dytt8.scheduler.task_manager import TaskScheduler

scheduler = TaskScheduler()
scheduler.add_job('every_day_at_10', '0 10 * * *', 'scrape_latest_movies')
scheduler.start()
```

或者使用命令行：

```bash
dytt8-full --scheduler
```

## 更多文档

更多详细信息，请参阅[完整文档](https://github.com/yourusername/dytt8/blob/main/README.md)或[高级使用指南](https://github.com/yourusername/dytt8/blob/main/advanced_guide_zh.md)。 