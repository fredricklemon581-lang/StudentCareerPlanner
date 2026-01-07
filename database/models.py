"""
数据库模型定义
使用SQLite + 原生SQL实现
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
import json


@dataclass
class Student:
    """学生模型"""
    id: Optional[int] = None
    student_id: str = ""  # 学号
    name: str = ""
    gender: str = ""
    grade: str = ""
    class_name: str = ""
    enrollment_year: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Subject:
    """学科模型"""
    id: Optional[int] = None
    name: str = ""
    category: str = ""  # 文/理/综合
    is_core: bool = False


@dataclass
class Exam:
    """考试模型"""
    id: Optional[int] = None
    name: str = ""
    subject_id: int = 0
    exam_type: str = ""  # 月考/期中/期末/模拟
    exam_date: Optional[date] = None
    total_score: float = 100.0
    grade_scope: str = ""
    difficulty_level: float = 0.5


@dataclass
class ExamScore:
    """成绩模型"""
    id: Optional[int] = None
    student_id: int = 0
    exam_id: int = 0
    score: float = 0.0
    rank_in_class: Optional[int] = None
    rank_in_grade: Optional[int] = None
    score_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgePoint:
    """知识点模型"""
    id: Optional[int] = None
    subject_id: int = 0
    name: str = ""
    parent_id: Optional[int] = None
    level: int = 1
    description: str = ""


@dataclass
class Question:
    """题目模型"""
    id: Optional[int] = None
    subject_id: int = 0
    content: str = ""
    answer: str = ""
    analysis: str = ""
    question_type: str = ""  # 选择/填空/解答等
    difficulty: float = 0.5
    score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class QuestionKnowledge:
    """题目-知识点关联"""
    question_id: int = 0
    knowledge_point_id: int = 0
    weight: float = 1.0


@dataclass
class ExamQuestion:
    """考试-题目关联"""
    exam_id: int = 0
    question_id: int = 0
    order_num: int = 0


@dataclass
class StudentAnswer:
    """学生答题详情"""
    id: Optional[int] = None
    student_id: int = 0
    exam_id: int = 0
    question_id: int = 0
    student_answer: str = ""
    score_obtained: float = 0.0
    is_correct: bool = False


@dataclass
class AIConversation:
    """AI对话记录"""
    id: Optional[int] = None
    student_id: int = 0
    session_id: str = ""
    role: str = ""  # user/assistant
    message: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CareerReport:
    """职业规划报告"""
    id: Optional[int] = None
    student_id: int = 0
    report_date: date = field(default_factory=date.today)
    personality_traits: dict = field(default_factory=dict)
    subject_recommendations: dict = field(default_factory=dict)
    career_recommendations: dict = field(default_factory=dict)
    major_recommendations: dict = field(default_factory=dict)
    detailed_analysis: str = ""
    
    def to_json(self) -> dict:
        """转换为可JSON序列化的字典"""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "report_date": self.report_date.isoformat() if self.report_date else None,
            "personality_traits": self.personality_traits,
            "subject_recommendations": self.subject_recommendations,
            "career_recommendations": self.career_recommendations,
            "major_recommendations": self.major_recommendations,
            "detailed_analysis": self.detailed_analysis
        }
    
    @classmethod
    def from_json(cls, data: dict) -> "CareerReport":
        """从字典创建实例"""
        if isinstance(data.get("report_date"), str):
            data["report_date"] = date.fromisoformat(data["report_date"])
        return cls(**data)


@dataclass
class LearningSession:
    """学习会话记录 - 用于学习行为分析"""
    id: Optional[int] = None
    student_id: int = 0
    subject_id: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0  # 学习时长(分钟)
    focus_score: float = 0.0  # 专注度评分(0-100)
    efficiency_score: float = 0.0  # 效率评分(0-100)
    notes: str = ""  # 学习笔记
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Goal:
    """学习目标 - SMART目标管理"""
    id: Optional[int] = None
    student_id: int = 0
    goal_type: str = ""  # 成绩目标/排名目标/知识点目标
    title: str = ""  # 目标标题
    description: str = ""  # 详细描述
    target_value: float = 0.0  # 目标值
    current_value: float = 0.0  # 当前值
    start_date: date = field(default_factory=date.today)
    deadline: date = field(default_factory=date.today)
    status: str = "进行中"  # 进行中/已完成/已放弃
    progress: float = 0.0  # 进度百分比(0-100)
    subject_id: Optional[int] = None  # 关联科目(可选)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class Achievement:
    """成就记录 - 游戏化激励"""
    id: Optional[int] = None
    student_id: int = 0
    achievement_type: str = ""  # 进步之星/学霸勋章/坚持达人等
    title: str = ""
    description: str = ""
    icon: str = ""  # 图标emoji或路径
    unlock_date: datetime = field(default_factory=datetime.now)
    related_goal_id: Optional[int] = None  # 关联目标


@dataclass
class EmotionLog:
    """情绪日记 - 心理健康监测"""
    id: Optional[int] = None
    student_id: int = 0
    log_date: date = field(default_factory=date.today)
    mood_score: int = 3  # 心情评分 1(很差)-5(很好)
    stress_level: int = 3  # 压力等级 1(很轻松)-5(很大压力)
    energy_level: int = 3  # 精力水平 1(疲惫)-5(充沛)
    study_motivation: int = 3  # 学习动力 1(很低)-5(很高)
    diary_content: str = ""  # 日记内容
    tags: str = ""  # 标签(用逗号分隔): 焦虑,兴奋,疲惫等
    ai_suggestions: str = ""  # AI生成的建议(自动填充)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MistakeNote:
    """错题本 - 智能错题管理"""
    id: Optional[int] = None
    student_id: int = 0
    subject_id: int = 0
    question_id: Optional[int] = None  # 关联题目(若存在)
    exam_id: Optional[int] = None  # 来源考试
    question_content: str = ""  # 题目内容
    correct_answer: str = ""  # 正确答案
    student_answer: str = ""  # 学生的错误答案
    error_reason: str = ""  # 错误原因
    knowledge_points: str = ""  # 关联知识点(逗号分隔)
    difficulty_level: int = 3  # 难度 1-5
    review_count: int = 0  # 复习次数
    mastered: bool = False  # 是否已掌握
    next_review_date: Optional[date] = None  # 下次复习日期
    notes: str = ""  # 备注
    created_at: datetime = field(default_factory=datetime.now)
    last_review_date: Optional[datetime] = None


@dataclass
class ResourceRecommendation:
    """学习资源推荐记录"""
    id: Optional[int] = None
    student_id: int = 0
    subject_id: int = 0
    knowledge_point: str = ""  # 针对的知识点
    resource_type: str = ""  # 视频/文章/练习题/在线课程
    title: str = ""
    description: str = ""
    url: str = ""
    difficulty_level: int = 3  # 难度 1-5
    estimated_duration: int = 0  # 预计学习时长(分钟)
    priority: int = 3  # 推荐优先级 1-5
    is_completed: bool = False  # 是否已完成
    rating: Optional[int] = None  # 学生评分 1-5
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

