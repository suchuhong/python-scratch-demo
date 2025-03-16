#!/bin/bash

# 打印标题
echo "==================================================="
echo "            电影天堂工具集安装向导"
echo "==================================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "✗ Python未安装"
    echo "  请安装Python 3.6或更高版本"
    exit 1
fi

# 获取Python版本
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
    echo "✗ Python版本不满足要求: $PYTHON_VERSION"
    echo "  需要Python 3.6或更高版本"
    exit 1
fi

echo "✓ Python版本满足要求: $PYTHON_VERSION"

# 检查pip是否可用
echo ""
echo "检查pip..."
if $PYTHON_CMD -m pip --version &>/dev/null; then
    echo "✓ pip可用"
else
    echo "✗ pip不可用"
    echo "  请安装pip"
    exit 1
fi

# 安装依赖
echo ""
echo "开始安装电影天堂工具集..."
echo "安装依赖..."
$PYTHON_CMD -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "✗ 依赖安装失败"
    exit 1
fi
echo "✓ 依赖安装成功"

# 安装包
echo ""
echo "安装电影天堂工具集..."
$PYTHON_CMD -m pip install -e .
if [ $? -ne 0 ]; then
    echo "✗ 电影天堂工具集安装失败"
    exit 1
fi

# 打印成功信息
echo ""
echo "==================================================="
echo "                  安装成功!"
echo "==================================================="
echo ""
echo "现在您可以使用以下命令运行电影天堂工具集:"
echo "  dytt8            - 命令行界面"
echo "  dytt8-gui        - 图形用户界面"
echo "  dytt8-full       - 全功能版本"
echo ""
echo "祝您使用愉快!" 