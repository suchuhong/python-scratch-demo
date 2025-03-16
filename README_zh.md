# Python + Selenium 网页自动化

本项目演示如何使用 Python 和 Selenium 进行网页自动化任务。

**相关文档:**
- [高级用法指南](advanced_guide_zh.md) - 包含更复杂场景的解决方案
- [English README](README.md) - English version

## 环境配置

1. 安装 Python 3.8 或更高版本
2. 安装依赖项：
   ```
   pip install -r requirements.txt
   ```
3. WebDriver 设置：
   - Chrome 浏览器：项目使用 webdriver-manager 自动下载和管理适当版本的 ChromeDriver
   - 其他浏览器：您需要下载相应的驱动程序并相应地更新脚本

## 项目结构

- `main.py`：Selenium 自动化的基本示例
- `utils.py`：常见 Selenium 操作的辅助函数
- `examples/`：不同用例的其他示例脚本

## 使用方法

运行基本示例：
```
python main.py
```

## 常见任务

以下示例展示如何使用 Selenium 执行常见任务：

### 导航到 URL
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.example.com")
```

### 查找元素
```python
# 通过 ID 查找
element = driver.find_element(By.ID, "search")

# 通过 CSS 选择器查找
element = driver.find_element(By.CSS_SELECTOR, "button.submit")

# 通过 XPath 查找
element = driver.find_element(By.XPATH, "//button[@type='submit']")
```

### 与元素交互
```python
# 点击按钮
button = driver.find_element(By.ID, "submit-button")
button.click()

# 输入文本
input_field = driver.find_element(By.NAME, "username")
input_field.send_keys("my_username")

# 清除输入字段
input_field.clear()
```

### 等待元素加载
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 等待元素可点击（显式等待）
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "submit-button"))
)
element.click()
```

## 高级示例

项目包含两个高级示例：

### 网页抓取器 (web_scraper.py)

这个示例演示如何从演示电子商务网站抓取产品信息，包括：
- 抓取多个页面的数据
- 提取产品名称、价格和描述
- 将数据保存到 CSV 文件

运行方式：
```
python examples/web_scraper.py
```

### 动态内容处理 (dynamic_content.py)

这个示例演示如何处理通过 JavaScript 加载的动态内容，包括：
- 处理无限滚动页面
- 等待 AJAX 请求完成
- 与模态对话框交互

运行方式：
```
python examples/dynamic_content.py
```

## 实用技巧

1. **无头模式运行**：无需打开浏览器界面，提高速度
   ```python
   driver = setup_chrome_driver(headless=True)
   ```

2. **禁用图像加载**：加快页面加载速度
   ```python
   driver = setup_chrome_driver(disable_images=True)
   ```

3. **安全点击元素**：处理常见点击错误并自动重试
   ```python
   from utils import safe_click
   safe_click(driver, element, retries=3)
   ```

4. **截图**：用于调试或记录
   ```python
   from utils import take_screenshot
   take_screenshot(driver, "debug_screenshot")
   ```

5. **始终关闭浏览器**：使用 try/finally 确保资源释放
   ```python
   try:
       # 自动化代码
   finally:
       driver.quit()
   ``` 