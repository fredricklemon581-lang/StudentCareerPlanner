# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QIcon

class SidebarItem(QPushButton):
    """iPad风格侧边栏列表项"""
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # 图标
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 18px; color: #333;")
        layout.addWidget(self.icon_label)
        
        # 文本
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("font-size: 15px; font-weight: 500; color: #333;")
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        # 样式
        self.setStyleSheet("""
            SidebarItem {
                background-color: transparent;
                border: none;
                border-radius: 10px;
                text-align: left;
            }
            SidebarItem:hover {
                background-color: rgba(0, 0, 0, 0.05);
            }
            SidebarItem:checked {
                background-color: #007AFF; /* Apple Blue */
            }
        """)

    def setChecked(self, checked):
        super().setChecked(checked)
        color = "white" if checked else "#333"
        self.icon_label.setStyleSheet(f"font-size: 18px; color: {color};")
        self.text_label.setStyleSheet(f"font-size: 15px; font-weight: {'600' if checked else '500'}; color: {color};")


class SidebarDock(QFrame):
    """
    iPadOS风格侧边栏
    - 半透明背景
    - 悬浮列表项
    """
    item_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            SidebarDock {
                background-color: rgba(242, 242, 247, 0.8); /* iOS System Gray 6 */
                border-right: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(8, 0, 0, 20)
        
        # 应用图标/标志
        logo = QLabel("🎓")
        logo.setStyleSheet("font-size: 24px;")
        title_layout.addWidget(logo)
        
        app_title = QLabel("CareerOS")
        app_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1c1c1e;")
        title_layout.addWidget(app_title)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # 导航项列表
        self.items = []
        self.item_data = [
            ("🏠", "今日概览"),
            ("📊", "数据洞察"),
            ("💬", "AI 咨询"),
            ("🎯", "生涯规划"),
            ("📚", "智能组卷"),
            ("👥", "学生档案"),
            ("⚙️", "设置")
        ]
        
        for i, (icon, text) in enumerate(self.item_data):
            btn = SidebarItem(icon, text)
            btn.clicked.connect(lambda checked, idx=i: self._on_item_clicked(idx))
            self.items.append(btn)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # 选中第一项
        if self.items:
            self.items[0].setChecked(True)

    def _on_item_clicked(self, index):
        for i, btn in enumerate(self.items):
            btn.setChecked(i == index)
        self.item_clicked.emit(index)
