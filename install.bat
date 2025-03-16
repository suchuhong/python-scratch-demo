@echo off
echo ===================================================
echo            电影天堂工具集安装向导
echo ===================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python未安装或未添加到PATH环境变量中。
    echo 请安装Python 3.6或更高版本，并确保将其添加到PATH环境变量中。
    echo 安装地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查pip是否可用
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip未安装或不可用。
    echo 请确保pip已正确安装。
    pause
    exit /b 1
)

echo 开始安装电影天堂工具集...
echo.

REM 安装依赖
echo 安装依赖...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 依赖安装失败，请查看上面的错误信息。
    pause
    exit /b 1
)
echo 依赖安装成功！
echo.

REM 安装包
echo 安装电影天堂工具集...
python -m pip install -e .
if %errorlevel% neq 0 (
    echo 电影天堂工具集安装失败，请查看上面的错误信息。
    pause
    exit /b 1
)

echo.
echo ===================================================
echo                  安装成功!
echo ===================================================
echo.
echo 现在您可以使用以下命令运行电影天堂工具集:
echo   dytt8            - 命令行界面
echo   dytt8-gui        - 图形用户界面
echo   dytt8-full       - 全功能版本
echo.
echo 祝您使用愉快!
echo.
pause 