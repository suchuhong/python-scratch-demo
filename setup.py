#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dytt8",
    version="1.0.0",
    author="AI Developer",
    author_email="ai@example.com",
    description="电影天堂工具集 - 电影资源爬取与管理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dytt8",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
        "pandas>=1.0.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "tqdm>=4.50.0",
        "flask>=2.0.0",
        "apscheduler>=3.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "pylint>=2.0.0",
            "mypy>=0.9.0",
            "sphinx>=4.0.0",
            "twine>=3.0.0",
            "wheel>=0.37.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dytt8=dytt8.__main__:main",
            "dytt8-gui=dytt8.gui.main_gui:start_gui",
            "dytt8-full=dytt8.main_full:main",
        ],
    },
) 