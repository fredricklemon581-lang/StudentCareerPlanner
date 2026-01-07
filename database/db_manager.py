"""
数据库管理器
处理SQLite数据库的创建、连接和CRUD操作
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, date
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager

from .models import (
    Student, Subject, Exam, ExamScore, KnowledgePoint,
    Question, QuestionKnowledge, ExamQuestion, StudentAnswer,
    AIConversation, CareerReport, LearningSession, Goal,
    Achievement, EmotionLog, MistakeNote, ResourceRecommendation
)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 学生表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    gender VARCHAR(10),
                    grade VARCHAR(20),
                    class_name VARCHAR(20),
                    enrollment_year INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 学科表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(20) UNIQUE NOT NULL,
                    category VARCHAR(10),
                    is_core BOOLEAN DEFAULT 0
                )
            ''')
            
            # 考试表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    subject_id INTEGER,
                    exam_type VARCHAR(20),
                    exam_date DATE,
                    total_score DECIMAL DEFAULT 100,
                    grade_scope VARCHAR(20),
                    difficulty_level DECIMAL DEFAULT 0.5,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            ''')
            
            # 成绩表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exam_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    exam_id INTEGER NOT NULL,
                    score DECIMAL NOT NULL,
                    rank_in_class INTEGER,
                    rank_in_grade INTEGER,
                    score_rate DECIMAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (exam_id) REFERENCES exams(id),
                    UNIQUE(student_id, exam_id)
                )
            ''')
            
            # 知识点表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    parent_id INTEGER,
                    level INTEGER DEFAULT 1,
                    description TEXT,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id),
                    FOREIGN KEY (parent_id) REFERENCES knowledge_points(id)
                )
            ''')
            
            # 题目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    answer TEXT,
                    analysis TEXT,
                    question_type VARCHAR(20),
                    difficulty DECIMAL DEFAULT 0.5,
                    score DECIMAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            ''')
            
            # 题目-知识点关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_knowledge (
                    question_id INTEGER NOT NULL,
                    knowledge_point_id INTEGER NOT NULL,
                    weight DECIMAL DEFAULT 1.0,
                    PRIMARY KEY (question_id, knowledge_point_id),
                    FOREIGN KEY (question_id) REFERENCES questions(id),
                    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id)
                )
            ''')
            
            # 考试-题目关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exam_questions (
                    exam_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    order_num INTEGER,
                    PRIMARY KEY (exam_id, question_id),
                    FOREIGN KEY (exam_id) REFERENCES exams(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            ''')
            
            # 学生答题详情表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    exam_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    student_answer TEXT,
                    score_obtained DECIMAL DEFAULT 0,
                    is_correct BOOLEAN DEFAULT 0,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (exam_id) REFERENCES exams(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            ''')
            
            # AI对话记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    session_id VARCHAR(50) NOT NULL,
                    role VARCHAR(10) NOT NULL,
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            ''')
            
            # 职业规划报告表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS career_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    report_date DATE DEFAULT CURRENT_DATE,
                    personality_traits JSON,
                    subject_recommendations JSON,
                    career_recommendations JSON,
                    major_recommendations JSON,
                    detailed_analysis TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            ''')
            
            # 学习会话记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration_minutes DECIMAL DEFAULT 0,
                    focus_score DECIMAL DEFAULT 0,
                    efficiency_score DECIMAL DEFAULT 0,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            ''')
            
            # 学习目标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    goal_type VARCHAR(50),
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    target_value DECIMAL DEFAULT 0,
                    current_value DECIMAL DEFAULT 0,
                    start_date DATE,
                    deadline DATE,
                    status VARCHAR(20) DEFAULT '进行中',
                    progress DECIMAL DEFAULT 0,
                    subject_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            ''')
            
            # 成就记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    achievement_type VARCHAR(50),
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    icon VARCHAR(100),
                    unlock_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    related_goal_id INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (related_goal_id) REFERENCES goals(id)
                )
            ''')
            
            # 情绪日记表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotion_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    log_date DATE DEFAULT CURRENT_DATE,
                    mood_score INTEGER DEFAULT 3,
                    stress_level INTEGER DEFAULT 3,
                    energy_level INTEGER DEFAULT 3,
                    study_motivation INTEGER DEFAULT 3,
                    diary_content TEXT,
                    tags VARCHAR(200),
                    ai_suggestions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
            ''')
            
            # 错题本表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mistake_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    question_id INTEGER,
                    exam_id INTEGER,
                    question_content TEXT NOT NULL,
                    correct_answer TEXT,
                    student_answer TEXT,
                    error_reason TEXT,
                    knowledge_points VARCHAR(500),
                    difficulty_level INTEGER DEFAULT 3,
                    review_count INTEGER DEFAULT 0,
                    mastered BOOLEAN DEFAULT 0,
                    next_review_date DATE,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_review_date DATETIME,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id),
                    FOREIGN KEY (question_id) REFERENCES questions(id),
                    FOREIGN KEY (exam_id) REFERENCES exams(id)
                )
            ''')
            
            # 学习资源推荐表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resource_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    knowledge_point VARCHAR(200),
                    resource_type VARCHAR(50),
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    url TEXT,
                    difficulty_level INTEGER DEFAULT 3,
                    estimated_duration INTEGER DEFAULT 0,
                    priority INTEGER DEFAULT 3,
                    is_completed BOOLEAN DEFAULT 0,
                    rating INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id)
                )
            ''')
            
            # 初始化学科数据
            self._init_subjects(cursor)
    
    def _init_subjects(self, cursor):
        """初始化学科数据"""
        subjects = [
            ("语文", "综合", True),
            ("数学", "综合", True),
            ("英语", "综合", True),
            ("物理", "理科", False),
            ("化学", "理科", False),
            ("生物", "理科", False),
            ("政治", "文科", False),
            ("历史", "文科", False),
            ("地理", "文科", False),
        ]
        
        for name, category, is_core in subjects:
            cursor.execute('''
                INSERT OR IGNORE INTO subjects (name, category, is_core)
                VALUES (?, ?, ?)
            ''', (name, category, is_core))
    
    # ============ 学生CRUD ============
    
    def add_student(self, student: Student) -> int:
        """添加学生"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (student_id, name, gender, grade, class_name, enrollment_year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student.student_id, student.name, student.gender, 
                  student.grade, student.class_name, student.enrollment_year))
            return cursor.lastrowid
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """通过学号获取学生"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
            row = cursor.fetchone()
            if row:
                return Student(
                    id=row['id'],
                    student_id=row['student_id'],
                    name=row['name'],
                    gender=row['gender'],
                    grade=row['grade'],
                    class_name=row['class_name'],
                    enrollment_year=row['enrollment_year'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None
    
    def get_student_by_id(self, id: int) -> Optional[Student]:
        """通过ID获取学生"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return Student(
                    id=row['id'],
                    student_id=row['student_id'],
                    name=row['name'],
                    gender=row['gender'],
                    grade=row['grade'],
                    class_name=row['class_name'],
                    enrollment_year=row['enrollment_year'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
            return None
    
    def get_all_students(self) -> List[Student]:
        """获取所有学生"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM students ORDER BY student_id')
            rows = cursor.fetchall()
            return [
                Student(
                    id=row['id'],
                    student_id=row['student_id'],
                    name=row['name'],
                    gender=row['gender'],
                    grade=row['grade'],
                    class_name=row['class_name'],
                    enrollment_year=row['enrollment_year'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                for row in rows
            ]
    
    def update_student(self, student: Student) -> bool:
        """更新学生信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE students 
                SET name = ?, gender = ?, grade = ?, class_name = ?, enrollment_year = ?
                WHERE id = ?
            ''', (student.name, student.gender, student.grade, 
                  student.class_name, student.enrollment_year, student.id))
            return cursor.rowcount > 0
    
    def delete_student(self, student_id: int) -> bool:
        """删除学生"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
            return cursor.rowcount > 0
    
    def search_students(self, keyword: str) -> List[Student]:
        """搜索学生"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            pattern = f"%{keyword}%"
            cursor.execute('''
                SELECT * FROM students 
                WHERE student_id LIKE ? OR name LIKE ?
                ORDER BY student_id
            ''', (pattern, pattern))
            rows = cursor.fetchall()
            return [
                Student(
                    id=row['id'],
                    student_id=row['student_id'],
                    name=row['name'],
                    gender=row['gender'],
                    grade=row['grade'],
                    class_name=row['class_name'],
                    enrollment_year=row['enrollment_year'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                for row in rows
            ]
    
    # ============ 学科操作 ============
    
    def get_all_subjects(self) -> List[Subject]:
        """获取所有学科"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM subjects ORDER BY id')
            rows = cursor.fetchall()
            return [
                Subject(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    is_core=bool(row['is_core'])
                )
                for row in rows
            ]
    
    def get_subject_by_name(self, name: str) -> Optional[Subject]:
        """通过名称获取学科"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM subjects WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                return Subject(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    is_core=bool(row['is_core'])
                )
            return None
    
    # ============ 考试CRUD ============
    
    def add_exam(self, exam: Exam) -> int:
        """添加考试"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO exams (name, subject_id, exam_type, exam_date, total_score, grade_scope, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (exam.name, exam.subject_id, exam.exam_type, 
                  exam.exam_date.isoformat() if exam.exam_date else None,
                  exam.total_score, exam.grade_scope, exam.difficulty_level))
            return cursor.lastrowid
    
    def get_all_exams(self) -> List[Exam]:
        """获取所有考试"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM exams ORDER BY exam_date DESC')
            rows = cursor.fetchall()
            return [
                Exam(
                    id=row['id'],
                    name=row['name'],
                    subject_id=row['subject_id'],
                    exam_type=row['exam_type'],
                    exam_date=date.fromisoformat(row['exam_date']) if row['exam_date'] else None,
                    total_score=row['total_score'],
                    grade_scope=row['grade_scope'],
                    difficulty_level=row['difficulty_level']
                )
                for row in rows
            ]
    
    def get_exams_by_subject(self, subject_id: int) -> List[Exam]:
        """获取某学科的所有考试"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM exams WHERE subject_id = ? ORDER BY exam_date DESC', (subject_id,))
            rows = cursor.fetchall()
            return [
                Exam(
                    id=row['id'],
                    name=row['name'],
                    subject_id=row['subject_id'],
                    exam_type=row['exam_type'],
                    exam_date=date.fromisoformat(row['exam_date']) if row['exam_date'] else None,
                    total_score=row['total_score'],
                    grade_scope=row['grade_scope'],
                    difficulty_level=row['difficulty_level']
                )
                for row in rows
            ]
    
    # ============ 成绩CRUD ============
    
    def add_score(self, score: ExamScore) -> int:
        """添加成绩"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO exam_scores 
                (student_id, exam_id, score, rank_in_class, rank_in_grade, score_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (score.student_id, score.exam_id, score.score,
                  score.rank_in_class, score.rank_in_grade, score.score_rate))
            return cursor.lastrowid
    
    def get_student_scores(self, student_id: int) -> List[Tuple[ExamScore, Exam, Subject]]:
        """获取学生的所有成绩（包含考试和学科信息）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT es.*, e.*, s.name as subject_name, s.category, s.is_core
                FROM exam_scores es
                JOIN exams e ON es.exam_id = e.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE es.student_id = ?
                ORDER BY e.exam_date DESC
            ''', (student_id,))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                score = ExamScore(
                    id=row['id'],
                    student_id=row['student_id'],
                    exam_id=row['exam_id'],
                    score=row['score'],
                    rank_in_class=row['rank_in_class'],
                    rank_in_grade=row['rank_in_grade'],
                    score_rate=row['score_rate']
                )
                exam = Exam(
                    id=row['exam_id'],
                    name=row['name'],
                    subject_id=row['subject_id'],
                    exam_type=row['exam_type'],
                    exam_date=date.fromisoformat(row['exam_date']) if row['exam_date'] else None,
                    total_score=row['total_score']
                )
                subject = Subject(
                    id=row['subject_id'],
                    name=row['subject_name'],
                    category=row['category'],
                    is_core=bool(row['is_core'])
                )
                results.append((score, exam, subject))
            
            return results
    
    def get_student_scores_by_subject(self, student_id: int, subject_id: int) -> List[Tuple[ExamScore, Exam]]:
        """获取学生某学科的所有成绩"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT es.*, e.*
                FROM exam_scores es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = ? AND e.subject_id = ?
                ORDER BY e.exam_date ASC
            ''', (student_id, subject_id))
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                score = ExamScore(
                    id=row['id'],
                    student_id=row['student_id'],
                    exam_id=row['exam_id'],
                    score=row['score'],
                    rank_in_class=row['rank_in_class'],
                    rank_in_grade=row['rank_in_grade'],
                    score_rate=row['score_rate']
                )
                exam = Exam(
                    id=row['exam_id'],
                    name=row['name'],
                    subject_id=row['subject_id'],
                    exam_type=row['exam_type'],
                    exam_date=date.fromisoformat(row['exam_date']) if row['exam_date'] else None,
                    total_score=row['total_score']
                )
                results.append((score, exam))
            
            return results
    
    # ============ 知识点CRUD ============
    
    def add_knowledge_point(self, kp: KnowledgePoint) -> int:
        """添加知识点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO knowledge_points (subject_id, name, parent_id, level, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (kp.subject_id, kp.name, kp.parent_id, kp.level, kp.description))
            return cursor.lastrowid
    
    def get_knowledge_points_by_subject(self, subject_id: int) -> List[KnowledgePoint]:
        """获取某学科的所有知识点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM knowledge_points WHERE subject_id = ? ORDER BY level, id', (subject_id,))
            rows = cursor.fetchall()
            return [
                KnowledgePoint(
                    id=row['id'],
                    subject_id=row['subject_id'],
                    name=row['name'],
                    parent_id=row['parent_id'],
                    level=row['level'],
                    description=row['description']
                )
                for row in rows
            ]
    
    # ============ 题目CRUD ============
    
    def add_question(self, question: Question) -> int:
        """添加题目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO questions (subject_id, content, answer, analysis, question_type, difficulty, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (question.subject_id, question.content, question.answer,
                  question.analysis, question.question_type, question.difficulty, question.score))
            return cursor.lastrowid
    
    def get_questions_by_subject(self, subject_id: int) -> List[Question]:
        """获取某学科的所有题目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM questions WHERE subject_id = ? ORDER BY id', (subject_id,))
            rows = cursor.fetchall()
            return [
                Question(
                    id=row['id'],
                    subject_id=row['subject_id'],
                    content=row['content'],
                    answer=row['answer'],
                    analysis=row['analysis'],
                    question_type=row['question_type'],
                    difficulty=row['difficulty'],
                    score=row['score']
                )
                for row in rows
            ]
    
    def link_question_to_knowledge(self, question_id: int, knowledge_point_id: int, weight: float = 1.0):
        """关联题目和知识点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO question_knowledge (question_id, knowledge_point_id, weight)
                VALUES (?, ?, ?)
            ''', (question_id, knowledge_point_id, weight))
    
    def link_question_to_exam(self, exam_id: int, question_id: int, order_num: int):
        """关联题目和考试"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO exam_questions (exam_id, question_id, order_num)
                VALUES (?, ?, ?)
            ''', (exam_id, question_id, order_num))
    
    # ============ 学生答题CRUD ============
    
    def add_student_answer(self, answer: StudentAnswer) -> int:
        """添加学生答题记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_answers (student_id, exam_id, question_id, student_answer, score_obtained, is_correct)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (answer.student_id, answer.exam_id, answer.question_id,
                  answer.student_answer, answer.score_obtained, answer.is_correct))
            return cursor.lastrowid
    
    def get_student_answers_for_exam(self, student_id: int, exam_id: int) -> List[StudentAnswer]:
        """获取学生某次考试的答题详情"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM student_answers
                WHERE student_id = ? AND exam_id = ?
                ORDER BY id
            ''', (student_id, exam_id))
            rows = cursor.fetchall()
            return [
                StudentAnswer(
                    id=row['id'],
                    student_id=row['student_id'],
                    exam_id=row['exam_id'],
                    question_id=row['question_id'],
                    student_answer=row['student_answer'],
                    score_obtained=row['score_obtained'],
                    is_correct=bool(row['is_correct'])
                )
                for row in rows
            ]
    
    # ============ AI对话CRUD ============
    
    def add_conversation(self, conv: AIConversation) -> int:
        """添加对话记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_conversations (student_id, session_id, role, message)
                VALUES (?, ?, ?, ?)
            ''', (conv.student_id, conv.session_id, conv.role, conv.message))
            return cursor.lastrowid
    
    def get_conversation_history(self, student_id: int, session_id: str) -> List[AIConversation]:
        """获取对话历史"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ai_conversations
                WHERE student_id = ? AND session_id = ?
                ORDER BY created_at ASC
            ''', (student_id, session_id))
            rows = cursor.fetchall()
            return [
                AIConversation(
                    id=row['id'],
                    student_id=row['student_id'],
                    session_id=row['session_id'],
                    role=row['role'],
                    message=row['message'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                for row in rows
            ]
    
    def get_all_sessions(self, student_id: int) -> List[str]:
        """获取学生的所有会话ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT session_id FROM ai_conversations
                WHERE student_id = ?
                ORDER BY created_at DESC
            ''', (student_id,))
            rows = cursor.fetchall()
            return [row['session_id'] for row in rows]
    
    # ============ 职业报告CRUD ============
    
    def add_career_report(self, report: CareerReport) -> int:
        """添加职业规划报告"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO career_reports 
                (student_id, report_date, personality_traits, subject_recommendations, 
                 career_recommendations, major_recommendations, detailed_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (report.student_id, 
                  report.report_date.isoformat() if report.report_date else None,
                  json.dumps(report.personality_traits, ensure_ascii=False),
                  json.dumps(report.subject_recommendations, ensure_ascii=False),
                  json.dumps(report.career_recommendations, ensure_ascii=False),
                  json.dumps(report.major_recommendations, ensure_ascii=False),
                  report.detailed_analysis))
            return cursor.lastrowid
    
    def get_career_reports(self, student_id: int) -> List[CareerReport]:
        """获取学生的所有职业规划报告"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM career_reports
                WHERE student_id = ?
                ORDER BY report_date DESC
            ''', (student_id,))
            rows = cursor.fetchall()
            return [
                CareerReport(
                    id=row['id'],
                    student_id=row['student_id'],
                    report_date=date.fromisoformat(row['report_date']) if row['report_date'] else None,
                    personality_traits=json.loads(row['personality_traits']) if row['personality_traits'] else {},
                    subject_recommendations=json.loads(row['subject_recommendations']) if row['subject_recommendations'] else {},
                    career_recommendations=json.loads(row['career_recommendations']) if row['career_recommendations'] else {},
                    major_recommendations=json.loads(row['major_recommendations']) if row['major_recommendations'] else {},
                    detailed_analysis=row['detailed_analysis']
                )
                for row in rows
            ]
    
    # ============ 统计查询 ============
    
    def get_statistics(self) -> dict:
        """获取数据库统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM students')
            student_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM exams')
            exam_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM exam_scores')
            score_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM questions')
            question_count = cursor.fetchone()['count']
            
            return {
                "students": student_count,
                "exams": exam_count,
                "scores": score_count,
                "questions": question_count
            }
    
    # ============ 知识点得分分析 ============
    
    def get_knowledge_point_mastery(self, student_id: int) -> List[dict]:
        """
        分析学生在各知识点上的得分率
        
        Returns:
            [{
                'knowledge_point': str,
                'subject': str,
                'total_questions': int,
                'total_score': float,
                'obtained_score': float,
                'mastery_rate': float,
                'is_weak': bool
            }, ...]
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    kp.name as kp_name,
                    s.name as subject_name,
                    COUNT(sa.id) as question_count,
                    SUM(q.score) as total_score,
                    SUM(sa.score_obtained) as obtained_score
                FROM student_answers sa
                JOIN questions q ON sa.question_id = q.id
                JOIN question_knowledge qk ON q.id = qk.question_id
                JOIN knowledge_points kp ON qk.knowledge_point_id = kp.id
                JOIN subjects s ON kp.subject_id = s.id
                WHERE sa.student_id = ?
                GROUP BY kp.id
                ORDER BY s.id, kp.level, kp.id
            ''', (student_id,))
            
            rows = cursor.fetchall()
            results = []
            
            for row in rows:
                total = row['total_score'] or 0
                obtained = row['obtained_score'] or 0
                rate = obtained / total if total > 0 else 0
                
                results.append({
                    'knowledge_point': row['kp_name'],
                    'subject': row['subject_name'],
                    'total_questions': row['question_count'],
                    'total_score': total,
                    'obtained_score': obtained,
                    'mastery_rate': round(rate, 3),
                    'is_weak': rate < 0.6
                })
            
            return results
    
    def get_exam_statistics(self, subject_id: int = None) -> List[dict]:
        """
        获取考试统计信息（日期、参与人数、平均分）
        
        Args:
            subject_id: 可选，按学科过滤
        
        Returns:
            [{
                'exam_id': int,
                'exam_name': str,
                'subject_name': str,
                'exam_date': str,
                'total_score': float,
                'participant_count': int,
                'average_score': float,
                'avg_score_rate': float
            }, ...]
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if subject_id:
                cursor.execute('''
                    SELECT 
                        e.id as exam_id,
                        e.name as exam_name,
                        s.name as subject_name,
                        e.exam_date,
                        e.total_score,
                        COUNT(es.id) as participant_count,
                        AVG(es.score) as average_score,
                        AVG(es.score_rate) as avg_score_rate
                    FROM exams e
                    JOIN subjects s ON e.subject_id = s.id
                    LEFT JOIN exam_scores es ON e.id = es.exam_id
                    WHERE e.subject_id = ?
                    GROUP BY e.id
                    ORDER BY e.exam_date DESC
                ''', (subject_id,))
            else:
                cursor.execute('''
                    SELECT 
                        e.id as exam_id,
                        e.name as exam_name,
                        s.name as subject_name,
                        e.exam_date,
                        e.total_score,
                        COUNT(es.id) as participant_count,
                        AVG(es.score) as average_score,
                        AVG(es.score_rate) as avg_score_rate
                    FROM exams e
                    JOIN subjects s ON e.subject_id = s.id
                    LEFT JOIN exam_scores es ON e.id = es.exam_id
                    GROUP BY e.id
                    ORDER BY e.exam_date DESC
                ''')
            
            rows = cursor.fetchall()
            return [
                {
                    'exam_id': row['exam_id'],
                    'exam_name': row['exam_name'],
                    'subject_name': row['subject_name'],
                    'exam_date': row['exam_date'] or '',
                    'total_score': row['total_score'] or 100,
                    'participant_count': row['participant_count'] or 0,
                    'average_score': round(row['average_score'] or 0, 1),
                    'avg_score_rate': round((row['avg_score_rate'] or 0) * 100, 1)
                }
                for row in rows
            ]
    
    # ==================== 智能出卷系统支持方法 ====================
    
    def get_questions_by_knowledge_point(self, kp_id: int) -> List[Question]:
        """获取包含指定知识点的所有题目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT q.id, q.subject_id, q.content, q.answer, 
                       q.analysis, q.question_type, q.difficulty, q.score
                FROM questions q
                JOIN question_knowledge qk ON q.id = qk.question_id
                WHERE qk.knowledge_point_id = ?
            ''', (kp_id,))
            
            questions = []
            for row in cursor.fetchall():
                questions.append(Question(
                    id=row[0],
                    subject_id=row[1],
                    content=row[2],
                    answer=row[3],
                    analysis=row[4],
                    question_type=row[5],
                    difficulty=row[6],
                    score=row[7]
                ))
            return questions
    
    def get_student_all_answers(self, student_id: int) -> List[StudentAnswer]:
        """获取学生的所有答题记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, student_id, exam_id, question_id, 
                       student_answer, score_obtained, is_correct
                FROM student_answers
                WHERE student_id = ?
            ''', (student_id,))
            
            answers = []
            for row in cursor.fetchall():
                answers.append(StudentAnswer(
                    id=row[0],
                    student_id=row[1],
                    exam_id=row[2],
                    question_id=row[3],
                    student_answer=row[4],
                    score_obtained=row[5],
                    is_correct=bool(row[6])
                ))
            return answers
    
    def get_question_knowledge_points(self, question_id: int) -> List[KnowledgePoint]:
        """获取题目关联的所有知识点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT kp.id, kp.subject_id, kp.name, kp.parent_id, 
                       kp.level, kp.description
                FROM knowledge_points kp
                JOIN question_knowledge qk ON kp.id = qk.knowledge_point_id
                WHERE qk.question_id = ?
            ''', (question_id,))
            
            kps = []
            for row in cursor.fetchall():
                kps.append(KnowledgePoint(
                    id=row[0],
                    subject_id=row[1],
                    name=row[2],
                    parent_id=row[3],
                    level=row[4],
                    description=row[5]
                ))
            return kps
    
    def search_questions(self, filters: dict) -> List[Question]:
        """高级题目搜索
        
        Args:
            filters: {
                'subject_id': int,
                'knowledge_point_ids': List[int],
                'question_type': str,
                'min_difficulty': float,
                'max_difficulty': float,
                'exclude_ids': List[int]
            }
        """
        query = '''
            SELECT DISTINCT q.id, q.subject_id, q.content, q.answer,
                   q.analysis, q.question_type, q.difficulty, q.score
            FROM questions q
        '''
        
        conditions = []
        params = []
        
        # 如果要按知识点筛选
        if filters.get('knowledge_point_ids'):
            query += ' JOIN question_knowledge qk ON q.id = qk.question_id '
            kp_placeholders = ','.join('?' * len(filters['knowledge_point_ids']))
            conditions.append(f'qk.knowledge_point_id IN ({kp_placeholders})')
            params.extend(filters['knowledge_point_ids'])
        
        # 其他筛选条件
        if filters.get('subject_id'):
            conditions.append('q.subject_id = ?')
            params.append(filters['subject_id'])
        
        if filters.get('question_type'):
            conditions.append('q.question_type = ?')
            params.append(filters['question_type'])
        
        if filters.get('min_difficulty') is not None:
            conditions.append('q.difficulty >= ?')
            params.append(filters['min_difficulty'])
        
        if filters.get('max_difficulty') is not None:
            conditions.append('q.difficulty <= ?')
            params.append(filters['max_difficulty'])
        
        if filters.get('exclude_ids'):
            exclude_placeholders = ','.join('?' * len(filters['exclude_ids']))
            conditions.append(f'q.id NOT IN ({exclude_placeholders})')
            params.extend(filters['exclude_ids'])
        
        # 组合查询
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            questions = []
            for row in cursor.fetchall():
                questions.append(Question(
                    id=row[0],
                    subject_id=row[1],
                    content=row[2],
                    answer=row[3],
                    analysis=row[4],
                    question_type=row[5],
                    difficulty=row[6],
                    score=row[7]
                ))
            return questions
