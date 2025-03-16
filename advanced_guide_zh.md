# Selenium 高级用法指南

本文档提供了 Selenium 与 Python 结合使用的高级技巧，帮助您解决日常自动化测试和网络抓取中遇到的复杂场景。

## 目录

1. [处理各种弹窗](#处理各种弹窗)
2. [文件上传和下载](#文件上传和下载)
3. [处理多窗口和标签页](#处理多窗口和标签页)
4. [执行 JavaScript](#执行-javascript)
5. [高级浏览器选项配置](#高级浏览器选项配置)
6. [处理 Shadow DOM](#处理-shadow-dom)
7. [性能优化技巧](#性能优化技巧)
8. [常见问题排查](#常见问题排查)

## 处理各种弹窗

### 处理警告框 (Alert)

```python
from selenium.webdriver.common.alert import Alert

# 等待警告框出现
WebDriverWait(driver, 10).until(EC.alert_is_present())

# 获取警告框
alert = Alert(driver)

# 获取警告框文本
alert_text = alert.text
print(f"警告框文本: {alert_text}")

# 接受警告框 (点击 "确定")
alert.accept()

# 或者取消警告框 (点击 "取消")
# alert.dismiss()

# 在提示框中输入文本
# alert.send_keys("输入的文本")
```

### 处理确认框 (Confirm)

```python
# 触发确认框的按钮
button = driver.find_element(By.ID, "confirm-button")
button.click()

# 等待确认框出现
WebDriverWait(driver, 10).until(EC.alert_is_present())
confirm = driver.switch_to.alert

# 接受确认框 (点击 "确定")
confirm.accept()

# 或者取消确认框 (点击 "取消")
# confirm.dismiss()
```

### 处理提示框 (Prompt)

```python
# 触发提示框的按钮
button = driver.find_element(By.ID, "prompt-button")
button.click()

# 等待提示框出现
WebDriverWait(driver, 10).until(EC.alert_is_present())
prompt = driver.switch_to.alert

# 在提示框中输入文本
prompt.send_keys("输入的文本")

# 接受提示框
prompt.accept()
```

## 文件上传和下载

### 上传文件

```python
import os

# 方法 1: 使用 send_keys 方法上传文件（适用于大多数场景）
file_input = driver.find_element(By.ID, "file-upload")
# 使用绝对路径
file_path = os.path.abspath("/path/to/file.txt")
file_input.send_keys(file_path)

# 方法 2: 使用 pyautogui 处理非标准上传组件
import pyautogui
import time

upload_button = driver.find_element(By.ID, "custom-upload")
upload_button.click()
time.sleep(1)  # 等待文件选择对话框出现
pyautogui.write(file_path)
pyautogui.press('enter')
```

### 配置下载目录

```python
import os

# 配置 Chrome 下载设置
download_dir = os.path.abspath("/path/to/download")
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False
}
chrome_options.add_experimental_option("prefs", prefs)

# 初始化 driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
```

### 等待文件下载完成

```python
import os
import time

def wait_for_download(directory, timeout=30):
    """等待下载完成"""
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True
        seconds += 1
    return seconds < timeout

# 触发下载
download_button = driver.find_element(By.ID, "download-button")
download_button.click()

# 等待下载完成
if wait_for_download(download_dir):
    print("文件下载成功")
else:
    print("文件下载超时")
```

## 处理多窗口和标签页

### 在窗口之间切换

```python
# 保存当前窗口句柄
original_window = driver.current_window_handle

# 打开新窗口/标签页
driver.find_element(By.ID, "new-window-button").click()

# 等待新窗口/标签页打开
WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

# 切换到新窗口/标签页
for window_handle in driver.window_handles:
    if window_handle != original_window:
        driver.switch_to.window(window_handle)
        break

# 在新窗口中执行操作
print("新窗口标题:", driver.title)

# 关闭当前窗口/标签页
driver.close()

# 切回原窗口
driver.switch_to.window(original_window)
```

### 创建新标签页

```python
# 使用 JavaScript 打开新标签页
driver.execute_script("window.open('https://www.example.com', '_blank');")

# 切换到新标签页
driver.switch_to.window(driver.window_handles[-1])
```

## 执行 JavaScript

### 基本 JavaScript 执行

```python
# 执行简单的 JavaScript
result = driver.execute_script("return document.title;")
print(f"页面标题: {result}")

# 修改页面内容
driver.execute_script("document.body.style.backgroundColor = 'lightblue';")

# 滚动页面
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 滚动到底部
driver.execute_script("window.scrollTo(0, 0);")  # 滚动到顶部
```

### 使用 JavaScript 操作元素

```python
# 查找并点击元素
element = driver.find_element(By.ID, "my-button")
driver.execute_script("arguments[0].click();", element)

# 修改元素属性
driver.execute_script("arguments[0].setAttribute('style', 'border: 2px solid red;');", element)

# 向下滚动到特定元素
driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
```

### 处理元素的可见性和可交互性

```python
# 检查元素是否在视口中
is_visible = driver.execute_script("""
    var elem = arguments[0];
    var rect = elem.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
""", element)

# 模拟悬停效果
driver.execute_script("""
    var event = new MouseEvent('mouseover', {
        'view': window,
        'bubbles': true,
        'cancelable': true
    });
    arguments[0].dispatchEvent(event);
""", element)
```

## 高级浏览器选项配置

### Chrome 选项

```python
from selenium.webdriver.chrome.options import Options

options = Options()

# 常用选项
options.add_argument("--start-maximized")  # 启动时最大化浏览器
options.add_argument("--incognito")  # 无痕模式
options.add_argument("--disable-extensions")  # 禁用扩展
options.add_argument("--disable-popup-blocking")  # 禁用弹出窗口拦截
options.add_argument("--disable-infobars")  # 禁用信息栏
options.add_argument("--disable-notifications")  # 禁用通知
options.add_argument("--disable-gpu")  # 禁用 GPU 加速
options.add_argument("--proxy-server='direct://'")  # 设置代理
options.add_argument("--proxy-bypass-list=*")  # 绕过代理的地址
options.add_argument("--user-agent=自定义用户代理")  # 自定义用户代理

# 启用移动设备模拟
mobile_emulation = {
    "deviceName": "iPhone X"
}
options.add_experimental_option("mobileEmulation", mobile_emulation)

# 配置下载行为
prefs = {
    "download.default_directory": "/path/to/download",
    "download.prompt_for_download": False
}
options.add_experimental_option("prefs", prefs)

# 初始化 driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

### Firefox 选项

```python
from selenium.webdriver.firefox.options import Options

options = Options()

# 常用选项
options.add_argument("--width=1920")  # 设置窗口宽度
options.add_argument("--height=1080")  # 设置窗口高度
options.add_argument("-private")  # 隐私模式
options.set_preference("browser.download.folderList", 2)  # 使用自定义下载目录
options.set_preference("browser.download.dir", "/path/to/download")  # 设置下载目录
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")  # 不询问直接下载特定类型文件

# 初始化 driver
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
```

## 处理 Shadow DOM

Shadow DOM 是一种 Web 组件技术，用于创建隔离的 DOM 树。处理 Shadow DOM 需要特殊方法。

```python
# 获取 Shadow Host
shadow_host = driver.find_element(By.ID, "shadow-host")

# 获取 Shadow Root
shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

# 在 Shadow DOM 中查找元素
shadow_content = shadow_root.find_element(By.CSS_SELECTOR, ".shadow-content")

# 使用 JavaScript 获取 Shadow DOM 中的元素并进行操作
shadow_button = driver.execute_script("""
    return arguments[0].shadowRoot.querySelector('button.shadow-button');
""", shadow_host)

# 点击 Shadow DOM 中的按钮
driver.execute_script("arguments[0].click();", shadow_button)
```

## 性能优化技巧

### 减少浏览器启动次数

```python
# 在脚本开始时初始化 driver
driver = setup_chrome_driver()

# 多个任务中重用同一个 driver
try:
    # 任务 1
    driver.get("https://www.example1.com")
    # 处理页面...
    
    # 任务 2
    driver.get("https://www.example2.com")
    # 处理页面...
    
    # 任务 3
    driver.get("https://www.example3.com")
    # 处理页面...
finally:
    # 最后关闭 driver
    driver.quit()
```

### 使用显式等待而非隐式等待

```python
# 不推荐：隐式等待会影响所有操作
driver.implicitly_wait(10)

# 推荐：显式等待只影响特定操作
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "my-button"))
)
```

### 使用预加载缓存

```python
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--disk-cache-dir=/path/to/cache")

# 后续启动时使用相同的缓存目录可加快加载速度
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

## 常见问题排查

### 元素不可交互

```python
# 问题: ElementNotInteractableException
# 解决方案 1: 等待元素可交互
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "my-button"))
)

# 解决方案 2: 使用 JavaScript 点击
driver.execute_script("arguments[0].click();", element)

# 解决方案 3: 滚动到元素
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
time.sleep(0.5)  # 给页面一点时间来调整
element.click()
```

### StaleElementReferenceException

```python
# 问题: 元素已过时，无法访问
# 解决方案: 重新查找元素
from selenium.common.exceptions import StaleElementReferenceException

def safe_operation(driver, locator, operation):
    """安全地对元素执行操作"""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            element = driver.find_element(*locator)
            return operation(element)
        except StaleElementReferenceException:
            if attempt == max_attempts - 1:
                raise
            time.sleep(0.5)

# 使用示例
safe_operation(driver, (By.ID, "my-button"), lambda e: e.click())
```

### 超时异常

```python
# 问题: TimeoutException
# 解决方案 1: 增加等待时间
try:
    element = WebDriverWait(driver, 20).until(  # 增加等待时间到 20 秒
        EC.presence_of_element_located((By.ID, "slow-element"))
    )
except TimeoutException:
    print("元素在指定时间内未出现")
    
# 解决方案 2: 使用不同的等待条件
try:
    # 先等待元素存在
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "my-element"))
    )
    # 再等待元素可见
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "my-element"))
    )
except TimeoutException:
    print("元素在指定时间内未出现或未变为可见")
```

### 无法找到元素

```python
# 问题: NoSuchElementException
# 解决方案 1: 使用不同的定位方法
# 尝试 CSS 选择器
element = driver.find_element(By.CSS_SELECTOR, "#my-element")

# 或尝试 XPath
element = driver.find_element(By.XPATH, "//div[@class='container']//button")

# 解决方案 2: 检查元素是否在 iframe 中
iframes = driver.find_elements(By.TAG_NAME, "iframe")
for iframe in iframes:
    driver.switch_to.frame(iframe)
    try:
        element = driver.find_element(By.ID, "my-element")
        # 找到元素，执行操作
        break
    except NoSuchElementException:
        # 切换回主文档
        driver.switch_to.default_content()
        continue
```

---

本指南覆盖了 Selenium 的多种高级用法，帮助您解决网页自动化过程中可能遇到的各种挑战。如有其他问题，请参考[官方文档](https://www.selenium.dev/documentation/)或寻求社区支持。 