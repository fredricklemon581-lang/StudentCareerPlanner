"""
目标管理服务
处理学习目标创建、跟踪、成就解锁
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from database.db_manager import DatabaseManager
from database.models import Goal, Achievement


class GoalManagementService:
    """目标管理服务类"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_goal(self, goal: Goal) -> int:
        """创建学习目标"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO goals 
                (student_id, goal_type, title, description, target_value, current_value,
                 start_date, deadline, status, progress, subject_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (goal.student_id, goal.goal_type, goal.title, goal.description,
                  goal.target_value, goal.current_value,
                  goal.start_date.isoformat() if goal.start_date else None,
                  goal.deadline.isoformat() if goal.deadline else None,
                  goal.status, goal.progress, goal.subject_id))
            return cursor.lastrowid
    
    def get_student_goals(self, student_id: int, status: Optional[str] = None) -> List[Goal]:
        """获取学生的目标列表"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('''
                    SELECT * FROM goals 
                    WHERE student_id = ? AND status = ?
                    ORDER BY deadline ASC, created_at DESC
                ''', (student_id, status))
            else:
                cursor.execute('''
                    SELECT * FROM goals 
                    WHERE student_id = ?
                    ORDER BY deadline ASC, created_at DESC
                ''', (student_id,))
            
            rows = cursor.fetchall()
            return [self._row_to_goal(row) for row in rows]
    
    def update_goal_progress(self, goal_id: int, current_value: float) -> bool:
        """更新目标进度"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取目标信息
            cursor.execute('SELECT * FROM goals WHERE id = ?', (goal_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            goal = self._row_to_goal(row)
            
            # 计算进度百分比
            if goal.target_value > 0:
                progress = min(100, (current_value / goal.target_value) * 100)
            else:
                progress = 0
            
            # 判断是否已完成
            status = goal.status
            completed_at = None
            if progress >= 100 and status != "已完成":
                status = "已完成"
                completed_at = datetime.now()
                # 解锁成就
                self._unlock_achievement(goal.student_id, goal)
            
            # 更新数据库
            cursor.execute('''
                UPDATE goals 
                SET current_value = ?, progress = ?, status = ?, completed_at = ?
                WHERE id = ?
            ''', (current_value, progress, status,
                  completed_at.isoformat() if completed_at else None, goal_id))
            
            return cursor.rowcount > 0
    
    def _unlock_achievement(self, student_id: int, goal: Goal):
        """解锁成就"""
        achievement = Achievement(
            student_id=student_id,
            achievement_type="目标达成",
            title=f"🎯 完成目标: {goal.title}",
            description=f"恭喜你完成了\"{goal.title}\"目标！",
            icon="🏆",
            unlock_date=datetime.now(),
            related_goal_id=goal.id
        )
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO achievements 
                (student_id, achievement_type, title, description, icon, unlock_date, related_goal_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (achievement.student_id, achievement.achievement_type, achievement.title,
                  achievement.description, achievement.icon,
                  achievement.unlock_date.isoformat(), achievement.related_goal_id))
    
    def get_student_achievements(self, student_id: int, limit: int = 10) -> List[Achievement]:
        """获取学生的成就列表"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM achievements 
                WHERE student_id = ?
                ORDER BY unlock_date DESC
                LIMIT ?
            ''', (student_id, limit))
            
            rows = cursor.fetchall()
            return [self._row_to_achievement(row) for row in rows]
    
    def recommend_goals(self, student_id: int) -> List[dict]:
        """AI推荐目标"""
        # 这里可以基于学生的成绩情况智能推荐目标
        recommendations = []
        
        # 示例推荐（实际应该基于成绩分析）
        recommendations.append({
            'title': '数学提升计划',
            'description': '在下次月考中数学成绩提升10分',
            'goal_type': '成绩目标',
            'target_value': 90,
            'deadline_days': 30
        })
        
        recommendations.append({
            'title': '英语词汇突破',
            'description': '每天背诵20个单词，一个月掌握600词汇',
            'goal_type': '学习习惯',
            'target_value': 600,
            'deadline_days': 30
        })
        
        return recommendations
    
    def _row_to_goal(self, row) -> Goal:
        """数据库行转Goal对象"""
        return Goal(
            id=row['id'],
            student_id=row['student_id'],
            goal_type=row['goal_type'],
            title=row['title'],
            description=row['description'],
            target_value=row['target_value'],
            current_value=row['current_value'],
            start_date=date.fromisoformat(row['start_date']) if row['start_date'] else None,
            deadline=date.fromisoformat(row['deadline']) if row['deadline'] else None,
            status=row['status'],
            progress=row['progress'],
            subject_id=row['subject_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None
        )
    
    def _row_to_achievement(self, row) -> Achievement:
        """数据库行转Achievement对象"""
        return Achievement(
            id=row['id'],
            student_id=row['student_id'],
            achievement_type=row['achievement_type'],
            title=row['title'],
            description=row['description'],
            icon=row['icon'],
            unlock_date=datetime.fromisoformat(row['unlock_date']) if row['unlock_date'] else None,
            related_goal_id=row['related_goal_id']
        )
