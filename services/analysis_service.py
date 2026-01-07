"""
数据分析服务
提供成绩趋势分析、强弱科识别、知识点掌握分析、学习潜力评估
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import date
import numpy as np

from database.db_manager import DatabaseManager
from database.models import Student, Subject, ExamScore, Exam


@dataclass
class SubjectAnalysis:
    """学科分析结果"""
    subject_name: str
    subject_id: int
    average_score: float
    average_score_rate: float
    score_trend: str  # 上升/下降/稳定
    trend_slope: float  # 趋势斜率
    best_score: float
    worst_score: float
    exam_count: int
    is_strong: bool  # 是否为优势学科
    is_weak: bool  # 是否为劣势学科


@dataclass
class KnowledgeAnalysis:
    """知识点分析结果"""
    knowledge_point: str
    correct_rate: float
    question_count: int
    is_mastered: bool  # 是否已掌握
    is_weak: bool  # 是否为薄弱点


@dataclass
class PotentialAnalysis:
    """学习潜力分析结果"""
    overall_trend: str  # 整体趋势
    growth_rate: float  # 增长率
    stability_score: float  # 稳定性评分 (0-1)
    improvement_subjects: List[str]  # 进步学科
    declining_subjects: List[str]  # 退步学科
    potential_rating: str  # 潜力评级: 高/中/低


@dataclass
class StudentAnalysisReport:
    """学生综合分析报告"""
    student_id: int
    student_name: str
    grade: str
    subject_analyses: List[SubjectAnalysis]
    strong_subjects: List[str]
    weak_subjects: List[str]
    knowledge_weaknesses: List[str]
    potential_analysis: PotentialAnalysis
    recommendations: List[str]


class AnalysisService:
    """数据分析服务"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def analyze_student(self, student_id: int) -> Optional[StudentAnalysisReport]:
        """
        对学生进行综合分析
        
        Args:
            student_id: 学生数据库ID
            
        Returns:
            StudentAnalysisReport 或 None
        """
        student = self.db.get_student_by_id(student_id)
        if not student:
            return None
        
        # 获取所有学科
        subjects = self.db.get_all_subjects()
        
        # 分析各学科
        subject_analyses = []
        for subject in subjects:
            analysis = self._analyze_subject(student_id, subject)
            if analysis:
                subject_analyses.append(analysis)
        
        # 识别强弱科
        strong_subjects = [a.subject_name for a in subject_analyses if a.is_strong]
        weak_subjects = [a.subject_name for a in subject_analyses if a.is_weak]
        
        # 分析知识点薄弱项
        knowledge_weaknesses = self._get_knowledge_weaknesses(student_id)
        
        # 学习潜力分析
        potential_analysis = self._analyze_potential(subject_analyses)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            subject_analyses, knowledge_weaknesses, potential_analysis
        )
        
        return StudentAnalysisReport(
            student_id=student_id,
            student_name=student.name,
            grade=student.grade,
            subject_analyses=subject_analyses,
            strong_subjects=strong_subjects,
            weak_subjects=weak_subjects,
            knowledge_weaknesses=knowledge_weaknesses,
            potential_analysis=potential_analysis,
            recommendations=recommendations
        )
    
    def _analyze_subject(self, student_id: int, subject: Subject) -> Optional[SubjectAnalysis]:
        """分析单个学科"""
        scores = self.db.get_student_scores_by_subject(student_id, subject.id)
        
        if not scores:
            return None
        
        # 提取分数和得分率
        score_values = [s[0].score for s in scores]
        score_rates = [s[0].score_rate for s in scores]
        
        # 计算基本统计
        avg_score = np.mean(score_values)
        avg_rate = np.mean(score_rates)
        best_score = max(score_values)
        worst_score = min(score_values)
        
        # 计算趋势
        if len(score_rates) >= 2:
            x = np.arange(len(score_rates))
            slope, _ = np.polyfit(x, score_rates, 1)
            
            if slope > 0.02:
                trend = "上升"
            elif slope < -0.02:
                trend = "下降"
            else:
                trend = "稳定"
        else:
            slope = 0
            trend = "稳定"
        
        # 判断强弱科
        is_strong = avg_rate >= 0.85
        is_weak = avg_rate < 0.60
        
        return SubjectAnalysis(
            subject_name=subject.name,
            subject_id=subject.id,
            average_score=round(avg_score, 1),
            average_score_rate=round(avg_rate, 3),
            score_trend=trend,
            trend_slope=round(slope, 4),
            best_score=best_score,
            worst_score=worst_score,
            exam_count=len(scores),
            is_strong=is_strong,
            is_weak=is_weak
        )
    
    def _get_knowledge_weaknesses(self, student_id: int) -> List[str]:
        """获取知识点薄弱项（通过分析每道题的得分）"""
        # 从数据库获取知识点掌握情况
        mastery_data = self.db.get_knowledge_point_mastery(student_id)
        
        # 筛选薄弱知识点（得分率低于60%）
        weaknesses = []
        for item in mastery_data:
            if item['is_weak'] and item['total_questions'] >= 2:
                weaknesses.append(f"{item['subject']}-{item['knowledge_point']} ({item['mastery_rate']*100:.0f}%)")
        
        # 按得分率排序，返回最薄弱的
        weaknesses.sort(key=lambda x: float(x.split('(')[1].rstrip('%)')) if '(' in x else 0)
        
        return weaknesses[:10]
    
    def _analyze_potential(self, subject_analyses: List[SubjectAnalysis]) -> PotentialAnalysis:
        """分析学习潜力"""
        if not subject_analyses:
            return PotentialAnalysis(
                overall_trend="未知",
                growth_rate=0,
                stability_score=0,
                improvement_subjects=[],
                declining_subjects=[],
                potential_rating="未知"
            )
        
        # 计算整体趋势
        slopes = [a.trend_slope for a in subject_analyses]
        avg_slope = np.mean(slopes)
        
        if avg_slope > 0.02:
            overall_trend = "上升"
        elif avg_slope < -0.02:
            overall_trend = "下降"
        else:
            overall_trend = "稳定"
        
        # 计算增长率
        growth_rate = avg_slope * 100  # 转换为百分比
        
        # 计算稳定性
        score_rates = [a.average_score_rate for a in subject_analyses]
        stability_score = 1 - np.std(score_rates) if len(score_rates) > 1 else 0.5
        stability_score = max(0, min(1, stability_score))
        
        # 识别进步和退步学科
        improvement_subjects = [a.subject_name for a in subject_analyses if a.trend_slope > 0.02]
        declining_subjects = [a.subject_name for a in subject_analyses if a.trend_slope < -0.02]
        
        # 评估潜力
        avg_rate = np.mean(score_rates)
        if avg_slope > 0.03 or (avg_rate < 0.7 and avg_slope > 0):
            potential_rating = "高"
        elif avg_slope > 0 or avg_rate > 0.8:
            potential_rating = "中"
        else:
            potential_rating = "低"
        
        return PotentialAnalysis(
            overall_trend=overall_trend,
            growth_rate=round(growth_rate, 2),
            stability_score=round(stability_score, 2),
            improvement_subjects=improvement_subjects,
            declining_subjects=declining_subjects,
            potential_rating=potential_rating
        )
    
    def _generate_recommendations(
        self,
        subject_analyses: List[SubjectAnalysis],
        knowledge_weaknesses: List[str],
        potential: PotentialAnalysis
    ) -> List[str]:
        """生成学习建议"""
        recommendations = []
        
        # 基于弱势学科的建议
        weak_subjects = [a for a in subject_analyses if a.is_weak]
        for subject in weak_subjects:
            if subject.score_trend == "上升":
                recommendations.append(
                    f"📈 {subject.subject_name}虽然是薄弱学科，但呈上升趋势，继续保持当前学习方法"
                )
            else:
                recommendations.append(
                    f"⚠️ {subject.subject_name}需要重点加强，建议增加学习时间和练习量"
                )
        
        # 基于优势学科的建议
        strong_subjects = [a for a in subject_analyses if a.is_strong]
        for subject in strong_subjects:
            if subject.score_trend == "下降":
                recommendations.append(
                    f"📉 {subject.subject_name}成绩有所下滑，需要注意保持"
                )
        
        # 基于潜力分析的建议
        if potential.potential_rating == "高":
            recommendations.append("🌟 学习潜力很高，保持积极的学习态度")
        
        if potential.declining_subjects:
            recommendations.append(
                f"📚 {', '.join(potential.declining_subjects)} 出现退步趋势，建议调整学习策略"
            )
        
        # 知识点相关建议
        if knowledge_weaknesses:
            recommendations.append(
                f"🎯 建议重点复习以下知识点: {', '.join(knowledge_weaknesses[:5])}"
            )
        
        return recommendations
    
    def get_subject_trend_data(self, student_id: int, subject_id: int) -> Dict:
        """
        获取某学科的趋势数据，用于绑制图表
        
        Returns:
            {
                'dates': [日期列表],
                'scores': [分数列表],
                'score_rates': [得分率列表],
                'exam_names': [考试名称列表]
            }
        """
        scores = self.db.get_student_scores_by_subject(student_id, subject_id)
        
        if not scores:
            return {'dates': [], 'scores': [], 'score_rates': [], 'exam_names': []}
        
        # 按日期排序
        sorted_scores = sorted(scores, key=lambda x: x[1].exam_date or date.min)
        
        return {
            'dates': [s[1].exam_date.isoformat() if s[1].exam_date else '' for s in sorted_scores],
            'scores': [s[0].score for s in sorted_scores],
            'score_rates': [s[0].score_rate for s in sorted_scores],
            'exam_names': [s[1].name for s in sorted_scores]
        }
    
    def get_all_subjects_comparison(self, student_id: int) -> Dict:
        """
        获取所有学科对比数据，用于雷达图
        
        Returns:
            {
                'subjects': [学科名称列表],
                'scores': [平均得分率列表]
            }
        """
        subjects = self.db.get_all_subjects()
        result = {'subjects': [], 'scores': []}
        
        for subject in subjects:
            scores = self.db.get_student_scores_by_subject(student_id, subject.id)
            if scores:
                avg_rate = np.mean([s[0].score_rate for s in scores])
                result['subjects'].append(subject.name)
                result['scores'].append(round(avg_rate * 100, 1))
        
        return result
    
    def generate_student_summary(self, student_id: int) -> str:
        """
        生成学生成绩摘要文本，用于AI对话上下文
        综合成绩数据和知识点掌握情况
        """
        report = self.analyze_student(student_id)
        if not report:
            return "暂无成绩数据"
        
        lines = []
        lines.append(f"学生姓名: {report.student_name}")
        lines.append(f"年级: {report.grade}")
        lines.append(f"\n【各科成绩情况】")
        
        for analysis in report.subject_analyses:
            status = "优势" if analysis.is_strong else ("薄弱" if analysis.is_weak else "中等")
            lines.append(
                f"- {analysis.subject_name}: 平均得分率{analysis.average_score_rate*100:.1f}% "
                f"[{status}] 趋势:{analysis.score_trend}"
            )
        
        if report.strong_subjects:
            lines.append(f"\n【优势学科】{', '.join(report.strong_subjects)}")
        
        if report.weak_subjects:
            lines.append(f"【薄弱学科】{', '.join(report.weak_subjects)}")
        
        # 添加知识点分析
        if report.knowledge_weaknesses:
            lines.append(f"\n【薄弱知识点】")
            for kp in report.knowledge_weaknesses[:5]:
                lines.append(f"  - {kp}")
        
        # 获取优势知识点
        mastery_data = self.db.get_knowledge_point_mastery(student_id)
        strong_kps = [
            f"{item['subject']}-{item['knowledge_point']} ({item['mastery_rate']*100:.0f}%)"
            for item in mastery_data 
            if item['mastery_rate'] >= 0.85 and item['total_questions'] >= 2
        ][:5]
        
        if strong_kps:
            lines.append(f"\n【掌握良好的知识点】")
            for kp in strong_kps:
                lines.append(f"  - {kp}")
        
        lines.append(f"\n【学习潜力评估】{report.potential_analysis.potential_rating}")
        lines.append(f"【整体趋势】{report.potential_analysis.overall_trend}")
        
        # 添加文理倾向分析
        science_subjects = ["数学", "物理", "化学", "生物"]
        arts_subjects = ["语文", "英语", "政治", "历史", "地理"]
        
        science_avg = 0
        arts_avg = 0
        science_count = 0
        arts_count = 0
        
        for analysis in report.subject_analyses:
            if analysis.subject_name in science_subjects:
                science_avg += analysis.average_score_rate
                science_count += 1
            elif analysis.subject_name in arts_subjects:
                arts_avg += analysis.average_score_rate
                arts_count += 1
        
        if science_count > 0 and arts_count > 0:
            science_avg /= science_count
            arts_avg /= arts_count
            
            if science_avg - arts_avg > 0.1:
                tendency = "明显偏理科"
            elif arts_avg - science_avg > 0.1:
                tendency = "明显偏文科"
            elif science_avg > arts_avg:
                tendency = "略偏理科"
            elif arts_avg > science_avg:
                tendency = "略偏文科"
            else:
                tendency = "文理均衡"
            
            lines.append(f"\n【文理倾向】{tendency}")
            lines.append(f"  - 理科平均得分率: {science_avg*100:.1f}%")
            lines.append(f"  - 文科平均得分率: {arts_avg*100:.1f}%")
        
        return '\n'.join(lines)
    
    # ============ 新增：成绩预测与预警 ============
    
    def predict_next_score(self, student_id: int, subject_id: int) -> Dict:
        """
        预测下次考试成绩
        
        Returns:
            {
                'predicted_score': float,
                'confidence_interval': (low, high),
                'trend_strength': str,  # 强上升/上升/稳定/下降/强下降
                'warning': str or None,
                'improvement_rate': float
            }
        """
        scores_data = self.db.get_student_scores_by_subject(student_id, subject_id)
        
        if len(scores_data) < 2:
            return {
                'predicted_score': None,
                'confidence_interval': (0, 0),
                'trend_strength': '数据不足',
                'warning': None,
                'improvement_rate': 0
            }
        
        # 按日期排序
        sorted_scores = sorted(scores_data, key=lambda x: x[1].exam_date or date.min)
        scores = [s[0].score for s in sorted_scores]
        total_scores = [s[1].total_score for s in sorted_scores]
        
        # 使用线性回归预测
        x = np.arange(len(scores))
        slope, intercept = np.polyfit(x, scores, 1)
        
        # 预测下一次分数
        predicted = slope * len(scores) + intercept
        predicted = max(0, min(100, predicted))  # 限制在0-100
        
        # 计算置信区间(基于标准差)
        std_dev = np.std(scores) if len(scores) > 2 else 5
        confidence_low = max(0, predicted - 1.5 * std_dev)
        confidence_high = min(100, predicted + 1.5 * std_dev)
        
        # 判断趋势强度
        if slope > 3:
            trend_strength = "强上升 📈"
        elif slope > 0.5:
            trend_strength = "上升 ↗"
        elif slope < -3:
            trend_strength = "强下降 📉"
        elif slope < -0.5:
            trend_strength = "下降 ↘"
        else:
            trend_strength = "稳定 →"
        
        # 生成预警
        warning = None
        if len(scores) >= 2:
            if scores[-1] < scores[-2] and scores[-2] < scores[-3] if len(scores) >= 3 else False:
                warning = "⚠️ 连续下降预警：最近成绩持续走低"
            elif predicted < 60:
                warning = "⚠️ 及格风险预警：预测分数可能不及格"
            elif predicted < scores[-1] - 10:
                warning = "⚠️ 下滑预警：预测分数较上次明显下降"
        
        # 计算改进率
        if len(scores) >= 2:
            improvement_rate = ((scores[-1] - scores[0]) / scores[0]) * 100 if scores[0] > 0 else 0
        else:
            improvement_rate = 0
        
        return {
            'predicted_score': round(predicted, 1),
            'confidence_interval': (round(confidence_low, 1), round(confidence_high, 1)),
            'trend_strength': trend_strength,
            'warning': warning,
            'improvement_rate': round(improvement_rate, 1)
        }
    
    # ============ 新增：同伴对比分析 ============
    
    def compare_with_peers(self, student_id: int, subject_id: int = None) -> Dict:
        """
        与同班/同年级同学对比
        
        Returns:
            {
                'class_rank': int,
                'class_total': int,
                'percentile': float,  # 百分位
                'vs_class_avg': float,  # 比班级平均高/低多少
                'progress_rank': int,  # 进步排名
                'subject_rankings': [{subject, rank, percentile}]
            }
        """
        student = self.db.get_student_by_id(student_id)
        if not student:
            return {}
        
        # 获取同班学生
        all_students = self.db.get_all_students()
        classmates = [s for s in all_students if s.class_name == student.class_name]
        
        if not classmates:
            return {'error': '暂无班级数据'}
        
        # 计算各科排名
        subject_rankings = []
        subjects = self.db.get_all_subjects()
        
        total_avg = 0
        class_avg_total = 0
        subject_count = 0
        
        for subj in subjects:
            if subject_id and subj.id != subject_id:
                continue
            
            # 计算每个同学在该科目的平均分
            student_avgs = []
            for s in classmates:
                scores = self.db.get_student_scores_by_subject(s.id, subj.id)
                if scores:
                    avg = np.mean([sc[0].score_rate for sc in scores])
                    student_avgs.append((s.id, avg))
            
            if not student_avgs:
                continue
            
            # 排序得名次
            student_avgs.sort(key=lambda x: -x[1])
            
            # 找到当前学生的排名
            rank = 1
            student_score = 0
            for i, (sid, avg) in enumerate(student_avgs):
                if sid == student_id:
                    rank = i + 1
                    student_score = avg
                    break
            
            class_avg = np.mean([x[1] for x in student_avgs])
            percentile = ((len(student_avgs) - rank) / len(student_avgs)) * 100
            
            subject_rankings.append({
                'subject': subj.name,
                'rank': rank,
                'total': len(student_avgs),
                'percentile': round(percentile, 1),
                'vs_avg': round((student_score - class_avg) * 100, 1),
                'score_rate': round(student_score * 100, 1)
            })
            
            total_avg += student_score
            class_avg_total += class_avg
            subject_count += 1
        
        # 计算综合排名
        overall_rank = 1
        overall_percentile = 50
        vs_class_avg = 0
        
        if subject_count > 0:
            vs_class_avg = round((total_avg / subject_count - class_avg_total / subject_count) * 100, 1)
        
        return {
            'class_size': len(classmates),
            'vs_class_avg': vs_class_avg,
            'subject_rankings': subject_rankings
        }
    
    # ============ 新增：学科相关性分析 ============
    
    def calculate_subject_correlation(self, student_id: int) -> Dict:
        """
        计算学科之间的相关性
        
        Returns:
            {
                'subjects': [科目名称],
                'matrix': [[相关系数矩阵]],
                'strong_correlations': [(科目1, 科目2, 系数)]
            }
        """
        subjects = self.db.get_all_subjects()
        subject_scores = {}
        
        # 获取每个科目的成绩序列
        for subj in subjects:
            scores = self.db.get_student_scores_by_subject(student_id, subj.id)
            if scores:
                subject_scores[subj.name] = [s[0].score_rate for s in scores]
        
        if len(subject_scores) < 2:
            return {'subjects': [], 'matrix': [], 'strong_correlations': []}
        
        # 对齐数据长度(取最小长度)
        min_len = min(len(v) for v in subject_scores.values())
        aligned_scores = {k: v[:min_len] for k, v in subject_scores.items()}
        
        subj_names = list(aligned_scores.keys())
        n = len(subj_names)
        
        # 计算相关系数矩阵
        matrix = np.zeros((n, n))
        strong_correlations = []
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    matrix[i][j] = 1.0
                elif len(aligned_scores[subj_names[i]]) >= 3:
                    corr = np.corrcoef(aligned_scores[subj_names[i]], aligned_scores[subj_names[j]])[0, 1]
                    if np.isnan(corr):
                        corr = 0
                    matrix[i][j] = round(corr, 2)
                    
                    if abs(corr) > 0.7 and i < j:
                        strong_correlations.append((subj_names[i], subj_names[j], round(corr, 2)))
        
        return {
            'subjects': subj_names,
            'matrix': matrix.tolist(),
            'strong_correlations': strong_correlations
        }
    
    # ============ 新增：多维度评分 ============
    
    def calculate_comprehensive_scores(self, student_id: int) -> Dict:
        """
        计算多维度综合评分
        
        Returns:
            {
                'mastery_score': float,  # 学科掌握度(0-100)
                'attitude_score': float,  # 学习态度(基于趋势)
                'stability_score': float,  # 稳定性
                'potential_score': float,  # 潜力评分
                'balance_score': float,  # 均衡度
                'overall_rating': str  # 综合评级
            }
        """
        report = self.analyze_student(student_id)
        
        if not report or not report.subject_analyses:
            return {
                'mastery_score': 0,
                'attitude_score': 0,
                'stability_score': 0,
                'potential_score': 0,
                'balance_score': 0,
                'overall_rating': '数据不足'
            }
        
        analyses = report.subject_analyses
        
        # 1. 学科掌握度 (平均得分率 * 100)
        mastery_score = np.mean([a.average_score_rate for a in analyses]) * 100
        
        # 2. 学习态度 (基于趋势斜率)
        avg_slope = np.mean([a.trend_slope for a in analyses])
        attitude_score = 50 + avg_slope * 1000  # 转换到0-100
        attitude_score = max(0, min(100, attitude_score))
        
        # 3. 稳定性 (基于标准差的倒数)
        score_rates = [a.average_score_rate for a in analyses]
        stability = 1 - np.std(score_rates) * 2
        stability_score = max(0, min(100, stability * 100))
        
        # 4. 潜力评分 (考虑趋势和当前水平)
        if report.potential_analysis.potential_rating == "高":
            potential_score = 85
        elif report.potential_analysis.potential_rating == "中":
            potential_score = 65
        else:
            potential_score = 45
        
        # 5. 均衡度 (各科差异小则高)
        range_score = max(score_rates) - min(score_rates)
        balance_score = max(0, 100 - range_score * 200)
        
        # 综合评级
        overall = (mastery_score * 0.4 + attitude_score * 0.2 + 
                   stability_score * 0.15 + potential_score * 0.15 + balance_score * 0.1)
        
        if overall >= 85:
            overall_rating = "优秀 ⭐⭐⭐"
        elif overall >= 70:
            overall_rating = "良好 ⭐⭐"
        elif overall >= 55:
            overall_rating = "中等 ⭐"
        else:
            overall_rating = "需努力 💪"
        
        return {
            'mastery_score': round(mastery_score, 1),
            'attitude_score': round(attitude_score, 1),
            'stability_score': round(stability_score, 1),
            'potential_score': round(potential_score, 1),
            'balance_score': round(balance_score, 1),
            'overall_rating': overall_rating
        }
    
    # ============ 新增：智能洞察生成 ============
    
    def generate_smart_insights(self, student_id: int) -> List[Dict]:
        """
        自动生成智能洞察
        
        Returns:
            [
                {
                    'type': 'warning'/'success'/'info',
                    'title': str,
                    'content': str,
                    'priority': int (1-5)
                }
            ]
        """
        insights = []
        report = self.analyze_student(student_id)
        
        if not report:
            return [{'type': 'info', 'title': '数据不足', 'content': '请先录入成绩数据', 'priority': 1}]
        
        # 1. 检测连续下降
        for analysis in report.subject_analyses:
            if analysis.trend_slope < -0.03:
                insights.append({
                    'type': 'warning',
                    'title': f'⚠️ {analysis.subject_name}成绩下滑',
                    'content': f'{analysis.subject_name}呈下降趋势，最近表现需要关注',
                    'priority': 1
                })
        
        # 2. 检测显著进步
        for analysis in report.subject_analyses:
            if analysis.trend_slope > 0.05:
                insights.append({
                    'type': 'success',
                    'title': f'🌟 {analysis.subject_name}进步明显',
                    'content': f'{analysis.subject_name}呈强上升趋势，继续保持！',
                    'priority': 2
                })
        
        # 3. 发现强项和弱项的差距
        if report.strong_subjects and report.weak_subjects:
            strong_avg = np.mean([a.average_score_rate for a in report.subject_analyses if a.is_strong])
            weak_avg = np.mean([a.average_score_rate for a in report.subject_analyses if a.is_weak])
            gap = (strong_avg - weak_avg) * 100
            
            if gap > 20:
                insights.append({
                    'type': 'info',
                    'title': '📊 科目差距较大',
                    'content': f'优势科与弱势科差距{gap:.0f}分，建议平衡发展',
                    'priority': 3
                })
        
        # 4. 学科相关性洞察
        correlation = self.calculate_subject_correlation(student_id)
        for subj1, subj2, corr in correlation.get('strong_correlations', []):
            insights.append({
                'type': 'info',
                'title': f'🔗 发现学科关联',
                'content': f'{subj1}和{subj2}成绩高度相关(系数{corr})，可采用相似学习方法',
                'priority': 4
            })
        
        # 5. 潜力评估
        if report.potential_analysis.potential_rating == "高":
            insights.append({
                'type': 'success',
                'title': '🚀 学习潜力高',
                'content': '数据显示你有很大的进步空间，保持积极态度！',
                'priority': 5
            })
        
        # 按优先级排序
        insights.sort(key=lambda x: x['priority'])
        
        return insights[:5]  # 最多返回5条


