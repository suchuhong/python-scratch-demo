#!/usr/bin/env python
"""
API服务器
提供REST API接口供其他应用调用
"""
import os
import sys
import json
import threading
import logging
from datetime import datetime
import argparse
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "api_server.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('api_server')

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

# 全局变量
scheduled_jobs = {}  # 存储正在运行的任务
data_dir = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(data_dir, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    """API首页"""
    return jsonify({
        'name': '电影天堂工具集API',
        'version': '1.0',
        'endpoints': [
            {'path': '/movies', 'method': 'GET', 'description': '获取电影列表'},
            {'path': '/movies/search', 'method': 'GET', 'description': '搜索电影'},
            {'path': '/movies/download/<movie_id>', 'method': 'GET', 'description': '获取电影下载链接'},
            {'path': '/recommendations', 'method': 'GET', 'description': '获取电影推荐'},
            {'path': '/scrape', 'method': 'POST', 'description': '启动爬取任务'},
            {'path': '/tasks', 'method': 'GET', 'description': '获取所有任务'},
            {'path': '/tasks/<task_id>', 'method': 'GET', 'description': '获取任务详情'},
        ]
    })

@app.route('/movies', methods=['GET'])
def get_movies():
    """获取电影列表"""
    try:
        # 参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        sort_by = request.args.get('sort_by', 'year')
        sort_order = request.args.get('sort_order', 'desc')
        category = request.args.get('category', None)
        year = request.args.get('year', None)
        source = request.args.get('source', None)
        
        # 加载最新的电影数据
        movies = _load_movies()
        
        # 筛选
        if category:
            movies = [m for m in movies if category.lower() in m.get('category', '').lower()]
        
        if year:
            movies = [m for m in movies if year == m.get('year', '')]
        
        if source:
            movies = [m for m in movies if source.lower() in m.get('source', '').lower()]
        
        # 排序
        reverse = sort_order.lower() == 'desc'
        if sort_by in ['year', 'score', 'title']:
            # 对于分数，需要转换为数值
            if sort_by == 'score':
                def get_score(m):
                    score = m.get('score', '0')
                    try:
                        return float(score.split('/')[0])
                    except (ValueError, AttributeError, IndexError):
                        return 0
                
                movies.sort(key=get_score, reverse=reverse)
            else:
                movies.sort(key=lambda m: m.get(sort_by, ''), reverse=reverse)
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_movies = movies[start:end]
        
        return jsonify({
            'total': len(movies),
            'page': page,
            'page_size': page_size,
            'total_pages': (len(movies) + page_size - 1) // page_size,
            'movies': paginated_movies
        })
        
    except Exception as e:
        logger.error(f"获取电影列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/movies/search', methods=['GET'])
def search_movies():
    """搜索电影"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': '缺少搜索关键词'}), 400
        
        # 加载电影数据
        movies = _load_movies()
        
        # 搜索匹配
        results = []
        for movie in movies:
            # 在标题、导演、演员、简介中搜索
            searchable_fields = [
                movie.get('title', ''),
                movie.get('director', ''),
                movie.get('actors', ''),
                movie.get('summary', '')
            ]
            
            # 如果任何字段包含查询词，则匹配
            if any(query.lower() in field.lower() for field in searchable_fields if field):
                results.append(movie)
        
        return jsonify({
            'total': len(results),
            'query': query,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"搜索电影失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/movies/download/<movie_id>', methods=['GET'])
def get_download_link(movie_id):
    """获取电影下载链接"""
    try:
        # 加载电影数据
        movies = _load_movies()
        
        # 查找对应的电影
        movie = None
        for m in movies:
            if m.get('id', '') == movie_id:
                movie = m
                break
        
        if not movie:
            return jsonify({'error': '未找到指定电影'}), 404
        
        download_link = movie.get('download_link', '')
        
        if not download_link:
            return jsonify({'error': '该电影没有下载链接'}), 404
        
        return jsonify({
            'movie_id': movie_id,
            'title': movie.get('title', ''),
            'download_link': download_link
        })
        
    except Exception as e:
        logger.error(f"获取下载链接失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    """获取电影推荐"""
    try:
        # 参数
        count = int(request.args.get('count', 10))
        source = request.args.get('source', 'all')
        genres = request.args.get('genres', '').split(',') if request.args.get('genres') else []
        year_range = request.args.get('year_range', '不限')
        regions = request.args.get('regions', '').split(',') if request.args.get('regions') else []
        
        # 导入推荐系统
        from recommender import MovieRecommender
        
        # 初始化推荐系统
        recommender = MovieRecommender()
        
        # 设置用户偏好
        if genres or year_range != '不限' or regions:
            recommender.set_preferences(genres=genres, year_range=year_range, regions=regions)
        
        # 获取推荐
        recommendations = recommender.get_recommendations(count=count, source=source)
        
        return jsonify({
            'count': len(recommendations),
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/scrape', methods=['POST'])
def start_scrape():
    """启动爬取任务"""
    try:
        data = request.json
        
        # 必需的参数
        source = data.get('source', 'dytt8')
        
        # 可选参数
        pages = int(data.get('pages', 3))
        delay = float(data.get('delay', 2.0))
        category = data.get('category', '最新电影')
        save_format = data.get('format', 'csv')
        async_run = data.get('async', True)  # 是否异步运行
        
        # 启动爬取过程
        if async_run:
            # 异步运行
            job_id = f"scrape_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            def run_scraper():
                try:
                    result = _execute_scrape(source, pages, delay, category, save_format)
                    scheduled_jobs[job_id] = {'status': 'completed', 'result': result}
                except Exception as e:
                    scheduled_jobs[job_id] = {'status': 'failed', 'error': str(e)}
            
            # 创建并启动线程
            thread = threading.Thread(target=run_scraper)
            thread.daemon = True
            thread.start()
            
            # 记录任务
            scheduled_jobs[job_id] = {'status': 'running'}
            
            return jsonify({
                'job_id': job_id,
                'status': 'running',
                'message': '爬取任务已启动'
            })
            
        else:
            # 同步运行
            result = _execute_scrape(source, pages, delay, category, save_format)
            
            return jsonify({
                'status': 'completed',
                'result': result
            })
            
    except Exception as e:
        logger.error(f"启动爬取任务失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """获取所有任务"""
    try:
        # 导入任务调度器
        from scheduler import TaskScheduler
        
        # 初始化调度器
        scheduler = TaskScheduler()
        
        # 获取所有任务
        tasks = scheduler.get_all_tasks()
        
        return jsonify({
            'count': len(tasks),
            'tasks': tasks
        })
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详情"""
    try:
        # 导入任务调度器
        from scheduler import TaskScheduler
        
        # 初始化调度器
        scheduler = TaskScheduler()
        
        # 获取任务
        task = scheduler.get_task(task_id)
        
        if not task:
            return jsonify({'error': '未找到指定任务'}), 404
        
        return jsonify(task)
        
    except Exception as e:
        logger.error(f"获取任务详情失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """获取异步任务状态"""
    if job_id not in scheduled_jobs:
        return jsonify({'error': '未找到指定任务'}), 404
    
    return jsonify(scheduled_jobs[job_id])

def _load_movies():
    """加载电影数据"""
    try:
        # 查找最新的电影数据文件
        data_file = os.path.join(data_dir, "movies_cache.json")
        
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 如果没有缓存文件，查找CSV文件
        csv_files = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith('.csv') and ('movies' in f or 'dytt' in f)]
        
        if not csv_files:
            return []
        
        # 按修改时间排序，取最新的文件
        latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(os.path.dirname(__file__), f)))
        latest_file_path = os.path.join(os.path.dirname(__file__), latest_file)
        
        # 读取CSV文件
        df = pd.read_csv(latest_file_path)
        movies = df.to_dict('records')
        
        # 为每部电影添加ID
        for i, movie in enumerate(movies):
            movie['id'] = f"movie_{i}"
        
        # 保存到缓存
        os.makedirs(data_dir, exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        return movies
        
    except Exception as e:
        logger.error(f"加载电影数据失败: {e}")
        return []

def _execute_scrape(source, pages, delay, category, save_format):
    """执行爬取过程"""
    try:
        if source == 'dytt8':
            # 导入爬虫
            from scrapers.dytt8_scraper import Dytt8Scraper
            
            # 初始化爬虫
            scraper = Dytt8Scraper(pages=pages, delay=delay, category=category, headless=True)
            
        elif source == 'douban':
            # 导入爬虫
            from scrapers.douban_scraper import DoubanScraper
            
            # 初始化爬虫
            scraper = DoubanScraper(pages=pages, delay=delay, category=category, headless=True)
            
        else:
            raise ValueError(f"不支持的数据源: {source}")
        
        # 执行爬取
        scraper.scrape()
        
        # 保存结果
        output_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(output_dir, exist_ok=True)
        
        saved_file = scraper.save_results(format=save_format, output_dir=output_dir)
        
        # 更新缓存
        movies = scraper.get_results()
        
        if movies:
            # 为每部电影添加ID
            for i, movie in enumerate(movies):
                movie['id'] = f"movie_{i}"
            
            # 保存到缓存
            cache_file = os.path.join(data_dir, "movies_cache.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(movies, f, ensure_ascii=False, indent=2)
        
        return {
            'source': source,
            'count': len(movies),
            'file': saved_file
        }
        
    except Exception as e:
        logger.error(f"执行爬取过程失败: {e}")
        raise

def start_server(port=8000, debug=False):
    """启动API服务器"""
    logger.info(f"启动API服务器于端口 {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='电影天堂工具集API服务器')
    parser.add_argument('-p', '--port', type=int, default=8000, help='监听端口')
    parser.add_argument('-d', '--debug', action='store_true', help='调试模式')
    
    args = parser.parse_args()
    
    start_server(port=args.port, debug=args.debug) 