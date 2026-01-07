# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QFrame, QGraphicsDropShadowEffect, QApplication)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QColor, QFont, QIcon

class TrafficLight(QPushButton):
    """iOS窗口控制按钮"""
    def __init__(self, color, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

class ModernWindow(QMainWindow):
    """
    iOS风格无边框窗口
    - 无缝融合的标题栏
    - 阴影效果
    - 拖拽移动
    """
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(1200, 800)
        
        # 主容器（带圆角和阴影）
        self.container = QFrame(self)
        self.container.setObjectName("Container")
        self.container.setStyleSheet("""
            #Container {
                background-color: #F2F2F7;
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        # 阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 10)
        self.container.setGraphicsEffect(shadow)
        
        # 布局
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 标题栏 (Unified Toolbar)
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(50)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        # 红绿灯控制
        self.btn_close = TrafficLight("#FF5F57", "#E0443E")
        self.btn_min = TrafficLight("#FEBC2E", "#D89E24")
        self.btn_max = TrafficLight("#28C840", "#1AAB29")
        
        self.btn_close.clicked.connect(self.close)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max)
        
        title_layout.addWidget(self.btn_close)
        title_layout.addSpacing(8)
        title_layout.addWidget(self.btn_min)
        title_layout.addSpacing(8)
        title_layout.addWidget(self.btn_max)
        
        # 统一工具栏区域 (Unified Toolbar)
        title_layout.addSpacing(20)
        
        # 搜索栏
        from PyQt6.QtWidgets import QLineEdit
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 搜索")
        self.search_bar.setFixedWidth(200)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(118, 118, 128, 0.12);
                border: none;
                border-radius: 9px;
                padding: 4px 8px;
                font-size: 13px;
                color: #333;
            }
            QLineEdit:focus {
                background-color: white;
                border: 1px solid #007AFF;
            }
        """)
        title_layout.addWidget(self.search_bar)
        
        title_layout.addStretch()
        
        # 右侧工具按钮容器
        self.toolbar_actions = QHBoxLayout()
        self.toolbar_actions.setSpacing(10)
        title_layout.addLayout(self.toolbar_actions)
        
        layout.addWidget(self.title_bar)
        
        # 内容区域
        self.content_area = QWidget()
        layout.addWidget(self.content_area)
        
        # 设置中心部件 (注意：QMainWindow需要setCentralWidget，但这里我们用custom container)
        super().setCentralWidget(self.container)
        
        # 拖拽状态
        self.old_pos = None

    def resizeEvent(self, event):
        # 确保container填满窗口（留出阴影边距）
        m = 20 # margin for shadow
        self.container.setGeometry(m, m, self.width()-2*m, self.height()-2*m)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 只有点击标题栏才能拖动
            if event.position().y() < 70: # 稍微宽容一点的区域
                self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        
    def toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
