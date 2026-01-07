"""
学习行为分析服务
分析学习时长、效率、专注度等
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager
from database.models import LearningSession
import statistics


class LearningBehaviorService:
    """学习行为分析服务"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def start_learning_session(self, student_id: int, subject_id: int) -> int:
        """开始学习会话"""
        session = LearningSession(
            student_id=student_id,
            subject_id=subject_id,
            start_time=datetime.now()
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO learning_sessions 
                (student_id, subject_id, start_time)
                VALUES (?, ?, ?)
            ''', (session.student_id, session.subject_id, session.start_time.isoformat()))
            return cursor.lastrowid
    
    def end_learning_session(self, session_id: int, focus_score: float = 0, notes: str = ""):
        """结束学习会话"""
        end_time = datetime.now()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取开始时间
            cursor.execute('SELECT start_time FROM learning_sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            start_time = datetime.fromisoformat(row['start_time'])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            
            # 计算效率分数(基于时长和专注度的简单算法)
            efficiency_score = min(100, focus_score * (duration_minutes / 30) * 0.5)
            
            cursor.execute('''
                UPDATE learning_sessions 
                SET end_time = ?, duration_minutes = ?, focus_score = ?, 
                    efficiency_score = ?, notes = ?
                WHERE id = ?
            ''', (end_time.isoformat(), duration_minutes, focus_score,
                  efficiency_score, notes, session_id))
            
            return cursor.rowcount > 0
    
    def get_time_investment_analysis(self, student_id: int, days: int = 30) -> Dict:
        """获取时间投入分析"""
        start_date = date.today() - timedelta(days=days)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 查询最近的学习记录
            cursor.execute('''
                SELECT 
                    ls.subject_id,
                    s.name as subject_name,
                    SUM(ls.duration_minutes) as total_minutes,
                    AVG(ls.focus_score) as avg_focus,
                    AVG(ls.efficiency_score) as avg_efficiency,
                    COUNT(ls.id) as session_count
                FROM learning_sessions ls
                JOIN subjects s ON ls.subject_id = s.id
                WHERE ls.student_id = ? 
                  AND DATE(ls.start_time) >= ?
                  AND ls.end_time IS NOT NULL
                GROUP BY ls.subject_id
                ORDER BY total_minutes DESC
            ''', (student_id, start_date.isoformat()))
            
            rows = cursor.fetchall()
            
            results = []
            total_time = 0
            
            for row in rows:
                minutes = row['total_minutes'] or 0
                total_time += minutes
                results.append({
                    'subject_name': row['subject_name'],
                    'total_hours': round(minutes / 60, 1),
                    'total_minutes': minutes,
                    'avg_focus_score': round(row['avg_focus'] or 0, 1),
                    'avg_efficiency_score': round(row['avg_efficiency'] or 0, 1),
                    'session_count': row['session_count']
                })
            
            return {
                'period_days': days,
                'total_hours': round(total_time / 60, 1),
                'by_subject': results
            }
    
    def get_efficiency_curve(self, student_id: int, days: int = 7) -> Dict:
        """获取效率曲线数据"""
        start_date = date.today() - timedelta(days=days)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(start_time) as study_date,
                    AVG(efficiency_score) as avg_efficiency,
                    SUM(duration_minutes) as total_minutes
                FROM learning_sessions
                WHERE student_id = ? 
                  AND DATE(start_time) >= ?
                  AND end_time IS NOT NULL
                GROUP BY DATE(start_time)
                ORDER BY study_date ASC
            ''', (student_id, start_date.isoformat()))
            
            rows = cursor.fetchall()
            
            dates = []
            efficiencies = []
            durations = []
            
            for row in rows:
                dates.append(row['study_date'])
                efficiencies.append(round(row['avg_efficiency'] or 0, 1))
                durations.append(round((row['total_minutes'] or 0) / 60, 1))
            
            return {
                'dates': dates,
                'efficiency_scores': efficiencies,
                'daily_hours': durations
            }
    
    def get_focus_summary(self, student_id: int) -> Dict:
        """获取专注力摘要"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    AVG(focus_score) as avg_focus,
                    MAX(focus_score) as max_focus,
                    MIN(focus_score) as min_focus
                FROM learning_sessions
                WHERE student_id = ? AND end_time IS NOT NULL
            ''', (student_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'average': round(row['avg_focus'] or 0, 1),
                    'best': round(row['max_focus'] or 0, 1),
                    'worst': round(row['min_focus'] or 0, 1),
                    'rating': self._get_focus_rating(row['avg_focus'] or 0)
                }
            
            return {
                'average': 0,
                'best': 0,
                'worst': 0,
                'rating': '暂无数据'
            }
    
    def _get_focus_rating(self, score: float) -> str:
        """获取专注力评级"""
        if score >= 80:
            return "优秀"
        elif score >= 60:
            return "良好"
        elif score >= 40:
            return "一般"
        else:
            return "需要改进"
