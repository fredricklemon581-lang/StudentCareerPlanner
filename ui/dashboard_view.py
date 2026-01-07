"""
数据总览仪表盘
展示关键统计数据和快捷操作
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DatabaseManager
from services.analysis_service import AnalysisService


class StatCard(QFrame):
    """统计卡片 - 支持动态更新"""
    def __init__(self, icon: str, title: str, value: str, subtitle: str = "", color: str = "#667eea"):
        super().__init__()
        self.color = color
        self._value_label = None  # 保存引用以便动态更新
        
        self.setFixedHeight(140)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 16px;
                border: none;
            }}
        """)
        
        # 添加阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setFixedWidth(70)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background: {color}20;
            border-radius: 12px;
            padding: 10px;
        """)
        layout.addWidget(icon_label)
        
        # 文字
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #718096; font-size: 13px;")
        text_layout.addWidget(title_label)
        
        self._value_label = QLabel(value)
        self._value_label.setFont(QFont("Microsoft YaHei", 28, QFont.Weight.Bold))
        self._value_label.setStyleSheet(f"color: {color};")
        text_layout.addWidget(self._value_label)
        
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet("color: #a0aec0; font-size: 12px;")
            text_layout.addWidget(sub_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
    
    def update_value(self, new_value: str):
        """更新显示的数值"""
        if self._value_label:
            self._value_label.setText(new_value)


class QuickActionCard(QFrame):
    """快捷操作卡片"""
    def __init__(self, icon: str, title: str, description: str, on_click=None):
        super().__init__()
        self.setFixedHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.on_click = on_click
        
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 2px solid transparent;
            }
            QFrame:hover {
                border: 2px solid #667eea;
                background: #f8f9ff;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 20))
        self.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setFixedWidth(50)
        layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2d3748;")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #718096; font-size: 12px;")
        text_layout.addWidget(desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        arrow = QLabel("→")
        arrow.setStyleSheet("color: #667eea; font-size: 18px;")
        layout.addWidget(arrow)
    
    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click()


class DashboardView(QWidget):
    """仪表盘视图"""
    
    def __init__(self, db: DatabaseManager, analysis: AnalysisService):
        super().__init__()
        self.db = db
        self.analysis = analysis
        self._init_ui()
    
    def _init_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # 欢迎标题
        header = QHBoxLayout()
        
        welcome_layout = QVBoxLayout()
        title = QLabel("欢迎使用智慧学业规划系统")
        title.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        welcome_layout.addWidget(title)
        
        subtitle = QLabel("AI驱动的学业分析与职业规划平台")
        subtitle.setStyleSheet("color: #718096; font-size: 14px;")
        welcome_layout.addWidget(subtitle)
        
        header.addLayout(welcome_layout)
        header.addStretch()
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新数据")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #5a67d8;
            }
        """)
        refresh_btn.clicked.connect(self.refresh)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # 统计卡片
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        self.card_students = StatCard("👨‍🎓", "学生总数", "0", "已注册学生", "#007AFF")  # Apple Blue
        self.card_exams = StatCard("📝", "考试场次", "0", "已录入试卷", "#34C759")      # Apple Green
        self.card_scores = StatCard("📊", "成绩记录", "0", "答题记录", "#FF9500")       # Apple Orange
        self.card_reports = StatCard("🎯", "规划报告", "0", "已生成报告", "#FF3B30")    # Apple Red
        
        stats_layout.addWidget(self.card_students, 0, 0)
        stats_layout.addWidget(self.card_exams, 0, 1)
        stats_layout.addWidget(self.card_scores, 0, 2)
        stats_layout.addWidget(self.card_reports, 0, 3)
        
        layout.addLayout(stats_layout)
        
        # 快捷操作区
        actions_title = QLabel("⚡ 快捷操作")
        actions_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        actions_title.setStyleSheet("color: #2d3748; margin-top: 10px;")
        layout.addWidget(actions_title)
        
        actions_layout = QGridLayout()
        actions_layout.setSpacing(15)
        
        actions = [
            ("📥", "导入学生数据", "从Excel批量导入学生信息"),
            ("📊", "录入成绩", "录入或导入学生考试成绩"),
            ("🤖", "AI咨询", "开始一对一AI职业规划对话"),
            ("📈", "查看分析", "查看学生成绩分析报告"),
        ]
        
        for i, (icon, title, desc) in enumerate(actions):
            card = QuickActionCard(icon, title, desc)
            actions_layout.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(actions_layout)
        
        # AI状态
        self.ai_status = QFrame()
        self.ai_status.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #007AFF, stop:1 #5856D6);
                border-radius: 16px;
                padding: 20px;
            }
        """)
        ai_layout = QHBoxLayout(self.ai_status)
        
        ai_icon = QLabel("🤖")
        ai_icon.setFont(QFont("Segoe UI Emoji", 28))
        ai_layout.addWidget(ai_icon)
        
        ai_text = QVBoxLayout()
        ai_title = QLabel("AI 智能助手已就绪")
        ai_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        ai_title.setStyleSheet("color: #FFD700;")  # 金色，更醒目
        ai_text.addWidget(ai_title)
        
        ai_desc = QLabel("智能职业规划顾问 • 帮助学生发现自我、规划未来")
        ai_desc.setStyleSheet("color: #E0E7FF; font-size: 13px; font-weight: 500;")  # 浅靛蓝色
        ai_text.addWidget(ai_desc)
        
        ai_layout.addLayout(ai_text)
        ai_layout.addStretch()
        
        layout.addWidget(self.ai_status)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def refresh(self):
        """刷新数据 - 从数据库获取真实统计"""
        stats = self.db.get_statistics()
        
        # 获取规划报告数量
        report_count = self._get_report_count()
        
        # 更新各统计卡片
        self.card_students.update_value(str(stats.get('students', 0)))
        self.card_exams.update_value(str(stats.get('exams', 0)))
        self.card_scores.update_value(str(stats.get('scores', 0)))
        self.card_reports.update_value(str(report_count))
    
    def _get_report_count(self) -> int:
        """获取规划报告总数"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) as count FROM career_reports')
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Exception:
            return 0

