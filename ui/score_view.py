"""
成绩录入视图 - 优化版
包含试卷得分详情功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QLabel, QDialog, QFormLayout, QSpinBox,
    QMessageBox, QFileDialog, QHeaderView, QFrame, QGraphicsDropShadowEffect,
    QTabWidget, QDoubleSpinBox, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DatabaseManager
from database.models import ExamScore, StudentAnswer
from utils.data_import import DataImporter
import config


class ScoreView(QWidget):
    """成绩录入视图"""
    
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.importer = DataImporter(db)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题栏
        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("📝 成绩管理")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("录入成绩、查看答题详情、批量导入")
        subtitle.setStyleSheet("color: #718096; font-size: 13px;")
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)
        
        # 选择区域
        select_card = QFrame()
        select_card.setStyleSheet("QFrame { background: white; border-radius: 12px; }")
        self._add_shadow(select_card)
        
        select_layout = QHBoxLayout(select_card)
        select_layout.setContentsMargins(20, 15, 20, 15)
        
        select_layout.addWidget(QLabel("👤 学生:"))
        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(200)
        self.student_combo.setStyleSheet(self._combo_style())
        self.student_combo.currentIndexChanged.connect(self._on_student_changed)
        select_layout.addWidget(self.student_combo)
        
        select_layout.addWidget(QLabel("  📚 科目:"))
        self.subject_combo = QComboBox()
        self.subject_combo.setMinimumWidth(120)
        self.subject_combo.setStyleSheet(self._combo_style())
        self.subject_combo.currentIndexChanged.connect(self._on_filter_changed)
        select_layout.addWidget(self.subject_combo)
        
        select_layout.addStretch()
        
        self.import_btn = QPushButton("📥 导入成绩")
        self.import_btn.setStyleSheet(self._btn_style("#48bb78", "#38a169"))
        self.import_btn.clicked.connect(self._import_scores)
        select_layout.addWidget(self.import_btn)
        
        layout.addWidget(select_card)
        
        # 标签页
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
                border-radius: 12px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 5px;
                background: #e2e8f0;
                border-radius: 6px 6px 0 0;
                color: #4a5568;
            }
            QTabBar::tab:selected {
                background: white;
                color: #667eea;
                font-weight: bold;
            }
        """)
        
        # Tab 1: 成绩概览
        self.tabs.addTab(self._create_overview_tab(), "📊 成绩概览")
        
        # Tab 2: 答题详情
        self.tabs.addTab(self._create_detail_tab(), "📋 答题详情")
        
        layout.addWidget(self.tabs)
    
    def _create_overview_tab(self):
        """成绩概览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 15, 0, 0)
        
        self.score_table = QTableWidget()
        self.score_table.setColumnCount(7)
        self.score_table.setHorizontalHeaderLabels([
            "考试名称", "科目", "日期", "得分", "满分", "得分率", "查看详情"
        ])
        self.score_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.score_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.score_table.setColumnWidth(6, 100)
        self.score_table.setStyleSheet(self._table_style())
        self.score_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.score_table)
        return widget
    
    def _create_detail_tab(self):
        """答题详情标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 15, 0, 0)
        
        # 选择考试
        exam_bar = QHBoxLayout()
        exam_bar.addWidget(QLabel("选择考试:"))
        self.exam_combo = QComboBox()
        self.exam_combo.setMinimumWidth(300)
        self.exam_combo.setStyleSheet(self._combo_style())
        self.exam_combo.currentIndexChanged.connect(self._load_exam_details)
        exam_bar.addWidget(self.exam_combo)
        exam_bar.addStretch()
        layout.addLayout(exam_bar)
        
        # 详情表格
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(6)
        self.detail_table.setHorizontalHeaderLabels([
            "题号", "题目类型", "满分", "得分", "得分率", "状态"
        ])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.setStyleSheet(self._table_style())
        self.detail_table.verticalHeader().setVisible(False)
        layout.addWidget(self.detail_table)
        
        # 统计信息
        self.detail_stats = QLabel()
        self.detail_stats.setStyleSheet("color: #718096; padding: 10px; font-size: 13px;")
        layout.addWidget(self.detail_stats)
        
        return widget
    
    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 20))
        widget.setGraphicsEffect(shadow)
    
    def _combo_style(self):
        return """
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                background: white;
            }
            QComboBox:focus { border-color: #667eea; }
        """
    
    def _btn_style(self, bg, hover):
        return f"""
            QPushButton {{
                background: {bg};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """
    
    def _table_style(self):
        return """
            QTableWidget {
                border: none;
                gridline-color: #f0f0f0;
                background: white;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background: #f7fafc;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #4a5568;
            }
        """
    
    def refresh(self):
        """刷新数据"""
        # 刷新学生列表
        self.student_combo.clear()
        self.student_combo.addItem("-- 选择学生 --", None)
        for s in self.db.get_all_students():
            self.student_combo.addItem(f"{s.student_id} - {s.name}", s.id)
        
        # 刷新科目列表
        self.subject_combo.clear()
        self.subject_combo.addItem("全部科目", None)
        for subject in self.db.get_all_subjects():
            self.subject_combo.addItem(subject.name, subject.id)
    
    def _on_student_changed(self):
        self._load_scores()
        self._load_exams_for_detail()
    
    def _on_filter_changed(self):
        self._load_scores()
    
    def _load_scores(self):
        """加载成绩列表"""
        student_id = self.student_combo.currentData()
        if not student_id:
            self.score_table.setRowCount(0)
            return
        
        scores = self.db.get_student_scores(student_id)
        subject_filter = self.subject_combo.currentData()
        
        if subject_filter:
            scores = [s for s in scores if s[2].id == subject_filter]
        
        self.score_table.setRowCount(len(scores))
        
        for row, (score, exam, subject) in enumerate(scores):
            self.score_table.setItem(row, 0, QTableWidgetItem(exam.name))
            self.score_table.setItem(row, 1, QTableWidgetItem(subject.name))
            self.score_table.setItem(row, 2, QTableWidgetItem(
                exam.exam_date.strftime("%Y-%m-%d") if exam.exam_date else ""
            ))
            self.score_table.setItem(row, 3, QTableWidgetItem(f"{score.score:.1f}"))
            self.score_table.setItem(row, 4, QTableWidgetItem(f"{exam.total_score:.0f}"))
            
            rate = score.score_rate * 100 if score.score_rate else 0
            rate_item = QTableWidgetItem(f"{rate:.1f}%")
            if rate >= 85:
                rate_item.setForeground(QColor("#22543d"))
                rate_item.setBackground(QColor("#c6f6d5"))
            elif rate < 60:
                rate_item.setForeground(QColor("#742a2a"))
                rate_item.setBackground(QColor("#fed7d7"))
            self.score_table.setItem(row, 5, rate_item)
            
            # 查看详情按钮
            view_btn = QPushButton("查看")
            view_btn.setStyleSheet("""
                QPushButton {
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 5px 12px;
                    border-radius: 4px;
                }
                QPushButton:hover { background: #5a67d8; }
            """)
            view_btn.clicked.connect(lambda _, e=exam.id: self._show_detail(e))
            self.score_table.setCellWidget(row, 6, view_btn)
    
    def _load_exams_for_detail(self):
        """加载考试列表到详情标签页"""
        student_id = self.student_combo.currentData()
        self.exam_combo.clear()
        
        if not student_id:
            return
        
        self.exam_combo.addItem("-- 选择考试 --", None)
        scores = self.db.get_student_scores(student_id)
        for score, exam, subject in scores:
            self.exam_combo.addItem(f"{exam.name}", (exam.id, student_id))
    
    def _show_detail(self, exam_id):
        """跳转到详情页并选择对应考试"""
        self.tabs.setCurrentIndex(1)
        for i in range(self.exam_combo.count()):
            data = self.exam_combo.itemData(i)
            if data and data[0] == exam_id:
                self.exam_combo.setCurrentIndex(i)
                break
    
    def _load_exam_details(self):
        """加载考试答题详情"""
        data = self.exam_combo.currentData()
        if not data:
            self.detail_table.setRowCount(0)
            self.detail_stats.clear()
            return
        
        exam_id, student_id = data
        answers = self.db.get_student_answers_for_exam(student_id, exam_id)
        
        if not answers:
            self.detail_table.setRowCount(0)
            self.detail_stats.setText("暂无答题详情数据")
            return
        
        self.detail_table.setRowCount(len(answers))
        
        total_max = 0
        total_got = 0
        correct_count = 0
        
        for row, answer in enumerate(answers):
            # 获取题目信息
            question = None
            for q in self.db.get_questions_by_subject(1):  # 需要优化
                if q.id == answer.question_id:
                    question = q
                    break
            
            q_score = question.score if question else 10
            q_type = question.question_type if question else "未知"
            
            self.detail_table.setItem(row, 0, QTableWidgetItem(f"第{row+1}题"))
            self.detail_table.setItem(row, 1, QTableWidgetItem(q_type))
            self.detail_table.setItem(row, 2, QTableWidgetItem(f"{q_score:.0f}"))
            self.detail_table.setItem(row, 3, QTableWidgetItem(f"{answer.score_obtained:.1f}"))
            
            rate = answer.score_obtained / q_score * 100 if q_score > 0 else 0
            rate_item = QTableWidgetItem(f"{rate:.0f}%")
            self.detail_table.setItem(row, 4, rate_item)
            
            status = "✅ 正确" if answer.is_correct else ("⚠️ 部分" if rate >= 50 else "❌ 错误")
            status_item = QTableWidgetItem(status)
            if answer.is_correct:
                status_item.setForeground(QColor("#22543d"))
            elif rate < 50:
                status_item.setForeground(QColor("#c53030"))
            self.detail_table.setItem(row, 5, status_item)
            
            total_max += q_score
            total_got += answer.score_obtained
            if answer.is_correct:
                correct_count += 1
        
        # 更新统计
        self.detail_stats.setText(
            f"📊 共 {len(answers)} 道题 | "
            f"正确 {correct_count} 道 | "
            f"得分 {total_got:.1f}/{total_max:.0f} | "
            f"得分率 {total_got/total_max*100:.1f}%"
        )
    
    def _import_scores(self):
        """导入成绩"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            success, errors = self.importer.import_scores_from_excel(file_path)
            self.refresh()
            msg = f"成功导入 {success} 条成绩"
            if errors:
                msg += f"\n\n部分导入失败:\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "导入结果", msg)
