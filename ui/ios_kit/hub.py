# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QFrame
from PyQt6.QtCore import Qt, QSize
from .window import ModernWindow # for types if needed
from .motion import InteractiveMixin

class SmartWidget(InteractiveMixin, QFrame):
    """
    iOS风格桌面小组件
    """
    def __init__(self, title, content, size="medium", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            SmartWidget {
                background-color: white;
                border-radius: 20px;
                border: 1px solid rgba(0,0,0,0.05);
            }
        """)
        
        self.setup_interactions() # Initialize mixin
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #8E8E93;")
        layout.addWidget(t_lbl)
        
        # Content
        c_lbl = QLabel(content)
        c_lbl.setWordWrap(True)
        c_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        c_lbl.setStyleSheet("font-size: 24px; font-weight: 500; color: #1C1C1E; margin-top: 10px;")
        layout.addWidget(c_lbl)
        layout.addStretch()
        
        # Size logic
        if size == "small":
            self.setFixedSize(160, 160)
        elif size == "medium":
            self.setFixedSize(340, 160)
        elif size == "large":
            self.setFixedSize(340, 340)

class HubView(QWidget):
    """
    仪表盘 (iPadOS Home Screen style)
    包含大标题和网格小组件
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        # Scroll Content
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(20)
        
        # Large Title
        self.date_label = QLabel("1月7日 星期二")
        self.date_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #8E8E93; text-transform: uppercase;")
        self.content_layout.addWidget(self.date_label)
        
        self.title_label = QLabel("早上好")
        self.title_label.setStyleSheet("font-size: 34px; font-weight: 700; color: #1C1C1E;")
        self.content_layout.addWidget(self.title_label)
        
        self.content_layout.addSpacing(20)
        
        # Grid for Widgets
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Add Widgets
        w1 = SmartWidget("今日摘要", "您有 3 个待办任务\n2 门课程即将考试", "medium")
        grid.addWidget(w1, 0, 0, 1, 2)
        
        w2 = SmartWidget("情绪指数", "😊 快乐\n保持良好的心态", "small")
        grid.addWidget(w2, 0, 2)
        
        w3 = SmartWidget("最近对话", "AI: 建议重点复习数学...", "medium")
        grid.addWidget(w3, 1, 0, 1, 2)
        
        # w4 = SmartWidget("学习时长", "4h 20m\n比昨日 +15%", "small")
        # grid.addWidget(w4, 1, 2)
        
        self.content_layout.addLayout(grid)
        self.content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
