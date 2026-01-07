"""
学生成绩分析与职业规划系统 - 配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据库配置
DATABASE_PATH = BASE_DIR / "data" / "student_data.db"

# ============ Claude API配置 ============
# 从环境变量读取API密钥 (请在 .env 文件中配置)
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
CLAUDE_BASE_URL = os.getenv("CLAUDE_BASE_URL", "https://yunwu.ai")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# 应用配置
APP_NAME = "智慧学业规划系统"
APP_VERSION = "2.0.0"

# 学科配置
SUBJECTS = {
    "语文": {"category": "综合", "is_core": True},
    "数学": {"category": "综合", "is_core": True},
    "英语": {"category": "综合", "is_core": True},
    "物理": {"category": "理科", "is_core": False},
    "化学": {"category": "理科", "is_core": False},
    "生物": {"category": "理科", "is_core": False},
    "政治": {"category": "文科", "is_core": False},
    "历史": {"category": "文科", "is_core": False},
    "地理": {"category": "文科", "is_core": False},
}

# 年级配置
GRADES = [
    "初一", "初二", "初三",
    "高一", "高二", "高三"
]

# 考试类型
EXAM_TYPES = [
    "单元测试", "月考", "期中考试", "期末考试", "模拟考试"
]

# 题型配置
QUESTION_TYPES = [
    "单选题", "多选题", "填空题", "判断题", "简答题", "计算题", "论述题", "作文"
]

# 主题色配置 - Apple Human Interface Guidelines
THEME = {
    "primary": "#007AFF",       # Apple Blue
    "primary_dark": "#0056CC",
    "secondary": "#34C759",     # Apple Green
    "accent": "#FF9500",        # Apple Orange
    "danger": "#FF3B30",        # Apple Red
    "warning": "#FFCC00",       # Apple Yellow
    "info": "#5AC8FA",          # Apple Light Blue
    "dark": "#1C1C1E",          # Apple Dark
    "light": "#F2F2F7",         # Apple Light Gray
    "gray": "#8E8E93"           # Apple Gray
}
