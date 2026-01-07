"""
情绪跟踪服务
管理情绪日记、压力指数分析、心理疏导建议
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from database.db_manager import DatabaseManager
from database.models import EmotionLog


class EmotionTrackingService:
    """情绪跟踪服务"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def log_emotion(self, emotion_log: EmotionLog) -> int:
        """记录情绪日记"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emotion_logs 
                (student_id, log_date, mood_score, stress_level, energy_level,
                 study_motivation, diary_content, tags, ai_suggestions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (emotion_log.student_id,
                  emotion_log.log_date.isoformat() if emotion_log.log_date else None,
                  emotion_log.mood_score, emotion_log.stress_level,
                  emotion_log.energy_level, emotion_log.study_motivation,
                  emotion_log.diary_content, emotion_log.tags, emotion_log.ai_suggestions))
            return cursor.lastrowid
    
    def get_recent_emotions(self, student_id: int, days: int = 30) -> List[EmotionLog]:
        """获取最近的情绪记录"""
        start_date = date.today() - timedelta(days=days)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM emotion_logs
                WHERE student_id = ? AND log_date >= ?
                ORDER BY log_date DESC
            ''', (student_id, start_date.isoformat()))
            
            rows = cursor.fetchall()
            return [self._row_to_emotion_log(row) for row in rows]
    
    def calculate_stress_index(self, student_id: int) -> Dict:
        """计算压力指数"""
        # 获取最近7天的情绪数据
        recent_logs = self.get_recent_emotions(student_id, days=7)
        
        if not recent_logs:
            return {
                'stress_index': 50,
                'level': '中等',
                'trend': '暂无数据',
                'recommendation': '开始记录你的情绪，帮助我们更好地了解你的状态'
            }
        
        # 计算平均压力水平
        avg_stress = sum(log.stress_level for log in recent_logs) / len(recent_logs)
        avg_mood = sum(log.mood_score for log in recent_logs) / len(recent_logs)
        avg_energy = sum(log.energy_level for log in recent_logs) / len(recent_logs)
        avg_motivation = sum(log.study_motivation for log in recent_logs) / len(recent_logs)
        
        # 综合计算压力指数 (0-100)
        # 压力高、心情差、精力低、动力低 -> 压力指数高
        stress_index = (
            avg_stress * 0.4 +  # 直接压力占40%
            (6 - avg_mood) * 0.3 +  # 心情差(反向)占30%
            (6 - avg_energy) * 0.15 +  # 精力低(反向)占15%
            (6 - avg_motivation) * 0.15  # 动力低(反向)占15%
        ) * 20  # 转换为0-100
        
        # 判断趋势
        if len(recent_logs) >= 3:
            recent_3 = recent_logs[:3]
            earlier_3 = recent_logs[3:6] if len(recent_logs) >= 6 else recent_logs[3:]
            
            if earlier_3:
                recent_avg = sum(log.stress_level for log in recent_3) / len(recent_3)
                earlier_avg = sum(log.stress_level for log in earlier_3) / len(earlier_3)
                
                if recent_avg > earlier_avg + 0.5:
                    trend = "上升 ↑"
                elif recent_avg < earlier_avg - 0.5:
                    trend = "下降 ↓"
                else:
                    trend = "稳定 →"
            else:
                trend = "数据不足"
        else:
            trend = "数据不足"
        
        # 获取建议
        level, recommendation = self._get_stress_advice(stress_index)
        
        return {
            'stress_index': round(stress_index, 1),
            'level': level,
            'trend': trend,
            'recommendation': recommendation,
            'components': {
                'avg_stress': round(avg_stress, 1),
                'avg_mood': round(avg_mood, 1),
                'avg_energy': round(avg_energy, 1),
                'avg_motivation': round(avg_motivation, 1)
            }
        }
    
    def get_emotion_trend(self, student_id: int, days: int = 14) -> Dict:
        """获取情绪趋势数据"""
        logs = self.get_recent_emotions(student_id, days=days)
        
        dates = []
        moods = []
        stresses = []
        energies = []
        motivations = []
        
        for log in reversed(logs):  # 反转以按时间正序排列
            dates.append(log.log_date.isoformat() if log.log_date else '')
            moods.append(log.mood_score)
            stresses.append(log.stress_level)
            energies.append(log.energy_level)
            motivations.append(log.study_motivation)
        
        return {
            'dates': dates,
            'mood_scores': moods,
            'stress_levels': stresses,
            'energy_levels': energies,
            'motivation_levels': motivations
        }
    
    def generate_ai_suggestions(self, student_id: int, emotion_log: EmotionLog) -> str:
        """生成AI心理疏导建议"""
        suggestions = []
        
        # 基于压力水平
        if emotion_log.stress_level >= 4:
            suggestions.append("💆 你的压力值较高，建议每天安排15-30分钟放松时间，可以尝试深呼吸、听音乐或散步。")
        
        # 基于心情
        if emotion_log.mood_score <= 2:
            suggestions.append("🌈 心情低落时，试着做一些你喜欢的事情。记住，任何困难都是暂时的，你并不孤单。")
        
        # 基于精力
        if emotion_log.energy_level <= 2:
            suggestions.append("⚡ 精力不足会影响学习效率。保证充足睡眠(7-8小时)，适当运动，会让你更有活力！")
        
        # 基于学习动力
        if emotion_log.study_motivation <= 2:
            suggestions.append("🎯 学习动力低落时，可以设定小目标，完成后给自己小奖励。享受每一点进步！")
        
        # 综合评估
        if emotion_log.stress_level >= 4 and emotion_log.mood_score <= 2:
            suggestions.append("⚠️ 注意：你最近可能压力较大且心情不佳。如果持续感到困扰，建议找老师、家长或心理咨询师谈谈。")
        
        if not suggestions:
            suggestions.append("✨ 你的状态看起来不错！继续保持积极的心态，相信自己！")
        
        return " ".join(suggestions)
    
    def _get_stress_advice(self, stress_index: float) -> tuple:
        """根据压力指数获取建议"""
        if stress_index >= 75:
            return "很高", "⚠️ 强烈建议：调整学习节奏，增加休息时间，必要时寻求专业心理支持。"
        elif stress_index >= 60:
            return "较高", "💡 建议：适当减轻学习负担，多与朋友家人交流，保持运动习惯。"
        elif stress_index >= 40:
            return "中等", "😊 状态正常，继续保持学习与休息的平衡。"
        elif stress_index >= 25:
            return "较低", "🌟 心态很好！保持积极乐观，享受学习过程。"
        else:
            return "很低", "✨ 状态非常棒！你的自我调节能力很强。"
    
    def _row_to_emotion_log(self, row) -> EmotionLog:
        """数据库行转EmotionLog对象"""
        return EmotionLog(
            id=row['id'],
            student_id=row['student_id'],
            log_date=date.fromisoformat(row['log_date']) if row['log_date'] else None,
            mood_score=row['mood_score'],
            stress_level=row['stress_level'],
            energy_level=row['energy_level'],
            study_motivation=row['study_motivation'],
            diary_content=row['diary_content'],
            tags=row['tags'],
            ai_suggestions=row['ai_suggestions'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
