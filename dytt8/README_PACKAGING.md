# 电影天堂工具集 - 跨平台打包指南

本文档提供了多种方法来打包电影天堂工具集，使其能够在不同的操作系统上运行。

## 方法1：使用PyInstaller打包（推荐）

PyInstaller可以将Python脚本和所有依赖打包成单个可执行文件。我们已经提供了一个打包脚本`build.py`来简化这个过程。

### 步骤：

1. 确保已安装PyInstaller：
   ```
   pip install pyinstaller
   ```

2. 进入dytt8目录：
   ```
   cd dytt8
   ```

3. 运行打包脚本：
   ```
   python build.py
   ```

4. 打包完成后，可执行文件将位于`dist`目录中。
   - Windows：`dist/电影天堂工具集.exe`
   - macOS：`dist/电影天堂工具集`
   - Linux：`dist/电影天堂工具集`

### 注意事项：

- 打包后的程序仍然需要目标计算机安装Chrome浏览器
- 首次运行时会自动下载与浏览器匹配的ChromeDriver
- 如遇到兼容性问题，可以在程序中使用选项5修复ChromeDriver

## 方法2：使用conda环境导出

如果目标用户熟悉conda，可以使用以下方法导出环境：

1. 创建conda环境：
   ```
   conda create -n dytt8 python=3.10
   conda activate dytt8
   pip install -r requirements.txt
   ```

2. 导出环境：
   ```
   conda env export > environment.yml
   ```

3. 在目标计算机上还原环境：
   ```
   conda env create -f environment.yml
   conda activate dytt8
   ```

## 方法3：使用Docker容器化（高级用户）

Docker可以确保在任何平台上提供一致的运行环境。

1. 创建Dockerfile：
   ```dockerfile
   FROM python:3.10-slim
   
   # 安装Chrome
   RUN apt-get update && apt-get install -y \
       wget \
       gnupg \
       unzip \
       xvfb \
       libxi6 \
       libgconf-2-4 \
       default-jdk \
       curl
   
   # 安装Chrome浏览器
   RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
       && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
       && apt-get update \
       && apt-get install -y google-chrome-stable
   
   # 设置工作目录
   WORKDIR /app
   
   # 复制代码
   COPY . /app/
   
   # 安装Python依赖
   RUN pip install --no-cache-dir -r requirements.txt
   
   # 运行应用
   CMD ["python", "main.py"]
   ```

2. 构建Docker镜像：
   ```
   docker build -t dytt8-tools .
   ```

3. 运行Docker容器：
   ```
   docker run -it dytt8-tools
   ```

## 方法4：使用虚拟环境和requirements.txt（开发者推荐）

1. 创建虚拟环境：
   ```
   python -m venv dytt8-env
   ```

2. 激活虚拟环境：
   - Windows: `dytt8-env\Scripts\activate`
   - macOS/Linux: `source dytt8-env/bin/activate`

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

4. 运行程序：
   ```
   python main.py
   ```

## 分发注意事项

无论选择哪种方法，以下事项都需要注意：

1. **浏览器依赖**: 所有方法都需要目标计算机安装Chrome浏览器
2. **网络需求**: 首次运行时需要网络连接来下载ChromeDriver
3. **兼容性**: 如遇到问题，选择使用选项3或4的脚本版本，它们拥有更好的兼容性
4. **文件路径**: 打包后的程序可能对中文路径敏感，建议放在英文路径下运行

## 支持平台

- Windows 10/11
- macOS 10.15+
- Ubuntu 20.04+/其他主流Linux发行版

## 故障排除

如果遇到以下问题：

1. **ChromeDriver错误**: 使用程序中的选项5修复
2. **无法启动浏览器**: 确保已安装Chrome/Chromium浏览器
3. **依赖缺失**: 使用`pip install -r requirements.txt`安装依赖 