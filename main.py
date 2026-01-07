"""
学生成绩分析与职业规划系统
主程序入口
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import run_app

if __name__ == "__main__":
    run_app()
