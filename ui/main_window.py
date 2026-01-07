"""
智慧学业规划系统 - 主窗口
现代化设计 + 功能强大
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QPainter

from database.db_manager import DatabaseManager
from services.analysis_service import AnalysisService
from services.ai_service import AIService
from services.goal_management_service import GoalManagementService
from services.learning_behavior_service import LearningBehaviorService
from services.emotion_tracking_service import EmotionTrackingService
from ui.teacher_tools_view import TeacherToolsView
import config


class GradientWidget(QWidget):
    """渐变背景组件 - Apple风格"""
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        # Apple风格的深蓝渐变
        gradient.setColorAt(0, QColor("#1C1C1E"))
        gradient.setColorAt(0.5, QColor("#2C2C2E"))
        gradient.setColorAt(1, QColor("#1C1C1E"))
        painter.fillRect(self.rect(), gradient)


class NavButton(QPushButton):
    """导航按钮 - Apple风格胶囊设计"""
    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}  {text}")
        self.setCheckable(True)
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 10px;
                color: rgba(255,255,255,0.6);
                font-family: "SF Pro Display", "PingFang SC", "Microsoft YaHei";
                font-size: 14px;
                font-weight: 500;
                text-align: left;
                padding: 10px 14px;
                margin: 1px 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255,255,255,0.08),
                    stop:1 rgba(255,255,255,0.03));
                color: rgba(255,255,255,0.9);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0A84FF, stop:1 #007AFF);
                color: white;
                font-weight: 600;
            }
            QPushButton:pressed {
                background: rgba(0,122,255,0.85);
            }
        """)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.setMinimumSize(1400, 900)
        
        # 初始化服务
        self.db = DatabaseManager(config.DATABASE_PATH)
        self.analysis_service = AnalysisService(self.db)
        self.ai_service = AIService(self.db, self.analysis_service)
        self.goal_service = GoalManagementService(self.db)
        self.learning_behavior_service = LearningBehaviorService(self.db)
        self.emotion_service = EmotionTrackingService(self.db)
        
        self._init_ui()
        self._apply_theme()
    
    def _init_ui(self):
        """初始化UI"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ========== 侧边栏 ==========
        sidebar = GradientWidget()
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(8)
        
        # Logo区域
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 20)
        
        logo_icon = QLabel("🎓")
        logo_icon.setFont(QFont("Segoe UI Emoji", 36))
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_icon.setStyleSheet("color: white;")
        logo_layout.addWidget(logo_icon)
        
        logo_text = QLabel("智慧学业规划")
        logo_text.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setStyleSheet("color: white;")
        logo_layout.addWidget(logo_text)
        
        version_text = QLabel(f"v{config.APP_VERSION}")
        version_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_text.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 11px;")
        logo_layout.addWidget(version_text)
        
        sidebar_layout.addWidget(logo_widget)
        
        # 分隔线
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.15);")
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(20)
        
        # ═══ 新架构：4个核心区域 ═══
        self.nav_buttons = []
        
        # 区域1: 核心
        section1 = QLabel("  核心")
        section1.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 600; padding-left: 8px;")
        sidebar_layout.addWidget(section1)
        
        nav_core = [
            ("🏠", "今日概览", 0),      # Today - 智能摘要
            ("📊", "数据洞察", 1),      # Insight - 分析+趋势
        ]
        
        for icon, text, idx in nav_core:
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(16)
        
        # 区域2: 探索
        section2 = QLabel("  探索")
        section2.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 600; padding-left: 8px;")
        sidebar_layout.addWidget(section2)
        
        nav_journey = [
            ("💬", "AI对话", 2),        # 职业探索对话
            ("🎯", "生涯规划", 3),      # 报告+目标
        ]
        
        for icon, text, idx in nav_journey:
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addSpacing(16)
        
        # 区域3: 工具
        section3 = QLabel("  工具")
        section3.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px; font-weight: 600; padding-left: 8px;")
        sidebar_layout.addWidget(section3)
        
        nav_tools = [
            ("🎓", "智能组卷", 4),      # 教师工具
            ("👥", "学生管理", 5),      # 管理+录入
            ("💚", "情绪健康", 6),      # 情绪追踪
        ]
        
        for icon, text, idx in nav_tools:
            btn = NavButton(icon, text)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        self.nav_buttons[0].setChecked(True)
        
        sidebar_layout.addStretch()
        
        # 底部信息
        footer = QLabel("© 2024 智慧教育")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 11px;")
        sidebar_layout.addWidget(footer)
        
        main_layout.addWidget(sidebar)
        
        # ========== 内容区域 ==========
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f7fa;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 页面堆栈
        self.stack = QStackedWidget()
        
        # 导入视图
        from ui.dashboard_view import DashboardView
        from ui.student_view import StudentView
        from ui.score_view import ScoreView
        from ui.analysis_view import AnalysisView
        from ui.chat_view import ChatView
        from ui.career_view import CareerView
        from ui.goal_tracking_view import GoalTrackingView
        from ui.emotion_tracking_view import EmotionTrackingView
        
        # ═══ 按新架构顺序初始化 ═══
        # 0: 今日概览 (Dashboard)
        self.dashboard_view = DashboardView(self.db, self.analysis_service)
        # 1: 数据洞察 (Analysis)
        self.analysis_view = AnalysisView(self.db, self.analysis_service)
        # 2: AI对话 (Chat)
        self.chat_view = ChatView(self.db, self.ai_service)
        # 3: 生涯规划 (Career + Goal)
        self.career_view = CareerView(self.db, self.ai_service)
        # 4: 智能组卷 (Teacher Tools)
        self.teacher_tools_view = TeacherToolsView(self.db)
        # 5: 学生管理 (Student + Score)
        self.student_view = StudentView(self.db)
        # 6: 情绪健康 (Emotion)
        self.emotion_view = EmotionTrackingView(self.db, self.emotion_service)
        
        # 按新顺序添加到堆栈
        self.stack.addWidget(self.dashboard_view)     # 0
        self.stack.addWidget(self.analysis_view)      # 1
        self.stack.addWidget(self.chat_view)          # 2
        self.stack.addWidget(self.career_view)        # 3
        self.stack.addWidget(self.teacher_tools_view) # 4
        self.stack.addWidget(self.student_view)       # 5
        self.stack.addWidget(self.emotion_view)       # 6
        
        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)
    
    def _apply_theme(self):
        """应用主题 - Apple Human Interface Guidelines"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F2F2F7;
            }
            
            /* 滚动条 - Apple风格 */
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,0,0,0.15);
                border-radius: 4px;
                min-height: 40px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0,0,0,0.25);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            /* 分组框 */
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #E5E5EA;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                color: #3c3c43;
            }
            
            /* 下拉框 */
            QComboBox {
                background: white;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 36px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #007AFF;
            }
            QComboBox:focus {
                border: 2px solid #007AFF;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            
            /* 输入框 */
            QLineEdit, QTextEdit {
                background: white;
                border: 1px solid #E5E5EA;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                selection-background-color: #007AFF;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #007AFF;
            }
            
            /* 表格 */
            QTableWidget {
                background: white;
                border: 1px solid #E5E5EA;
                border-radius: 12px;
                gridline-color: #F2F2F7;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F2F2F7;
            }
            QTableWidget::item:selected {
                background: #007AFF;
                color: white;
            }
            QHeaderView::section {
                background: #F9F9FB;
                color: #3c3c43;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid #E5E5EA;
                font-weight: 600;
                font-size: 12px;
            }
            
            /* 标签页 */
            QTabWidget::pane {
                border: 1px solid #E5E5EA;
                border-radius: 12px;
                background: white;
            }
            QTabBar::tab {
                background: #F2F2F7;
                border: 1px solid #E5E5EA;
                border-bottom: none;
                padding: 10px 20px;
                border-radius: 8px 8px 0 0;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: 600;
            }
            
            /* 按钮通用 */
            QPushButton {
                font-size: 14px;
            }
            
            /* 标签 */
            QLabel {
                color: #3c3c43;
            }
        """)
    
    def _switch_page(self, index: int):
        """切换页面"""
        # 更新按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        
        # 刷新页面数据
        widget = self.stack.widget(index)
        if hasattr(widget, 'refresh'):
            widget.refresh()
        
        self.stack.setCurrentIndex(index)


def run_app():
    """运行应用"""
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
