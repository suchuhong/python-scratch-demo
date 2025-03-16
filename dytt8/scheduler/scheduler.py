#!/usr/bin/env python
"""
定时任务管理器
实现自动抓取和更新推荐
"""
import os
import sys
import time
import json
import threading
import schedule
from datetime import datetime, timedelta
import subprocess
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "scheduler.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('movie_scheduler')

class TaskScheduler:
    """定时任务管理器"""
    
    def __init__(self):
        """初始化任务管理器"""
        self.tasks = []
        self.config_file = os.path.join(os.path.dirname(__file__), "data", "scheduler.json")
        self.stop_event = threading.Event()
        self.thread = None
        
        # 创建数据目录
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 加载任务配置
        self._load_tasks()
    
    def _load_tasks(self):
        """加载任务配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                logger.info(f"已加载 {len(self.tasks)} 个定时任务")
            except Exception as e:
                logger.error(f"加载任务配置失败: {e}")
                self.tasks = []
    
    def _save_tasks(self):
        """保存任务配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            logger.info("已保存任务配置")
        except Exception as e:
            logger.error(f"保存任务配置失败: {e}")
    
    def add_task(self, task_type, schedule_type, time_params, task_params=None, active=True):
        """
        添加定时任务
        
        参数:
            task_type (str): 任务类型 ('scrape' 或 'recommend')
            schedule_type (str): 调度类型 ('hourly', 'daily', 'weekly', 'monthly')
            time_params (dict): 时间参数，因调度类型而异
            task_params (dict): 任务参数
            active (bool): 是否激活任务
        
        返回:
            str: 任务ID
        """
        # 生成任务ID
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建任务记录
        task = {
            'id': task_id,
            'type': task_type,
            'schedule_type': schedule_type,
            'time_params': time_params,
            'task_params': task_params or {},
            'active': active,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_run': None,
            'next_run': self._calculate_next_run(schedule_type, time_params)
        }
        
        # 添加到任务列表
        self.tasks.append(task)
        
        # 保存配置
        self._save_tasks()
        
        # 如果任务是激活状态，立即安排它
        if active and self.thread and self.thread.is_alive():
            self._schedule_task(task)
        
        logger.info(f"已添加任务: {task_id} ({task_type})")
        return task_id
    
    def update_task(self, task_id, **kwargs):
        """
        更新任务
        
        参数:
            task_id (str): 任务ID
            **kwargs: 要更新的字段
        
        返回:
            bool: 是否成功
        """
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                # 更新字段
                for key, value in kwargs.items():
                    if key in task:
                        task[key] = value
                
                # 如果更新了时间参数，重新计算下次运行时间
                if 'time_params' in kwargs or 'schedule_type' in kwargs:
                    schedule_type = kwargs.get('schedule_type', task['schedule_type'])
                    time_params = kwargs.get('time_params', task['time_params'])
                    task['next_run'] = self._calculate_next_run(schedule_type, time_params)
                
                # 保存配置
                self._save_tasks()
                
                # 如果调度器正在运行，更新调度
                if self.thread and self.thread.is_alive():
                    # 清除现有任务
                    schedule.clear()
                    # 重新安排所有任务
                    self._schedule_all_tasks()
                
                logger.info(f"已更新任务: {task_id}")
                return True
        
        logger.warning(f"未找到任务: {task_id}")
        return False
    
    def delete_task(self, task_id):
        """
        删除任务
        
        参数:
            task_id (str): 任务ID
        
        返回:
            bool: 是否成功
        """
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                # 删除任务
                del self.tasks[i]
                
                # 保存配置
                self._save_tasks()
                
                # 如果调度器正在运行，更新调度
                if self.thread and self.thread.is_alive():
                    # 清除现有任务
                    schedule.clear()
                    # 重新安排所有任务
                    self._schedule_all_tasks()
                
                logger.info(f"已删除任务: {task_id}")
                return True
        
        logger.warning(f"未找到任务: {task_id}")
        return False
    
    def activate_task(self, task_id):
        """激活任务"""
        return self.update_task(task_id, active=True)
    
    def deactivate_task(self, task_id):
        """停用任务"""
        return self.update_task(task_id, active=False)
    
    def get_all_tasks(self):
        """获取所有任务"""
        return self.tasks
    
    def get_task(self, task_id):
        """获取指定任务"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def _calculate_next_run(self, schedule_type, time_params):
        """
        计算下次运行时间
        
        参数:
            schedule_type (str): 调度类型
            time_params (dict): 时间参数
        
        返回:
            str: 下次运行时间的字符串表示
        """
        now = datetime.now()
        next_run = None
        
        if schedule_type == 'hourly':
            # 时间参数: {'minute': 30}
            minute = int(time_params.get('minute', 0))
            
            next_run = now.replace(minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(hours=1)
        
        elif schedule_type == 'daily':
            # 时间参数: {'hour': 3, 'minute': 30}
            hour = int(time_params.get('hour', 0))
            minute = int(time_params.get('minute', 0))
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule_type == 'weekly':
            # 时间参数: {'weekday': 0, 'hour': 3, 'minute': 30}
            # weekday: 0=星期一, 6=星期日
            weekday = int(time_params.get('weekday', 0))
            hour = int(time_params.get('hour', 0))
            minute = int(time_params.get('minute', 0))
            
            # 计算从当前到下个指定星期几的天数
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:  # 如果今天已经是指定的星期几或之后，则等到下周
                days_ahead += 7
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
        
        elif schedule_type == 'monthly':
            # 时间参数: {'day': 1, 'hour': 3, 'minute': 30}
            day = int(time_params.get('day', 1))
            hour = int(time_params.get('hour', 0))
            minute = int(time_params.get('minute', 0))
            
            # 计算下个月的指定日期
            if day < now.day or (day == now.day and now.hour > hour) or (day == now.day and now.hour == hour and now.minute >= minute):
                # 如果今天已经是或超过指定日期，则等到下个月
                if now.month == 12:
                    next_run = now.replace(year=now.year+1, month=1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month+1, day=day, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # 否则就在本月的指定日期
                next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
        
        return next_run.strftime('%Y-%m-%d %H:%M:%S') if next_run else None
    
    def _execute_task(self, task):
        """
        执行任务
        
        参数:
            task (dict): 任务信息
        """
        task_id = task['id']
        task_type = task['type']
        task_params = task['task_params']
        
        logger.info(f"开始执行任务: {task_id} ({task_type})")
        
        try:
            if task_type == 'scrape':
                # 执行爬取任务
                self._execute_scrape_task(task_params)
            elif task_type == 'recommend':
                # 执行推荐更新任务
                self._execute_recommend_task(task_params)
            else:
                logger.warning(f"未知任务类型: {task_type}")
                return
            
            # 更新任务状态
            task['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task['next_run'] = self._calculate_next_run(task['schedule_type'], task['time_params'])
            self._save_tasks()
            
            logger.info(f"任务 {task_id} 执行完成")
            
        except Exception as e:
            logger.error(f"任务 {task_id} 执行失败: {e}")
    
    def _execute_scrape_task(self, params):
        """
        执行爬取任务
        
        参数:
            params (dict): 任务参数
        """
        # 从参数中获取爬取配置
        version = params.get('version', 'v2')
        pages = params.get('pages', 3)
        delay = params.get('delay', 2.0)
        category = params.get('category', '最新电影')
        save_format = params.get('format', 'csv')
        save_path = params.get('output', os.getcwd())
        
        # 映射版本到脚本名
        script_map = {
            'v1': 'dytt8_scraper.py',
            'v2': 'dytt8_scraper_v2.py',
            'simple': 'dytt8_simple.py'
        }
        
        script_name = script_map.get(version, 'dytt8_scraper_v2.py')
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        # 构建命令
        cmd = [
            sys.executable,
            script_path,
            '--pages', str(pages),
            '--delay', str(delay),
            '--category', category,
            '--format', save_format,
            '--output', save_path,
            '--headless'  # 确保无头模式运行
        ]
        
        # 执行命令
        logger.info(f"执行命令: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"爬取任务输出: {result.stdout}")
            if result.stderr:
                logger.warning(f"爬取任务错误: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"爬取任务失败: {e}")
            if e.stdout:
                logger.info(f"输出: {e.stdout}")
            if e.stderr:
                logger.error(f"错误: {e.stderr}")
            raise
    
    def _execute_recommend_task(self, params):
        """
        执行推荐更新任务
        
        参数:
            params (dict): 任务参数
        """
        # 从参数中获取推荐配置
        count = params.get('count', 10)
        source = params.get('source', 'all')
        
        # 导入推荐系统
        try:
            from recommender import MovieRecommender
            
            # 初始化推荐系统
            recommender = MovieRecommender()
            
            # 获取推荐
            recommendations = recommender.get_recommendations(count=count, source=source)
            
            # 保存推荐结果
            if recommendations:
                output_dir = os.path.join(os.path.dirname(__file__), "data")
                os.makedirs(output_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(output_dir, f"recommendations_{timestamp}.json")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(recommendations, f, ensure_ascii=False, indent=2)
                
                logger.info(f"已保存 {len(recommendations)} 条推荐结果到 {output_file}")
            else:
                logger.warning("未生成推荐结果")
            
        except ImportError:
            logger.error("导入推荐系统失败")
            raise
        except Exception as e:
            logger.error(f"生成推荐失败: {e}")
            raise
    
    def _schedule_task(self, task):
        """
        安排任务
        
        参数:
            task (dict): 任务信息
        """
        if not task['active']:
            return
        
        task_id = task['id']
        schedule_type = task['schedule_type']
        time_params = task['time_params']
        
        # 根据不同的调度类型设置任务
        if schedule_type == 'hourly':
            minute = int(time_params.get('minute', 0))
            schedule.every().hour.at(f":{minute:02d}").do(self._execute_task, task)
            logger.info(f"任务 {task_id} 已安排为每小时 {minute:02d} 分执行")
            
        elif schedule_type == 'daily':
            hour = int(time_params.get('hour', 0))
            minute = int(time_params.get('minute', 0))
            schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self._execute_task, task)
            logger.info(f"任务 {task_id} 已安排为每天 {hour:02d}:{minute:02d} 执行")
            
        elif schedule_type == 'weekly':
            weekday = int(time_params.get('weekday', 0))
            hour = int(time_params.get('hour', 0))
            minute = int(time_params.get('minute', 0))
            
            # 映射星期几
            weekday_map = {
                0: schedule.every().monday,
                1: schedule.every().tuesday,
                2: schedule.every().wednesday,
                3: schedule.every().thursday,
                4: schedule.every().friday,
                5: schedule.every().saturday,
                6: schedule.every().sunday
            }
            
            weekday_name = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][weekday]
            
            if weekday in weekday_map:
                weekday_map[weekday].at(f"{hour:02d}:{minute:02d}").do(self._execute_task, task)
                logger.info(f"任务 {task_id} 已安排为每周{weekday_name} {hour:02d}:{minute:02d} 执行")
                
        elif schedule_type == 'monthly':
            day = int(time_params.get('day', 1))
            hour = int(time_params.get('hour', 0))
            minute = int(time_params.get('minute', 0))
            
            # schedule库不直接支持每月调度，我们使用自定义的检查方法
            def monthly_job():
                now = datetime.now()
                if now.day == day:
                    # 今天是目标日期，检查时间
                    target_time = now.replace(hour=hour, minute=minute, second=0)
                    if now.timestamp() >= target_time.timestamp() and now.timestamp() < target_time.timestamp() + 60:
                        # 现在是目标时间的一分钟内，执行任务
                        self._execute_task(task)
            
            # 每小时检查一次
            schedule.every().hour.do(monthly_job)
            logger.info(f"任务 {task_id} 已安排为每月 {day} 日 {hour:02d}:{minute:02d} 执行")
    
    def _schedule_all_tasks(self):
        """安排所有活动任务"""
        for task in self.tasks:
            if task['active']:
                self._schedule_task(task)
    
    def start(self):
        """启动任务调度器"""
        if self.thread and self.thread.is_alive():
            logger.warning("任务调度器已在运行")
            return
        
        # 重置停止标志
        self.stop_event.clear()
        
        # 清除所有已安排的任务
        schedule.clear()
        
        # 安排所有活动任务
        self._schedule_all_tasks()
        
        # 创建并启动调度线程
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True  # 设置为守护线程，主线程退出时将终止
        self.thread.start()
        
        logger.info("任务调度器已启动")
    
    def stop(self):
        """停止任务调度器"""
        if not self.thread or not self.thread.is_alive():
            logger.warning("任务调度器未在运行")
            return
        
        # 设置停止标志
        self.stop_event.set()
        
        # 等待线程结束
        self.thread.join(timeout=5)
        self.thread = None
        
        # 清除所有已安排的任务
        schedule.clear()
        
        logger.info("任务调度器已停止")
    
    def _run_scheduler(self):
        """运行调度器（在单独的线程中执行）"""
        logger.info("调度器线程已启动")
        
        while not self.stop_event.is_set():
            # 运行所有待执行的任务
            schedule.run_pending()
            
            # 更新任务的下次运行时间
            now = datetime.now()
            for task in self.tasks:
                if task['active'] and task['next_run']:
                    next_run = datetime.strptime(task['next_run'], '%Y-%m-%d %H:%M:%S')
                    if next_run < now:
                        # 计算新的下次运行时间
                        task['next_run'] = self._calculate_next_run(task['schedule_type'], task['time_params'])
            
            # 保存更新后的任务
            self._save_tasks()
            
            # 休息一段时间，避免CPU过载
            time.sleep(30)
        
        logger.info("调度器线程已停止") 