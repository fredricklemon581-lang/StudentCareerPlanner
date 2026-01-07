# -*- coding: utf-8 -*-
"""
题目生成器 - 为每场考试生成题目
"""
import random
from typing import List, Tuple, Dict

# 题型配置
QUESTION_TYPES = {
    '选择题': {'min_score': 3, 'max_score': 5},
    '填空题': {'min_score': 5, 'max_score': 8},
    '解答题': {'min_score': 10, 'max_score': 20},
    '作文': {'min_score': 30, 'max_score': 60},
}

# 各科目题目配置
SUBJECT_QUESTION_CONFIG = {
    '语文': {
        'total_score': 150,
        'questions': [
            ('选择题', 8, 4),
            ('填空题', 5, 5),
            ('解答题', 5, 12),
            ('作文', 2, 40),
        ]
    },
    '数学': {
        'total_score': 150,
        'questions': [
            ('选择题', 12, 4),
            ('填空题', 4, 5),
            ('解答题', 6, 14),
        ]
    },
    '英语': {
        'total_score': 150,
        'questions': [
            ('选择题', 20, 3),
            ('填空题', 5, 6),
            ('作文', 2, 30),
        ]
    },
    '物理': {
        'total_score': 100,
        'questions': [
            ('选择题', 10, 4),
            ('解答题', 5, 12),
        ]
    },
    '化学': {
        'total_score': 100,
        'questions': [
            ('选择题', 10, 4),
            ('解答题', 5, 12),
        ]
    },
    '生物': {
        'total_score': 100,
        'questions': [
            ('选择题', 10, 4),
            ('解答题', 5, 12),
        ]
    },
    '政治': {
        'total_score': 100,
        'questions': [
            ('选择题', 12, 4),
            ('解答题', 4, 13),
        ]
    },
    '历史': {
        'total_score': 100,
        'questions': [
            ('选择题', 12, 4),
            ('解答题', 4, 13),
        ]
    },
    '地理': {
        'total_score': 100,
        'questions': [
            ('选择题', 12, 4),
            ('解答题', 4, 13),
        ]
    },
}


def generate_questions_for_exam(
    subject_name: str,
    available_kps: List[Tuple[int, str, int]]  # (kp_id, kp_name, difficulty)
) -> List[Dict]:
    """
    为指定科目的考试生成题目
    
    Args:
        subject_name: 科目名称
        available_kps: 可用的知识点列表 (id, name, difficulty)
    
    Returns:
        题目列表，每个题目包含：
        {
            'number': 题号,
            'type': 题型,
            'score': 分值,
            'difficulty': 难度(1-5),
            'knowledge_points': [关联的知识点ID]
        }
    """
    config = SUBJECT_QUESTION_CONFIG.get(subject_name)
    if not config:
        return []
    
    questions = []
    question_number = 1
    
    for question_type, count, base_score in config['questions']:
        for i in range(count):
            # 随机选择1-3个知识点
            num_kps = random.choice([1, 1, 2, 2, 3])  # 更倾向于1-2个
            selected_kps = random.sample(available_kps, min(num_kps, len(available_kps)))
            
            # 计算题目难度（基于关联知识点的平均难度）
            avg_difficulty = sum(kp[2] for kp in selected_kps) / len(selected_kps)
            
            # 分数可能有小幅波动
            score = base_score + random.choice([-1, 0, 0, 1])
            score = max(1, score)
            
            question = {
                'number': question_number,
                'type': question_type,
                'score': score,
                'difficulty': round(avg_difficulty),
                'knowledge_points': [kp[0] for kp in selected_kps]
            }
            
            questions.append(question)
            question_number += 1
    
    return questions


def calculate_student_score_for_question(
    student_ability: float,  # 学生能力 0-1
    kp_mastery: Dict[int, float],  # 知识点掌握度 {kp_id: mastery}
    question: Dict,  # 题目信息
    randomness: float = 0.15  # 随机波动幅度
) -> Tuple[float, bool]:
    """
    计算学生在某道题的得分
    
    Returns:
        (得分, 是否完全正确)
    """
    # 计算该学生对这道题相关知识点的平均掌握度
    kp_ids = question['knowledge_points']
    avg_mastery = sum(kp_mastery.get(kp_id, 0.5) for kp_id in kp_ids) / len(kp_ids)
    
    # 基础正确率 = 学生能力 * 知识掌握度 * (1 - 难度惩罚)
    difficulty_factor = 1.0 - (question['difficulty'] - 1) * 0.1
    base_correctness = student_ability * avg_mastery * difficulty_factor
    
    # 添加随机波动
    actual_correctness = base_correctness + random.gauss(0, randomness)
    actual_correctness = max(0, min(1, actual_correctness))
    
    # 根据题型计算得分
    full_score = question['score']
    question_type = question['type']
    
    if question_type in ['选择题', '填空题']:
        # 客观题：要么全对要么全错
        if actual_correctness > 0.6:  # 60%的把握就能答对
            return full_score, True
        else:
            return 0.0, False
    
    elif question_type in ['解答题', '作文']:
        # 主观题：可以得部分分
        # 即使不会，也可能得到20-40%的分数（写了一些相关内容）
        min_score_rate = 0.2 if actual_correctness > 0.3 else 0
        score_rate = min_score_rate + actual_correctness * (1 - min_score_rate)
        
        obtained = full_score * score_rate
        
        # 解答题的给分通常是整分或半分
        obtained = round(obtained * 2) / 2
        
        is_correct = obtained >= full_score * 0.8
        return obtained, is_correct
    
    return 0.0, False


if __name__ == '__main__':
    # 测试
    print("题目生成器测试")
    print("=" * 60)
    
    # 模拟知识点
    test_kps = [(i, f"知识点{i}", random.randint(1, 5)) for i in range(1, 21)]
    
    for subject in ['语文', '数学', '英语']:
        questions = generate_questions_for_exam(subject, test_kps)
        total = sum(q['score'] for q in questions)
        print(f"\n{subject}:")
        print(f"  题目数: {len(questions)}")
        print(f"  总分: {total}")
        print(f"  题型分布:")
        type_count = {}
        for q in questions:
            type_count[q['type']] = type_count.get(q['type'], 0) + 1
        for qtype, count in type_count.items():
            print(f"    {qtype}: {count}题")
