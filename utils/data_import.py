"""
数据导入工具
支持从Excel和CSV文件导入学生、成绩、试卷等数据
"""
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, date
import logging

from database.models import Student, Exam, ExamScore, Question, KnowledgePoint
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DataImporter:
    """数据导入器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def import_students_from_excel(self, file_path: str) -> Tuple[int, List[str]]:
        """
        从Excel导入学生数据
        
        期望的列名：学号, 姓名, 性别, 年级, 班级, 入学年份
        
        Returns:
            (成功导入数量, 错误信息列表)
        """
        errors = []
        success_count = 0
        
        try:
            df = pd.read_excel(file_path)
            
            # 列名映射
            column_map = {
                '学号': 'student_id',
                '姓名': 'name',
                '性别': 'gender',
                '年级': 'grade',
                '班级': 'class_name',
                '入学年份': 'enrollment_year'
            }
            
            # 检查必需列
            required_columns = ['学号', '姓名']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"缺少必需列: {col}")
                    return 0, errors
            
            for idx, row in df.iterrows():
                try:
                    student = Student(
                        student_id=str(row.get('学号', '')).strip(),
                        name=str(row.get('姓名', '')).strip(),
                        gender=str(row.get('性别', '')).strip() if pd.notna(row.get('性别')) else '',
                        grade=str(row.get('年级', '')).strip() if pd.notna(row.get('年级')) else '',
                        class_name=str(row.get('班级', '')).strip() if pd.notna(row.get('班级')) else '',
                        enrollment_year=int(row.get('入学年份', 0)) if pd.notna(row.get('入学年份')) else 0
                    )
                    
                    if not student.student_id or not student.name:
                        errors.append(f"第{idx + 2}行: 学号或姓名为空")
                        continue
                    
                    # 检查是否已存在
                    existing = self.db.get_student(student.student_id)
                    if existing:
                        errors.append(f"第{idx + 2}行: 学号 {student.student_id} 已存在")
                        continue
                    
                    self.db.add_student(student)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"第{idx + 2}行: {str(e)}")
                    
        except Exception as e:
            errors.append(f"读取文件失败: {str(e)}")
        
        return success_count, errors
    
    def import_students_from_csv(self, file_path: str, encoding: str = 'utf-8') -> Tuple[int, List[str]]:
        """从CSV导入学生数据"""
        errors = []
        success_count = 0
        
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            
            required_columns = ['学号', '姓名']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"缺少必需列: {col}")
                    return 0, errors
            
            for idx, row in df.iterrows():
                try:
                    student = Student(
                        student_id=str(row.get('学号', '')).strip(),
                        name=str(row.get('姓名', '')).strip(),
                        gender=str(row.get('性别', '')).strip() if pd.notna(row.get('性别')) else '',
                        grade=str(row.get('年级', '')).strip() if pd.notna(row.get('年级')) else '',
                        class_name=str(row.get('班级', '')).strip() if pd.notna(row.get('班级')) else '',
                        enrollment_year=int(row.get('入学年份', 0)) if pd.notna(row.get('入学年份')) else 0
                    )
                    
                    if not student.student_id or not student.name:
                        errors.append(f"第{idx + 2}行: 学号或姓名为空")
                        continue
                    
                    existing = self.db.get_student(student.student_id)
                    if existing:
                        errors.append(f"第{idx + 2}行: 学号 {student.student_id} 已存在")
                        continue
                    
                    self.db.add_student(student)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"第{idx + 2}行: {str(e)}")
                    
        except Exception as e:
            errors.append(f"读取文件失败: {str(e)}")
        
        return success_count, errors
    
    def import_scores_from_excel(self, file_path: str) -> Tuple[int, List[str]]:
        """
        从Excel导入成绩数据
        
        期望的列名：学号, 考试名称, 学科, 分数, 班级排名, 年级排名, 考试日期, 满分
        
        Returns:
            (成功导入数量, 错误信息列表)
        """
        errors = []
        success_count = 0
        
        try:
            df = pd.read_excel(file_path)
            
            required_columns = ['学号', '考试名称', '学科', '分数']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"缺少必需列: {col}")
                    return 0, errors
            
            # 缓存考试ID以避免重复创建
            exam_cache: Dict[str, int] = {}
            
            for idx, row in df.iterrows():
                try:
                    student_id = str(row.get('学号', '')).strip()
                    exam_name = str(row.get('考试名称', '')).strip()
                    subject_name = str(row.get('学科', '')).strip()
                    score_val = float(row.get('分数', 0))
                    
                    # 获取学生
                    student = self.db.get_student(student_id)
                    if not student:
                        errors.append(f"第{idx + 2}行: 学号 {student_id} 不存在")
                        continue
                    
                    # 获取学科
                    subject = self.db.get_subject_by_name(subject_name)
                    if not subject:
                        errors.append(f"第{idx + 2}行: 学科 {subject_name} 不存在")
                        continue
                    
                    # 获取或创建考试
                    exam_key = f"{exam_name}_{subject.id}"
                    if exam_key in exam_cache:
                        exam_id = exam_cache[exam_key]
                    else:
                        # 尝试查找现有考试
                        exams = self.db.get_exams_by_subject(subject.id)
                        exam_id = None
                        for e in exams:
                            if e.name == exam_name:
                                exam_id = e.id
                                break
                        
                        if not exam_id:
                            # 创建新考试
                            total_score = float(row.get('满分', 100)) if pd.notna(row.get('满分')) else 100
                            exam_date_val = None
                            if pd.notna(row.get('考试日期')):
                                try:
                                    exam_date_val = pd.to_datetime(row.get('考试日期')).date()
                                except:
                                    pass
                            
                            exam = Exam(
                                name=exam_name,
                                subject_id=subject.id,
                                exam_type='',
                                exam_date=exam_date_val,
                                total_score=total_score,
                                grade_scope=student.grade if student else ''
                            )
                            exam_id = self.db.add_exam(exam)
                        
                        exam_cache[exam_key] = exam_id
                    
                    # 计算得分率
                    total_score = float(row.get('满分', 100)) if pd.notna(row.get('满分')) else 100
                    score_rate = score_val / total_score if total_score > 0 else 0
                    
                    # 创建成绩记录
                    exam_score = ExamScore(
                        student_id=student.id,
                        exam_id=exam_id,
                        score=score_val,
                        rank_in_class=int(row.get('班级排名')) if pd.notna(row.get('班级排名')) else None,
                        rank_in_grade=int(row.get('年级排名')) if pd.notna(row.get('年级排名')) else None,
                        score_rate=score_rate
                    )
                    
                    self.db.add_score(exam_score)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"第{idx + 2}行: {str(e)}")
                    
        except Exception as e:
            errors.append(f"读取文件失败: {str(e)}")
        
        return success_count, errors
    
    def import_questions_from_excel(self, file_path: str) -> Tuple[int, List[str]]:
        """
        从Excel导入题目数据
        
        期望的列名：学科, 题目内容, 标准答案, 解析, 题型, 难度系数, 分值, 知识点
        
        Returns:
            (成功导入数量, 错误信息列表)
        """
        errors = []
        success_count = 0
        
        try:
            df = pd.read_excel(file_path)
            
            required_columns = ['学科', '题目内容']
            for col in required_columns:
                if col not in df.columns:
                    errors.append(f"缺少必需列: {col}")
                    return 0, errors
            
            for idx, row in df.iterrows():
                try:
                    subject_name = str(row.get('学科', '')).strip()
                    content = str(row.get('题目内容', '')).strip()
                    
                    # 获取学科
                    subject = self.db.get_subject_by_name(subject_name)
                    if not subject:
                        errors.append(f"第{idx + 2}行: 学科 {subject_name} 不存在")
                        continue
                    
                    question = Question(
                        subject_id=subject.id,
                        content=content,
                        answer=str(row.get('标准答案', '')).strip() if pd.notna(row.get('标准答案')) else '',
                        analysis=str(row.get('解析', '')).strip() if pd.notna(row.get('解析')) else '',
                        question_type=str(row.get('题型', '')).strip() if pd.notna(row.get('题型')) else '',
                        difficulty=float(row.get('难度系数', 0.5)) if pd.notna(row.get('难度系数')) else 0.5,
                        score=float(row.get('分值', 0)) if pd.notna(row.get('分值')) else 0
                    )
                    
                    question_id = self.db.add_question(question)
                    
                    # 处理知识点关联
                    knowledge_points = str(row.get('知识点', '')).strip() if pd.notna(row.get('知识点')) else ''
                    if knowledge_points:
                        for kp_name in knowledge_points.split(','):
                            kp_name = kp_name.strip()
                            if kp_name:
                                # 查找或创建知识点
                                kps = self.db.get_knowledge_points_by_subject(subject.id)
                                kp_id = None
                                for kp in kps:
                                    if kp.name == kp_name:
                                        kp_id = kp.id
                                        break
                                
                                if not kp_id:
                                    kp = KnowledgePoint(
                                        subject_id=subject.id,
                                        name=kp_name,
                                        level=1
                                    )
                                    kp_id = self.db.add_knowledge_point(kp)
                                
                                self.db.link_question_to_knowledge(question_id, kp_id)
                    
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"第{idx + 2}行: {str(e)}")
                    
        except Exception as e:
            errors.append(f"读取文件失败: {str(e)}")
        
        return success_count, errors
    
    def generate_import_template(self, template_type: str, output_path: str) -> bool:
        """
        生成导入模板Excel文件
        
        Args:
            template_type: 'students', 'scores', 'questions'
            output_path: 输出文件路径
        """
        try:
            if template_type == 'students':
                df = pd.DataFrame({
                    '学号': ['2024001', '2024002'],
                    '姓名': ['张三', '李四'],
                    '性别': ['男', '女'],
                    '年级': ['高一', '高一'],
                    '班级': ['1班', '2班'],
                    '入学年份': [2024, 2024]
                })
            elif template_type == 'scores':
                df = pd.DataFrame({
                    '学号': ['2024001', '2024001', '2024002'],
                    '考试名称': ['2024年期中考试', '2024年期中考试', '2024年期中考试'],
                    '学科': ['数学', '语文', '数学'],
                    '分数': [135, 128, 142],
                    '满分': [150, 150, 150],
                    '班级排名': [5, 8, 2],
                    '年级排名': [25, 45, 12],
                    '考试日期': ['2024-11-15', '2024-11-15', '2024-11-15']
                })
            elif template_type == 'questions':
                df = pd.DataFrame({
                    '学科': ['数学', '数学'],
                    '题目内容': ['求函数f(x)=x²+2x+1的最小值', '已知a+b=5, ab=6, 求a²+b²的值'],
                    '标准答案': ['0', '13'],
                    '解析': ['f(x)=(x+1)², 最小值为0', 'a²+b²=(a+b)²-2ab=25-12=13'],
                    '题型': ['解答题', '解答题'],
                    '难度系数': [0.3, 0.4],
                    '分值': [10, 8],
                    '知识点': ['二次函数,最值问题', '完全平方公式']
                })
            else:
                return False
            
            df.to_excel(output_path, index=False)
            return True
            
        except Exception as e:
            logger.error(f"生成模板失败: {e}")
            return False
