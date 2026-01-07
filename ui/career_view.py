"""
职业规划视图
查看和管理学生的职业规划报告
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QPushButton, QTextEdit, QFrame, QGroupBox, QListWidget,
    QListWidgetItem, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db_manager import DatabaseManager
from services.ai_service import AIService


class CareerView(QWidget):
    """职业规划视图"""
    
    def __init__(self, db: DatabaseManager, ai_service: AIService):
        super().__init__()
        self.db = db
        self.ai_service = ai_service
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🎯 职业规划报告")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 工具栏
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("选择学生:"))
        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(200)
        self.student_combo.currentIndexChanged.connect(self._on_student_changed)
        toolbar.addWidget(self.student_combo)
        toolbar.addStretch()
        
        self.generate_btn = QPushButton("📋 生成新报告")
        self.generate_btn.clicked.connect(self._generate_report)
        toolbar.addWidget(self.generate_btn)
        layout.addLayout(toolbar)
        
        # 主内容区
        content = QHBoxLayout()
        
        # 左侧：报告列表
        list_group = QGroupBox("历史报告")
        list_layout = QVBoxLayout(list_group)
        self.report_list = QListWidget()
        self.report_list.currentRowChanged.connect(self._on_report_selected)
        list_layout.addWidget(self.report_list)
        list_group.setMaximumWidth(200)
        content.addWidget(list_group)
        
        # 右侧：报告详情
        detail_scroll = QScrollArea()
        detail_scroll.setWidgetResizable(True)
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        # 性格特征
        personality_group = QGroupBox("🧠 性格特征分析")
        personality_layout = QVBoxLayout(personality_group)
        self.personality_text = QTextEdit()
        self.personality_text.setReadOnly(True)
        self.personality_text.setMaximumHeight(120)
        personality_layout.addWidget(self.personality_text)
        detail_layout.addWidget(personality_group)
        
        # 选科建议
        subject_group = QGroupBox("📚 选科建议")
        subject_layout = QVBoxLayout(subject_group)
        self.subject_text = QTextEdit()
        self.subject_text.setReadOnly(True)
        self.subject_text.setMaximumHeight(120)
        subject_layout.addWidget(self.subject_text)
        detail_layout.addWidget(subject_group)
        
        # 职业推荐
        career_group = QGroupBox("💼 职业推荐")
        career_layout = QVBoxLayout(career_group)
        self.career_text = QTextEdit()
        self.career_text.setReadOnly(True)
        self.career_text.setMaximumHeight(120)
        career_layout.addWidget(self.career_text)
        detail_layout.addWidget(career_group)
        
        # 专业推荐
        major_group = QGroupBox("🎓 专业推荐")
        major_layout = QVBoxLayout(major_group)
        self.major_text = QTextEdit()
        self.major_text.setReadOnly(True)
        self.major_text.setMaximumHeight(120)
        major_layout.addWidget(self.major_text)
        detail_layout.addWidget(major_group)
        
        # 详细分析
        analysis_group = QGroupBox("📝 详细分析")
        analysis_layout = QVBoxLayout(analysis_group)
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        analysis_layout.addWidget(self.analysis_text)
        detail_layout.addWidget(analysis_group)
        
        detail_scroll.setWidget(detail_widget)
        content.addWidget(detail_scroll)
        layout.addLayout(content)
        
        # 样式
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QTextEdit {
                border: none;
            }
        """)
    
    def refresh(self):
        self.student_combo.clear()
        self.student_combo.addItem("-- 请选择学生 --", None)
        for s in self.db.get_all_students():
            self.student_combo.addItem(f"{s.student_id} - {s.name}", s.id)
    
    def _on_student_changed(self):
        sid = self.student_combo.currentData()
        self.report_list.clear()
        self._clear_report()
        
        if sid:
            reports = self.db.get_career_reports(sid)
            for r in reports:
                item = QListWidgetItem(r.report_date.strftime("%Y-%m-%d"))
                item.setData(Qt.ItemDataRole.UserRole, r)
                self.report_list.addItem(item)
    
    def _on_report_selected(self, row):
        if row < 0:
            return
        item = self.report_list.item(row)
        report = item.data(Qt.ItemDataRole.UserRole)
        self._display_report(report)
    
    def _clear_report(self):
        self.personality_text.clear()
        self.subject_text.clear()
        self.career_text.clear()
        self.major_text.clear()
        self.analysis_text.clear()
    
    def _display_report(self, report):
        # 性格特征
        traits = report.personality_traits
        if traits:
            text = ""
            for k, v in traits.items():
                if isinstance(v, list):
                    text += f"{k}: {', '.join(v)}\n"
                else:
                    text += f"{k}: {v}\n"
            self.personality_text.setText(text)
        
        # 选科建议
        subjects = report.subject_recommendations
        if subjects:
            text = ""
            for k, v in subjects.items():
                if isinstance(v, list):
                    text += f"{k}: {', '.join(v)}\n"
                else:
                    text += f"{k}: {v}\n"
            self.subject_text.setText(text)
        
        # 职业推荐
        careers = report.career_recommendations
        if careers:
            text = ""
            for k, v in careers.items():
                if isinstance(v, list):
                    text += f"{k}: {', '.join(v)}\n"
                else:
                    text += f"{k}: {v}\n"
            self.career_text.setText(text)
        
        # 专业推荐
        majors = report.major_recommendations
        if majors:
            text = ""
            for k, v in majors.items():
                if isinstance(v, list):
                    text += f"{k}: {', '.join(v)}\n"
                else:
                    text += f"{k}: {v}\n"
            self.major_text.setText(text)
        
        # 详细分析
        self.analysis_text.setText(report.detailed_analysis)
    
    def _generate_report(self):
        sid = self.student_combo.currentData()
        if not sid:
            QMessageBox.warning(self, "提示", "请先选择学生")
            return
        
        if not self.ai_service.is_available():
            QMessageBox.warning(self, "提示", "请先配置Claude API Key")
            return
        
        # 需要有对话历史才能生成报告
        sessions = self.db.get_all_sessions(sid)
        if not sessions:
            QMessageBox.warning(self, "提示", "请先与该学生进行AI对话")
            return
        
        QMessageBox.information(self, "提示", "报告生成中，请稍候...")
        
        report = self.ai_service.generate_career_report(sid, sessions[0])
        if report:
            self._on_student_changed()
            QMessageBox.information(self, "成功", "职业规划报告已生成！")
        else:
            QMessageBox.warning(self, "失败", "报告生成失败，请重试")
