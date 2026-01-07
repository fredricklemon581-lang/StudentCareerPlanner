# -*- coding: utf-8 -*-
"""
薄弱点分析服务 - 识别学生的薄弱知识点
"""
from typing import List, Dict, Tuple
from database.db_manager import DatabaseManager


class WeaknessAnalysisService:
    """学生薄弱点分析服务"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def analyze_student_weaknesses(self, student_id: int, subject_id: int = None) -> List[Dict]:
        """
        分析学生的薄弱知识点
        
        Args:
            student_id: 学生ID
            subject_id: 科目ID（可选，不指定则分析所有科目）
        
        Returns:
            薄弱知识点列表，按掌握率从低到高排序
            [{
                'knowledge_point_id': int,
                'knowledge_point_name': str,
                'subject_name': str,
                'mastery_rate': float,
                'total_attempts': int,
                'correct_attempts': int,
                'level': int (难度等级)
            }]
        """
        # 获取学生所有答题记录
        answers = self.db.get_student_all_answers(student_id)
        
        if not answers:
            return []
        
        # 统计每个知识点的表现
        kp_performance = {}
        
        for answer in answers:
            # 获取这道题关联的知识点
            kps = self.db.get_question_knowledge_points(answer.question_id)
            
            for kp in kps:
                # 如果指定了科目，只统计该科目的知识点
                if subject_id and kp.subject_id != subject_id:
                    continue
                
                if kp.id not in kp_performance:
                    kp_performance[kp.id] = {
                        'knowledge_point_id': kp.id,
                        'knowledge_point_name': kp.name,
                        'subject_id': kp.subject_id,
                        'level': kp.level,
                        'total_attempts': 0,
                        'correct_attempts': 0
                    }
                
                kp_performance[kp.id]['total_attempts'] += 1
                if answer.is_correct:
                    kp_performance[kp.id]['correct_attempts'] += 1
        
        # 计算掌握率
        weaknesses = []
        for kp_data in kp_performance.values():
            if kp_data['total_attempts'] == 0:
                continue
            
            mastery_rate = kp_data['correct_attempts'] / kp_data['total_attempts']
            kp_data['mastery_rate'] = mastery_rate
            
            # 掌握率低于65%视为薄弱
            if mastery_rate < 0.65:
                # 获取科目名称
                subject = self.db.get_all_subjects()
                subject_name = next((s.name for s in subject if s.id == kp_data['subject_id']), '未知')
                kp_data['subject_name'] = subject_name
                
                weaknesses.append(kp_data)
        
        # 按掌握率排序（从低到高）
        weaknesses.sort(key=lambda x: x['mastery_rate'])
        
        return weaknesses
    
    def get_knowledge_point_mastery(self, student_id: int) -> Dict[int, float]:
        """
        获取学生对所有知识点的掌握度
        
        Returns:
            {knowledge_point_id: mastery_rate}
        """
        answers = self.db.get_student_all_answers(student_id)
        
        kp_stats = {}
        for answer in answers:
            kps = self.db.get_question_knowledge_points(answer.question_id)
            
            for kp in kps:
                if kp.id not in kp_stats:
                    kp_stats[kp.id] = {'correct': 0, 'total': 0}
                
                kp_stats[kp.id]['total'] += 1
                if answer.is_correct:
                    kp_stats[kp.id]['correct'] += 1
        
        # 计算掌握度
        mastery = {}
        for kp_id, stats in kp_stats.items():
            if stats['total'] > 0:
                mastery[kp_id] = stats['correct'] / stats['total']
            else:
                mastery[kp_id] = 0.5  # 默认值
        
        return mastery
    
    def get_improvement_suggestions(self, student_id: int, top_n: int = 5) -> List[str]:
        """
        生成改进建议
        
        Args:
            student_id: 学生ID
            top_n: 返回前N个薄弱点的建议
        
        Returns:
            建议列表
        """
        weaknesses = self.analyze_student_weaknesses(student_id)
        
        suggestions = []
        for i, weak in enumerate(weaknesses[:top_n], 1):
            mastery_pct = weak['mastery_rate'] * 100
            suggestion = (
                f"{i}. 加强【{weak['subject_name']}-{weak['knowledge_point_name']}】的练习 "
                f"(当前掌握率: {mastery_pct:.1f}%, 已练习{weak['total_attempts']}题)"
            )
            suggestions.append(suggestion)
        
        return suggestions


class KnowledgePointCoverageAnalyzer:
    """知识点覆盖度分析器"""
    
    @staticmethod
    def calculate_coverage(questions: List, all_kps: List) -> Dict:
        """
        计算题目集的知识点覆盖度
        
        Args:
            questions: Question对象列表
            all_kps: 该科目所有知识点列表
        
        Returns:
            {
                'covered_count': int,  # 已覆盖知识点数
                'total_count': int,    # 总知识点数
                'coverage_rate': float, # 覆盖率
                'covered_kps': List[int], # 已覆盖的知识点ID
                'uncovered_kps': List[int] # 未覆盖的知识点ID
            }
        """
        from database.db_manager import DatabaseManager
        import config
        
        # 这里简化处理，实际应传入db实例
        db = DatabaseManager(config.DATABASE_PATH)
        
        # 收集所有被使用的知识点
        covered_kp_ids = set()
        for q in questions:
            kps = db.get_question_knowledge_points(q.id)
            for kp in kps:
                covered_kp_ids.add(kp.id)
        
        all_kp_ids = set(kp.id for kp in all_kps)
        uncovered_kp_ids = all_kp_ids - covered_kp_ids
        
        coverage_rate = len(covered_kp_ids) / len(all_kp_ids) if all_kp_ids else 0
        
        return {
            'covered_count': len(covered_kp_ids),
            'total_count': len(all_kp_ids),
            'coverage_rate': coverage_rate,
            'covered_kps': list(covered_kp_ids),
            'uncovered_kps': list(uncovered_kp_ids)
        }
