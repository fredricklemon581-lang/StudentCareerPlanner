# -*- coding: utf-8 -*-
"""
智能组卷引擎 - AI驱动的针对性试卷生成
"""
import random
from typing import List, Dict, Tuple
from database.db_manager import DatabaseManager
from database.models import Question
from services.weakness_analysis_service import WeaknessAnalysisService


class IntelligentExamGenerator:
    """智能组卷引擎"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.weakness_analyzer = WeaknessAnalysisService(db)
    
    def generate_targeted_exam(
        self,
        student_id: int,
        subject_id: int,
        total_score: int = 150,
        focus_on_weaknesses: bool = True,
        difficulty_level: str = 'medium',
        question_distribution: Dict = None
    ) -> Dict:
        """
        为学生生成针对性试卷
        
        Args:
            student_id: 学生ID
            subject_id: 科目ID
            total_score: 试卷总分
            focus_on_weaknesses: 是否重点考察薄弱点（70%题目来自薄弱知识点）
            difficulty_level: 难度等级 'easy'/'medium'/'hard'
            question_distribution: 自定义题型分布
        
        Returns:
            {
                'questions': List[Question],
                'total_score': int,
                'difficulty_stats': Dict,
                'weakness_coverage': Dict,
                'recommendations': List[str]
            }
        """
        # 1. 分析学生薄弱点
        weaknesses = self.weakness_analyzer.analyze_student_weaknesses(student_id, subject_id)
        weak_kp_ids = [w['knowledge_point_id'] for w in weaknesses[:15]]  # 取前15个薄弱点
        
        # 2. 确定题型分布
        if question_distribution is None:
            question_distribution = self._get_default_distribution(subject_id, total_score)
        
        # 3. 设置难度目标
        difficulty_target = self._get_difficulty_target(difficulty_level)
        
        # 4. 开始选题
        selected_questions = []
        used_q_ids = []
        
        for q_type, config in question_distribution.items():
            count = config['count']
            score_each = config['score_each']
            
            for i in range(count):
                # 确定本题的难度目标
                q_difficulty = self._get_question_difficulty_target(
                    i, count, difficulty_target
                )
                
                # 确定是否从薄弱点选题
                use_weakness = focus_on_weaknesses and len(weak_kp_ids) > 0 and random.random() < 0.7
                
                # 选择题目
                question = self._select_question(
                    subject_id=subject_id,
                    question_type=q_type,
                    target_kp_ids=weak_kp_ids if use_weakness else None,
                    difficulty_range=(q_difficulty - 0.15, q_difficulty + 0.15),
                    exclude_ids=used_q_ids
                )
                
                if question:
                    selected_questions.append(question)
                    used_q_ids.append(question.id)
        
        # 5. 计算统计信息
        actual_total = sum(q.score for q in selected_questions)
        difficulty_stats = self._calculate_difficulty_stats(selected_questions)
        weakness_coverage = self._calculate_weakness_coverage(selected_questions, weak_kp_ids)
        recommendations = self._generate_recommendations(
            selected_questions, weaknesses, weakness_coverage
        )
        
        return {
            'questions': selected_questions,
            'total_score': actual_total,
            'actual_count': len(selected_questions),
            'difficulty_stats': difficulty_stats,
            'weakness_coverage': weakness_coverage,
            'recommendations': recommendations,
            'weaknesses_analyzed': weaknesses[:10]  # 返回前10个薄弱点供参考
        }
    
    def _get_default_distribution(self, subject_id: int, total_score: int) -> Dict:
        """获取默认题型分布"""
        # 根据科目和总分确定分布
        subjects = self.db.get_all_subjects()
        subject_name = next((s.name for s in subjects if s.id == subject_id), '')
        
        if total_score == 150:  # 主科
            return {
                '选择题': {'count': 12, 'score_each': 4},
                '填空题': {'count': 4, 'score_each': 5},
                '解答题': {'count': 6, 'score_each': 15}
            }
        elif total_score == 100:  # 副科
            return {
                '选择题': {'count': 10, 'score_each': 4},
                '解答题': {'count': 5, 'score_each': 12}
            }
        else:
            # 通用分布
            return {
                '选择题': {'count': 10, 'score_each': 4},
                '填空题': {'count': 5, 'score_each': 5},
                '解答题': {'count': 5, 'score_each': 10}
            }
    
    def _get_difficulty_target(self, level: str) -> float:
        """获取难度目标值"""
        levels = {
            'easy': 0.3,    # 简单
            'medium': 0.5,  # 中等
            'hard': 0.7     # 困难
        }
        return levels.get(level, 0.5)
    
    def _get_question_difficulty_target(self, index: int, total: int, base_difficulty: float) -> float:
        """
        获取单题难度目标（梯度分布）
        前面的题简单，后面逐渐变难
        """
        progress = index / total if total > 0 else 0
        # 难度范围：base_difficulty ± 0.2，按进度递增
        min_diff = max(0.1, base_difficulty - 0.2)
        max_diff = min(0.9, base_difficulty + 0.2)
        
        return min_diff + (max_diff - min_diff) * progress
    
    def _select_question(
        self,
        subject_id: int,
        question_type: str,
        target_kp_ids: List[int] = None,
        difficulty_range: Tuple[float, float] = (0.3, 0.7),
        exclude_ids: List[int] = None
    ) -> Question:
        """
        选择一道合适的题目
        """
        filters = {
            'subject_id': subject_id,
            'question_type': question_type,
            'min_difficulty': difficulty_range[0],
            'max_difficulty': difficulty_range[1],
            'exclude_ids': exclude_ids or []
        }
        
        if target_kp_ids:
            # 优先选择包含目标知识点的题目
            filters['knowledge_point_ids'] = target_kp_ids
            questions = self.db.search_questions(filters)
            
            if questions:
                return random.choice(questions)
            
            # 如果找不到，放宽条件（不限知识点）
            del filters['knowledge_point_ids']
        
        questions = self.db.search_questions(filters)
        
        if questions:
            return random.choice(questions)
        
        return None
    
    def _calculate_difficulty_stats(self, questions: List[Question]) -> Dict:
        """计算试卷难度统计"""
        if not questions:
            return {'average': 0, 'distribution': {}}
        
        difficulties = [q.difficulty for q in questions]
        avg_difficulty = sum(difficulties) / len(difficulties)
        
        # 统计分布
        easy_count = sum(1 for d in difficulties if d < 0.4)
        medium_count = sum(1 for d in difficulties if 0.4 <= d < 0.7)
        hard_count = sum(1 for d in difficulties if d >= 0.7)
        
        return {
            'average': round(avg_difficulty, 2),
            'distribution': {
                '简单': easy_count,
                '中等': medium_count,
                '困难': hard_count
            }
        }
    
    def _calculate_weakness_coverage(self, questions: List[Question], weak_kp_ids: List[int]) -> Dict:
        """计算薄弱点覆盖情况"""
        if not weak_kp_ids:
            return {'covered_count': 0, 'total_count': 0, 'coverage_rate': 0}
        
        covered_weak_kps = set()
        for q in questions:
            kps = self.db.get_question_knowledge_points(q.id)
            for kp in kps:
                if kp.id in weak_kp_ids:
                    covered_weak_kps.add(kp.id)
        
        coverage_rate = len(covered_weak_kps) / len(weak_kp_ids) if weak_kp_ids else 0
        
        return {
            'covered_count': len(covered_weak_kps),
            'total_count': len(weak_kp_ids),
            'coverage_rate': round(coverage_rate, 2)
        }
    
    def _generate_recommendations(
        self,
        questions: List[Question],
        weaknesses: List[Dict],
        coverage: Dict
    ) -> List[str]:
        """生成组卷建议"""
        recommendations = []
        
        # 检查题目数量
        if len(questions) == 0:
            recommendations.append("⚠️ 未能成功组卷，题库可能不足，请补充题目。")
            return recommendations
        
        # 检查薄弱点覆盖
        if coverage['coverage_rate'] < 0.5 and weaknesses:
            recommendations.append(
                f"💡 试卷仅覆盖了{coverage['covered_count']}/{coverage['total_count']}个薄弱知识点，"
                f"建议补充相关题目。"
            )
        elif coverage['coverage_rate'] >= 0.7:
            recommendations.append(
                f"✅ 试卷已覆盖{coverage['covered_count']}个薄弱知识点，针对性强。"
            )
        
        # 检查难度分布
        diff_stats = self._calculate_difficulty_stats(questions)
        if diff_stats['distribution']['简单'] > len(questions) * 0.5:
            recommendations.append("💡 试卷整体偏简单，可适当增加难度。")
        elif diff_stats['distribution']['困难'] > len(questions) * 0.5:
            recommendations.append("💡 试卷整体偏难，建议增加简单题增强信心。")
        
        return recommendations


# 快速工厂函数
def create_generator(db: DatabaseManager) -> IntelligentExamGenerator:
    """创建智能组卷引擎实例"""
    return IntelligentExamGenerator(db)
